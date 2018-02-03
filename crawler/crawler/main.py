from getpass import getpass
from datetime import date
from ipdb import set_trace
import email

from imapclient import IMAPClient


class MailCrawler(object):
    server_url = 'my.iamthefij.com'
    valid_content_types = [ 'text/plain', 'text/html' ]

    def get_credentials(self):
        password = getpass('Password?')
        return ('iamthefij@iamthefij.com', password)

    def get_server(self):
        server = IMAPClient(self.server_url, use_uid=True)
        server.login(*self.get_credentials())
        return server

    def is_valid_content_type(self, message):
        return message.get_content_type() in self.valid_content_types

    def get_email_text(self, message):
        if not message.is_multipart():
            if self.is_valid_content_type(message):
                return message.get_payload(decode=True)
        else:
            content_type_to_payload = {
                payload.get_content_type(): self.get_email_text(payload)
                for payload in message.get_payload()
            }
            for content_type in self.valid_content_types:
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
            set_trace()
            print(self.get_email_text(email_message))


if __name__ == '__main__':
    MailCrawler().run()
