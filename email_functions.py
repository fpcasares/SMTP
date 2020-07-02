# Imports

import smtplib
import imaplib
import configparser
import os
from getpass import getpass
from email.mime.text import MIMEText

#Vars
IMAP_SERVER='imap.gmail.com'
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

#Functions
def open_connection(username,password,verbose=False):

    # Connect to the server
    connection = imaplib.IMAP4_SSL(IMAP_SERVER)

    # Login to our account
    try:
        connection.login(username, password)
    except Exception as err:
        print('ERROR:', err)
    return (connection)

def send_email(username,password,to,subject,content,verbose=False):
    msg = MIMEText(content,'plain')
    msg['Subject'] = subject
    msg['From'] = username+'@gmail.com'
    msg['To'] = to
   
    connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    connection.set_debuglevel(verbose)
    connection.starttls()
    connection.login(username, password)
   
    #msg._payload = msg._payload.decode('unicode_escape').encode('utf-8')
    connection.sendmail(msg['From'], msg['To'], msg.as_string())

    connection.quit()


def search_email_by_criteria(username,password,mailbox='INBOX',criteria='SUBJECT "Codigo 12345"'):
    with open_connection(username,password) as c:
        typ, mbox_data = c.list()
        c.select('{}'.format(mailbox), readonly=True)
        typ, [msg_ids] = c.search(None, '({})'.format(criteria))
        return(msg_ids)


def process_message(username,password,msg_ids,process='Read',mailbox='INBOX'):
    with open_connection(username,password) as c:
        # Check if process mailbox exists
        if c.select('PROCESSED')[0]=='NO':
            typ, create_response = c.create('PROCESSED')
            print(create_response)
        c.select('{}'.format(mailbox), readonly=False)
        # What are the current flags?
        typ, response = c.fetch(msg_ids, '(FLAGS)')
        print('Flags before:', response)
        if process=='Read':
            typ, response = c.store(msg_ids, '+FLAGS', r'(\Seen)')
            print(c.copy(msg_ids, 'PROCESSED'))
        typ, response = c.store(msg_ids, '+FLAGS', r'(\Deleted)')
        # What are the flags now?
        typ, response = c.fetch(msg_ids, '(FLAGS)')
        print('Flags after:', response)
        # Really delete the message.
        typ, response = c.expunge()
        print('Expunged:', response)



if __name__ == '__main__':
    username=input('Input your gmail username\n')
    password=getpass('Input your password\n')
    msg_ids = search_email_by_criteria(username,password,'INBOX','SUBJECT "This is a test Subject"')
    msg_ids = ','.join(msg_ids.decode('utf-8').split(' '))
    print(msg_ids)
    if msg_ids!='':
        process_message(msg_ids)
    send_email(username,password,'fpcasares@gmail.com','Test Subject','Test content\n')
