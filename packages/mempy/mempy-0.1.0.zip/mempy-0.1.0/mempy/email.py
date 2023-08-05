# *-* coding: UTF8 -*-
#==============================================================================
"""
[email.py] - Mempire E-mail module

이 모듈은 E-mail 관련 기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email import utils
from email.header import Header
import os

smtp_server  = "smtp.gmail.com"
port = 587
userid = ""     #Google ID
passwd = ""     #Google Password


def send_mail(from_user, to_user, cc_users, subject, text, attach):
        COMMASPACE = ", "
        msg = MIMEMultipart("alternative")
        msg["From"] = from_user
        msg["To"] = to_user
        msg["Cc"] = COMMASPACE.join(cc_users)
        msg["Subject"] = Header(s=subject, charset="utf-8")
        msg["Date"] = utils.formatdate(localtime = 1)
        msg.attach(MIMEText(text, "html", _charset="utf-8"))

        if (attach != None):
                part = MIMEBase("application", "octet-stream")
                part.set_payload(open(attach, "rb").read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment; filename=\"%s\"" % os.path.basename(attach))
                msg.attach(part)

        smtp = smtplib.SMTP(smtp_server, port)
        smtp.login(userid, passwd)
        smtp.sendmail(from_user, cc_users, msg.as_string())
        smtp.close()


def runTest():
    from treeinsight.lib import easygui as gui
    
    userid = "herokims"     #Google ID
    passwd = gui.passwordbox(msg="gmail계정의 비밀번호를 입력하세요",title="gmail 암호 입력")     #Google Password
    
    send_mail("herokims@gmail.com","herokims@hanmail.net",["herokims@hanmail.net"],\
            "테스트성공", "안녕하세요. 테스트 성공입니다",None)
    print("메일을 전송했습니다")
    

if __name__ == '__main__':
    runTest()
