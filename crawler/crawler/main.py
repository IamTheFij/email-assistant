from datetime import datetime
from datetime import timedelta
from time import sleep
from imaplib import IMAP4
import os

from dateutil import parser
from dateutil.tz import tzutc
from imbox import Imbox
import requests


VALID_CONTENT_TYPES = ['text/plain', 'text/html']


def get_message_subject(message):
    """Returns message subject or a placeholder text"""
    return getattr(message, 'subject', 'NO SUBJECT')


class MailCrawler(object):
    parser_hosts = None
    indexer_host = os.environ['INDEXER']

    def __init__(self):
        self.imap_url = os.environ['IMAP_URL']
        self.imap_user = os.environ['IMAP_USER']
        self.imap_pass = os.environ['IMAP_PASS']

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
                'subject': message.subject,
            })
            print('Parsed result: ', result)
            print('Indexed result: ', self.index_token(result))

    def process_messages(self, server, since_date, last_message=0):
        for uid, message in server.messages(date__gt=since_date):
            uid = int(uid)
            if uid <= last_message:
                print(
                    'DDB Already seen message with uid {}. Skipping'.format(uid)
                )
                continue

            print(
                'Processing message uid {} message_id {} '
                'with subject "{}"'.format(
                    uid,
                    message.message_id,
                    get_message_subject(message),
                )
            )
            self.process_message(message)

            # Update since_date
            message_date = parser.parse(message.date)
            print('DDB Processed message. Message date: {} Old date: {}'.format(
                message_date, since_date
            ))
            try:
                since_date = max(since_date, message_date)
            except TypeError:
                print("Error comparing dates. We'll just use the last one")
            print('DDB Since date is now ', since_date)
            last_message = max(uid, last_message)

        return since_date, last_message

    def run(self):
        print('Starting crawler')
        # TODO: Put server into some kind of context manager and property
        with self.get_server() as server:
            # TODO: parameterize startup date, maybe relative
            since_date = datetime.now(tzutc()) - timedelta(days=15)
            last_message = 0
            while True:
                print('Lets process')
                since_date, last_message = self.process_messages(
                    server,
                    since_date,
                    last_message=last_message
                )
                print('DDB Processed all. New since_date', since_date)
                # TODO: parameterize sleep
                # Sleep for 10 min
                sleep(10 * 60)


if __name__ == '__main__':
    while True:
        try:
            MailCrawler().run()
        except IMAP4.abort:
            print('Imap abort. We will try to reconnect')
            pass
