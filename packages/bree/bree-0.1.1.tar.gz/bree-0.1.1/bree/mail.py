# -*- coding: utf-8 -*-


from tornado.template import Loader
from email.mime.text import MIMEText
import smtplib


class MailClient(object):
    def __init__(self, mail_config, **kwargs):

        self.mail_from = mail_config.get('mail_from')

        self.server = mail_config.get('host')
        self.port = mail_config.get('port', 25)

        self.user = mail_config.get('user', None)
        self.password = mail_config.get('password', None)

        self.mime_text = mail_config.get('mime_text', 'html')
        self.charset = mail_config.get('charset', 'utf-8')

        self.smtp = smtplib.SMTP()
        self.smtp.connect(self.server, self.port)

        if self.user:
            self.smtp.login(self.user, self.password)

        pass


    def send(self, mail_to, subject, content, mail_from=None, *args, **kwargs):
        """

        :param mail_from:
        :param mail_to:
        :param subject:
        :param content:
        :param args:
        :param kwargs:
        :return:
        """

        if not mail_from:
            mail_from = self.mail_from

        msg = MIMEText(content, self.mime_text, self.charset)
        msg['Subject'] = subject
        msg['From'] = mail_from
        if isinstance(mail_to, str):
            msg['To'] = mail_to
        else:
            msg['To'] = ','.join(mail_to)

        self.smtp.sendmail(mail_from, mail_to, msg.as_string())
        pass

    pass


class MailClient2(object):
    def __init__(self, mail_config, template_file=None, subject=None, template_path=None, debug=False, mime_text='html', charset='utf-8', **kwargs):

        self.server = mail_config.get('host')
        self.port = mail_config.get('port', 25)
        self.mail_from = mail_config.get('mail_from')
        self.user = mail_config.get('user', None)
        self.password = mail_config.get('password', None)
        # self.timeout = mail_config.get('timeout', None)

        self.subject = subject

        self.debug = debug

        self.template_root = template_path

        self.template = Loader(self.template_root).load(template_file) if template_file else None

        self.mime_text = mime_text
        self.charset = charset

        pass


    def send(self, mail_to, content=None, subject=None, **kwargs):

        if not content and self.template:
            content = self.template.generate(**kwargs)

        msg = MIMEText(content, self.mime_text, self.charset)
        msg['Subject'] = subject or self.subject
        msg['From'] = self.mail_from
        if isinstance(mail_to, str):
            msg['To'] = mail_to
        else:
            msg['To'] = ','.join(mail_to)

        smtp = smtplib.SMTP()
        smtp.connect(self.server, self.port)

        if self.user:
            smtp.login(self.user, self.password)

        smtp.sendmail(self.mail_from, mail_to, msg.as_string())

        if self.debug:
            print("Success in sending email to %s" % mail_to)

        smtp.quit()

        pass


# mail client 3

from tornado import iostream
import socket

# Originally from https://gist.github.com/1358253

class Envelope(object):
    def __init__(self, sender, rcpt, body, callback):
        self.sender = sender
        self.rcpt = rcpt[:]
        self.body = body
        self.callback = callback


class AsyncSMTPClient(object):
    CLOSED = -2
    CONNECTED = -1
    IDLE = 0
    EHLO = 1
    MAIL = 2
    RCPT = 3
    DATA = 4
    DATA_DONE = 5
    QUIT = 6

    def __init__(self, host='localhost', port=25):
        self.host = host
        self.port = port
        self.msgs = []
        self.stream = None
        self.state = self.CLOSED

    def send_message(self, msg, callback=None):
        """Message is a django style EmailMessage object"""

        if not msg:
            return

        self.msgs.append(Envelope(msg.from_email, msg.recipients(), msg.message().as_string(), callback))

        self.begin()

    def send(self, sender=None, rcpt=[], body="", callback=None):
        """Very simple sender, just take the necessary parameters to create an envelope"""
        self.msgs.append(Envelope(sender, rcpt, body, callback))

        self.begin()

    def begin(self):
        """Start the sending of a message, if we need a connection open it"""
        if not self.stream:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.stream = iostream.IOStream(s)
            self.stream.connect((self.host, self.port), self.connected)
        else:
            self.work_or_quit(self.process)

    def work_or_quit(self, callback=None):
        """
           callback is provided, for the startup case where we're not in the main processing loop
        """
        if self.state == self.IDLE:
            if self.msgs:
                self.state = self.MAIL
                self.stream.write('MAIL FROM: <%s>\r\n' % self.msgs[0].sender)
            else:
                self.state = self.QUIT
                self.stream.write('QUIT\r\n')
            if callback:
                self.stream.read_until('\r\n', callback)

    def connected(self):
        """Socket connect callback"""
        self.state = self.CONNECTED
        self.stream.read_until('\r\n', self.process)

    def process(self, data):
        # print self.state, data,
        code = int(data[0:3])
        if data[3] not in (' ', '\r', '\n'):
            self.stream.read_until('\r\n', self.process)
            return

        if self.state == self.CONNECTED:
            if not 200 <= code < 300:
                return self.error("Unexpected status %d from CONNECT: %s" % (code, data.strip()))
            self.state = self.EHLO
            self.stream.write('EHLO localhost\r\n')
        elif self.state == self.EHLO:
            if not 200 <= code < 300:
                return self.error("Unexpected status %d from EHLO: %s" % (code, data.strip()))
            self.state = self.IDLE
            self.work_or_quit()
        elif self.state == self.MAIL:
            if not 200 <= code < 300:
                return self.error("Unexpected status %d from MAIL: %s" % (code, data.strip()))
            if self.msgs[0].rcpt:
                self.stream.write('RCPT TO: <%s>\r\n' % self.msgs[0].rcpt.pop(0))
            self.state = self.RCPT
        elif self.state == self.RCPT:
            if not 200 <= code < 300:
                return self.error("Unexpected status %d from RCPT: %s" % (code, data.strip()))
            if self.msgs[0].rcpt:
                self.stream.write('RCPT TO: <%s>\r\n' % self.msgs[0].rcpt.pop(0))
            else:
                self.stream.write('DATA\r\n')
                self.state = self.DATA
        elif self.state == self.DATA:
            if code not in (354,):
                return self.error("Unexpected status %d from DATA: %s" % (code, data.strip()))
            self.stream.write(self.msgs[0].body)
            if self.msgs[0].body[-2:] != '\r\n':
                self.stream.write('\r\n')
            self.stream.write('.\r\n')
            self.state = self.DATA_DONE
        elif self.state == self.DATA_DONE:
            if not 200 <= code < 300:
                return self.error("Unexpected status %d from DATA END: %s" % (code, data.strip()))
            if self.msgs[0].callback:
                self.msgs[0].callback(True)

            self.msgs.pop(0)

            self.state = self.IDLE
            self.work_or_quit()
        elif self.state == self.QUIT:
            if not 200 <= code < 300:
                return self.error("Unexpected status %d from QUIT: %s" % (code, data.strip()))
            self.close()

        if self.stream:
            self.stream.read_until('\r\n', self.process)

    def error(self, msg):
        self.close(msg)

    def close(self, error_msg=None):
        for msg in self.msgs:
            if msg.callback:
                msg.callback(False, error_msg)
        self.stream.close()
        self.stream = None
        self.state = self.CLOSED




