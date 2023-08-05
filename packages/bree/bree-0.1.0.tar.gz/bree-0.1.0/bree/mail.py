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
    def __init__(self, subject, template_file, settings, **kwargs):
        mail_config = settings.get('smtp')

        self.server = mail_config.get('host')
        self.port = mail_config.get('port', 25)
        self.mail_from = mail_config.get('mail_from')
        self.user = mail_config.get('user', None)
        self.password = mail_config.get('password', None)
        # self.timeout = mail_config.get('timeout', None)


        self.subject = subject

        self.debug = settings.get('debug', False)

        self.template_root = settings.get('template_path')

        self.template = Loader(self.template_root).load(template_file)

        self.mime_text = settings.get('mime_text', 'html')
        self.charset = settings.get('charset', 'utf-8')

        pass


    def send(self, mail_to, **kwargs):
        content = self.template.generate(**kwargs)
        msg = MIMEText(content, self.mime_text, self.charset)
        msg['Subject'] = self.subject
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



