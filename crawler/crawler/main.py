from datetime import date
from datetime import datetime
from datetime import timedelta
from getpass import getpass
import email
import json
import os

from imbox import Imbox
import requests


VALID_CONTENT_TYPES = [ 'text/plain', 'text/html' ]


class MailCrawler(object):
    parser_hosts = None
    indexer_host = os.environ['INDEXER']

    def __init__(self):
        self.imap_url = os.environ['IMAP_URL']
        self.imap_user = os.environ['IMAP_USER']
        self.imap_pass = os.environ['IMAP_PASS']

    def get_parsers(self):
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
                    'subject': message.subject,
                    'message': text,
                },
            )
            response.raise_for_status()
            print('Got response', response.text)
            results += response.json()
        return results

    def get_server(self):
        return Imbox(
            self.imap_url,
            username=self.imap_user,
            password=self.imap_pass,
            ssl=True,
        )

    def get_email_text(self, message):
        body = message.body.get('plain') or message.body.get('html')
        if not body:
            return None
        # Concat all known body content together since it doesn't really matter
        return ''.join([text for text in body if isinstance(text, str)])

    def index_message(self, message):
        response = requests.post(
            self.indexer_host+'/token',
            json=message,
        )
        response.raise_for_status()
        return response.json()

    def run(self):
        print('Starting crawler')

        with self.get_server() as server:
            since_date = datetime.now() - timedelta(days=30)
            for uid, message in server.messages(date__gt=since_date):
                print(
                    'Processing message uid {} message_id {} '
                    'with subject "{}"'.format(
                        uid, message.message_id, message.subject
                    )
                )
                for result in self.parse_message(message):
                    result.update({
                        'subject': message.subject,
                    })
                    print('Parsed result: ', result)
                    print('Indexed result: ', self.index_message(result))


if __name__ == '__main__':
    MailCrawler().run()
