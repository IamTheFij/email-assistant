import logging
import os
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta
from imaplib import IMAP4
from time import sleep

import requests
from dateutil import parser
from dateutil.tz import tzutc
from imbox import Imbox


logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logging.getLogger(__name__).addHandler(logging.NullHandler())


VALID_CONTENT_TYPES = ['text/plain', 'text/html']


def get_message_subject(message):
    """Returns message subject or a placeholder text"""
    return getattr(message, 'subject', 'NO SUBJECT')


class MailCrawler(object):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.imap_url = os.environ['IMAP_URL']
        self.imap_user = os.environ['IMAP_USER']
        self.imap_pass = os.environ['IMAP_PASS']
        self.parser_hosts = None
        self.indexer_host = os.environ.get('INDEXER')
        self.debug_mode = os.environ.get('DEBUG', False)

    def get_parsers(self):
        """Retrieves a list of parser hosts"""
        if self.parser_hosts is None:
            self.parser_hosts = []
            parser_format = 'PARSER_{}'
            parser_index = 1
            parser_host = os.environ.get(parser_format.format(parser_index))
            while parser_host is not None:
                self.parser_hosts.append(parser_host)
                parser_index += 1
                parser_host = os.environ.get(parser_format.format(parser_index))

        return self.parser_hosts

    def parse_message(self, message):
        """Parses tokens from an email message"""
        text = self.get_email_text(message)
        if not text:
            print('No email text returned')
            return []

        results = []
        for parser_host in self.get_parsers():
            # print('Parsing email text... ', text)
            response = requests.post(
                parser_host+'/parse',
                json={
                    'subject': get_message_subject(message),
                    'message': text,
                },
            )
            response.raise_for_status()
            print('Got response', response.text)
            results += response.json()
        return results

    def get_server(self):
        """Returns an active IMAP server"""
        return Imbox(
            self.imap_url,
            username=self.imap_user,
            password=self.imap_pass,
            ssl=True,
        )

    def get_email_text(self, message):
        """Retrieves the text body of an email message"""
        body = message.body.get('plain') or message.body.get('html')
        if not body:
            return None
        # Concat all known body content together since it doesn't really matter
        return ''.join([text for text in body if isinstance(text, str)])

    def index_token(self, message):
        """Sends a token from the parser to the indexer"""
        if self.indexer_host is None and self.debug_mode:
            print("DDB No indexer host, but OK for debugging")
        response = requests.post(
            self.indexer_host+'/token',
            json=message,
        )
        response.raise_for_status()
        return response.json()

    def process_message(self, message):
        """Process a single email message"""
        for result in self.parse_message(message):
            result.update({
                "subject": message.subject,
            })
            print("Parsed result: ", result)
            print("Indexed result: ", self.index_token(result))

    def process_messages(self, server, since_date, last_uid=0):
        kwargs = {}
        if last_uid > 0:
            kwargs["uid__range"] = "{}:*".format(last_uid)
        else:
            kwargs["date__gt"] = since_date
        self._logger.info("Mailbox search kwargs %s", kwargs)
        for uid, message in server.messages(**kwargs):
            uid = int(uid)
            if uid <= last_uid:
                self._logger.debug(
                    "DDB Already seen message with uid {}. Skipping".format(uid)
                )
                continue

            self._logger.info(
                "Processing message uid %s message_id %s with subject '%s'",
                uid,
                message.message_id,
                get_message_subject(message),
            )
            self.process_message(message)

            # Update since_date
            message_date = parser.parse(message.date)
            self._logger.debug(
                "DDB Processed message. Message date: %s Old date: %s",
                message_date, since_date
            )
            try:
                since_date = max(since_date, message_date)
            except TypeError:
                self._logger.error(
                    "Error comparing dates. We'll just use the last one"
                )
            self._logger.debug("DDB Since date is now %s", since_date)
            last_uid = max(uid, last_uid)

        return since_date, last_uid

    def _parse_args(self, args=None):
        """Parses command line arguments and returns them"""
        parser = ArgumentParser(description="Inbox crawler")
        parser.add_argument(
            "--sleep", "-s",
            default=10*60,
            help=("Number of seconds to wait between polling IMAP server."
                  "Default 10 min"),
        )
        parser.add_argument(
            "--verbosity", "-v",
            action="count",
            help=("Adjust log verbosity by increasing arg count. Default log",
                  "level is ERROR. Level increases with each `v`"),
        )
        return parser.parse_args(args)

    def _set_log_level(self, verbosity):
        """Sets the log level for the class using the provided verbosity count"""
        if verbosity == 1:
            # Set this logger to info
            self._logger.setLevel(logging.INFO)
        elif verbosity == 2:
            # Set this logger to debug and root to info
            logging.getLogger().setLevel(logging.INFO)
            self._logger.setLevel(logging.DEBUG)
        elif verbosity >= 3:
            # Set the root logger to debug
            logging.getLogger().setLevel(logging.DEBUG)

    def run(self, args=None):
        args = self._parse_args(args=args)
        if args.verbosity:
            self._set_log_level(args.verbosity)

        self._logger.info('Starting crawler')
        with self.get_server() as server:
            # TODO: parameterize startup date, maybe relative
            since_date = datetime.now(tzutc()) - timedelta(days=16)
            last_uid = 0
            while True:
                print("Processing messages")
                since_date, last_uid = self.process_messages(
                    server,
                    since_date,
                    last_uid=last_uid
                )
                self._logger.info(
                    "DDB Processed all. New since_date %s",
                    since_date,
                )
                sleep(args.sleep)


if __name__ == '__main__':
    while True:
        try:
            MailCrawler().run()
        except IMAP4.abort:
            print('Imap abort. We will try to reconnect')
            pass
