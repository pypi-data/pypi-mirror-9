#!/usr/bin/env python
# -*- coding:utf-8 -*-
from email import Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
"""
send a email using smtp auth server
@returns: true if send success otherwise false
@param 
"""
class MailSender:
    def __init__(self,host='smtp.haodou.com',port=465,username='noreply@haodou.com',password='josh5vosh8'):
        self.mail_host=host
        self.mail_user=username
        self.mail_pass=password
        self.mail_port = port
        try:
            self.s = smtplib.SMTP_SSL()
            self.s.connect(self.mail_host, self.mail_port)
            self.s.login(self.mail_user, self.mail_pass)
        except Exception,e:
            print 'failed to connect mailserver:%s' % str(e)
            exit(1)
            
    def sendmail(self,subject=None,to=None,content=None):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['Content-Type'] = "text/html; charset=utf-8"
        msg['From'] = self.mail_user
        #msg['To'] = toEmail
        msg['To'] = to
        part = MIMEText(content, _subtype='html',_charset='utf-8')
        msg.attach(part)
        self.s.sendmail(self.mail_user,to,msg.as_string())
        self.s.quit()
    