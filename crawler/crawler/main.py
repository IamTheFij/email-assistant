from getpass import getpass
from datetime import date
import json
import email
import os

from imapclient import IMAPClient
import requests


VALID_CONTENT_TYPES = [ 'text/plain', 'text/html' ]


class MailCrawler(object):
    parser_hosts = None
    indexer_host = os.environ["INDEXER"]

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
            return []

        results = []
        for parser_host in self.get_parsers():
            response = requests.post(
                parser_host+'/parse',
                json={'message': text},
            )
            response.raise_for_status()
            results += response.json()
        return results

    def get_server(self):
        server = IMAPClient(self.imap_url, use_uid=True)
        server.login(self.imap_user, self.imap_pass)
        return server

    def is_valid_content_type(self, message):
        return message.get_content_type() in VALID_CONTENT_TYPES

    def get_email_text(self, message):
        if not message.is_multipart():
            if self.is_valid_content_type(message):
                # TODO: Check encoding (maybe CHARSET)
                return message.get_payload(decode=True).decode("utf-8")
        else:
            content_type_to_payload = {
                payload.get_content_type(): self.get_email_text(payload)
                for payload in message.get_payload()
            }
            for content_type in VALID_CONTENT_TYPES:
                text = content_type_to_payload.get(content_type)
                if text:
                    return text
        return None

    def index_message(self, message):
        response = requests.post(
            self.indexer_host+'/token',
            json=message,
        )
        response.raise_for_status()
        return response.json()

    def run(self):
        server = self.get_server()
        server.select_folder('INBOX')
        message_ids = server.search(['SINCE', date(2018, 1, 31)])
        for msgid, data in server.fetch(message_ids, 'RFC822').items():
            email_message = email.message_from_bytes(data[b'RFC822'])
            for result in self.parse_message(email_message):
                result.update({
                    'subject': email_message['SUBJECT'],
                })
                print("Parsed result: ", result)
                print("Indexed result: ", self.index_message(result))


if __name__ == '__main__':
    MailCrawler().run()
