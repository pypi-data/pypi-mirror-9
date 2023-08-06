#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2011-8-28

@author: huwei
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_html_mail(sender, to, subject, message):
    """发送html邮件.
    ::
        send_html_mail(
            '爱玩儿<aiwanr.com@gmail.com>',
            'hu77wei@gmail.com',
            'hi, xiaohu xiaohu love you',
            '<html><body>hi, Im huwei </body></html>')
    :param sender: 发送者email 爱玩儿<aiwanr.com@gmail.com>.
    :param to: 接收者email.
    :param subject: 标题.
    :param message: 正文.
    :return: bool 成功发送返回true.
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(message, 'html', 'utf-8'))
    server = smtplib.SMTP('localhost')
    server.sendmail(sender, to, msg.as_string())
    server.quit()


def send_text_mail(sender, to, subject, message):
    """发送纯文本邮件.

    :param sender: string  发送者email 爱玩儿<aiwanr.com@gmail.com>.
    :param to: string 接收者email.
    :param subject: string 标题.
    :param message: string 正文.
    :return: bool 成功发送返回true.
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(message, 'plain', 'utf-8'))
    server = smtplib.SMTP('localhost')
    server.sendmail(sender, to, msg.as_string())
    server.quit()

if __name__ == '__main__':
    send_html_mail('爱玩儿<aiwanr.com@gmail.com>', '876213774@qq.com', 'hi, xiaohu xiaohu love you', '<html><body>hi, Im huwei </body></html>')
    pass
