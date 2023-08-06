#!/usr/bin/python

import smtplib
from email.mime.text import MIMEText
import os
import logging
import sys


class TextLogger(object):
    def __init__(self):
        logging.info("Getting Text-Logger environment variables")
        self.sender = os.environ.get('TEXT_LOGGER_SENDER')
        self.receiver = os.environ.get('TEXT_LOGGER_RECEIVER')
        self.sender_pass = os.environ.get('TEXT_LOGGER_PASS')
        if not self.sender or not self.receiver or not self.sender_pass:
            raise KeyError("Text-Logger environment variables not set")
        logging.info("Text-Logger Sender: %s" % self.sender)
        logging.info("Text-Logger Receiver: %s" % self.receiver)

    def send_message(self,msg_text):
        msg = MIMEText(msg_text)
        msg['Subject'] = "Text-Logger Notifications"
        msg['From'] = "Text-Logger"
        msg['To'] = self.receiver

        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.sender,self.sender_pass)
        server.sendmail(self.sender,self.receiver,msg_text)
        server.close()

if __name__ == "__main__":
    msg_handler = TextLogger()
    msg_handler.send_message(sys.argv[1])