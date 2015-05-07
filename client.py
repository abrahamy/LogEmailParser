import imaplib
import email
import ConfigParser


READ_NETPOSTPAY = '(HEADER Subject "NetPostPay Error (Contact Dev Team)")'
READ_PAYARENA = '(HEADER Subject "PayArena Error (Contact Dev Team)")'


def open_connection():
    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read(['mail.local.conf'])

    # Connect to the server
    hostname = config.get('Server', 'HostName')
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = config.get('Account', 'Username')
    password = config.get('Account', 'Password')
    connection.login(username, password)
    return connection


def read_emails(readfrom):
    imapclient = open_connection()
    messages = []
    try:
        imapclient.select('NAF Application Logs')
        rs, data = imapclient.uid('search', None, readfrom)
        email_uids = data[0].split()

        for email_id in email_uids:
            rs, data = imapclient.uid('fetch', email_id, '(RFC822)')
            raw_email = data[0][1]

            email_message = email.message_from_string(raw_email)
            if not email_message.is_multipart():
                messages.append(email_message.get_payload())

    finally:
        imapclient.logout()
    return messages
