import email
import json
import logging
import os
import sys
from datetime import date, datetime, timedelta
from getpass import getpass
from imaplib import IMAP4
from time import sleep

import requests
from dateutil import parser
from dateutil.tz import tzutc
from imbox import Imbox
from imbox.parser import parse_email

logging.basicConfig()


class MailCrawler(object):
    parser_urls = None
    indexer_url = os.environ['INDEXER_URL']

    def __init__(self):
        self.imap_url = os.environ.get('IMAP_URL')
        self.imap_user = os.environ.get('IMAP_USER')
        self.imap_pass = os.environ.get('IMAP_PASS')
        self.imap_folder = os.environ.get('IMAP_FOLDER', False)

    def get_parsers(self):
        """Retrieves a list of parser hosts"""
        if self.parser_urls is None:
            self.parser_urls = os.environ.get('PARSERS', '').split(',')
        return self.parser_urls

    def parse_message(self, message):
        """Parses tokens from an email message"""
        body = self.get_email_body(message)
        if not body:
            print('No email text returned')
            return []

        results = []
        for parser_url in self.get_parsers():
            # print('Parsing email text... ', text)
            response = requests.post(
                parser_url+'/parse',
                json={
                    'from': message.sent_from,
                    'subject': message.subject,
                    'message': body,
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

    def get_email_body(self, message):
        """Get the body from the message"""
        has_body = message.body.get('html') or message.body.get('plain')
        if not has_body:
            return None
        # Concat all known body content together since it doesn't really matter
        return {
            'html': ''.join([text
                             for text in message.body.get('html')
                             if isinstance(text, str)]),
            'plain': ''.join([text
                              for text in message.body.get('plain')
                              if isinstance(text, str)])
        }

    def index_token(self, message):
        """Sends a token from the parser to the indexer"""
        response = requests.post(
            self.indexer_url+'/token',
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
        for uid, message in server.messages(date__gt=since_date,
                                            folder=self.imap_folder):
            uid = int(uid)
            if uid <= last_message:
                print('DDB Already seen message with uid {}. Skipping'.format(uid))
                continue

            print(
                'Processing message uid {} message_id {} '
                'with subject "{}"'.format(
                    uid, getattr(message, 'message_id', '?'), message.subject
                )
            )
            try:
                self.process_message(message)
            except Exception as e:
                logging.error(
                    'An error occured while processing message %s: %s.',
                    uid, str(e)
                )

            # Update since_date
            message_date = parser.parse(message.date)
            print('DDB Processed message. Message date: {} Old date: {}'.format(
                message_date, since_date
            ))
            if since_date:
                since_date = max(since_date, message_date)
            else:
                since_date = message_date
            print('DDB Since date is now ', since_date)
            last_message = max(uid, last_message)

        return since_date, last_message


    def run_against_imap(self):
        print('Starting crawler')
        # TODO: Put server into some kind of context manager and property
        with self.get_server() as server:
            # TODO: parameterize startup date, maybe relative
            since_date = False  # Start back from origin
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

    def run_against_stdin(self):
        print('Running crawler on stdin')
        message = parse_email(sys.stdin.read())
        self.process_message(message)
        print('Done')

    def run(self):
        if self.imap_url and self.imap_user and self.imap_pass:
            while True:
                try:
                    self.run_against_imap()
                except IMAP4.abort:
                    print('Imap abort. We will try to reconnect')
                    pass
        else:
            self.run_against_stdin()


if __name__ == '__main__':
    MailCrawler().run()
