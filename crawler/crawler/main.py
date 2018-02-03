from getpass import getpass
from datetime import date
import email
import os

from imapclient import IMAPClient


VALID_CONTENT_TYPES = [ 'text/plain', 'text/html' ]


class MailCrawler(object):

    def __init__(self):
        self.imap_url = os.environ['IMAP_URL']
        self.imap_user = os.environ['IMAP_USER']
        self.imap_pass = os.environ['IMAP_PASS']

    def get_server(self):
        server = IMAPClient(self.imap_url, use_uid=True)
        server.login(self.imap_user, self.imap_pass)
        return server

    def is_valid_content_type(self, message):
        return message.get_content_type() in VALID_CONTENT_TYPES

    def get_email_text(self, message):
        if not message.is_multipart():
            if self.is_valid_content_type(message):
                return message.get_payload(decode=True)
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


    def run(self):
        server = self.get_server()
        server.select_folder('INBOX')
        message_ids = server.search(['SINCE', date(2018, 1, 31)])
        for msgid, data in server.fetch(message_ids, 'RFC822').items():
            email_message = email.message_from_bytes(data[b'RFC822'])
            print(self.get_email_text(email_message))


if __name__ == '__main__':
    MailCrawler().run()
