#-*- coding: UTF-8 -*-
#-----------------------------------------------------------------------------
# Name:        telnet_class.py
# Purpose:     telnet class of users
#
# Author:      zhangdong
#
# Created:     2013/01/13
# RCS-ID:      $Id: telnet_class.py $
# Copyright:   (c) 2006
# Licence:     <your licence>
#-----------------------------------------------------------------------------
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from public import *
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import string
import base64
import time

#此类用于处理邮件发送
class smtpemail:
    def __init__(self,SMTPSERVER='smtp.163.com',USERNAME='zoomserver@163.com',PASSWORD='zoomtech123',POSTFIX='zoomserver@163.com',DEBUG ='1',PORT='25',TIMEOUT='20'):
        self.username = USERNAME
        self.password = PASSWORD
        self.server = SMTPSERVER
        self.postfix = POSTFIX
        self.debug = string.atoi(DEBUG)
        self.result = False
        self.email_cc =[]
        self.email_to =[]
        self.port = string.atoi(PORT)
        self.timeout = string.atoi(TIMEOUT)
        self.email_dic={'mailto_list':1,'mailcc_list':2,'mailfrom_user':3,'mailfrom_passwd':4,'mail_smtpserver':5,'mail_timeout':6,'mail_smtpport':7,'send_email_Flag':8,'mailcc_fail_list':9}
        self.dic_email_file={}

    def send_mail_text(self,to_list=[],cc_list=[],sub='sdn',content='sdn',codePlugin = [],version='sdn',text='sdn',email_Flag='html'):
        self.email = smtplib.SMTP()
        self.email.set_debuglevel(self.debug)

        #msg = MIMEText(content,_subtype='html',_charset='gb2312')
        msg = MIMEMultipart()
        msg['Subject'] = sub
        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        msg['From'] = self.postfix
        msg['To']=','.join(to_list)
        msg['Cc']=','.join(cc_list)
        #msg.attach(content)    #�ʼ�����
        #msg.set_payload(content)
        msg.attach(MIMEText( content, email_Flag, 'utf-8' ))
        test = '\r'+ '\r' + '\r'
        msg.attach(MIMEText( test, email_Flag, 'utf-8' ))
        #jgd-2014-4-3,add遍历读取所有子文件夹的执行总结果的日志文件,添加到邮件正文中
        k="-----------------------------------------end-------------------------------------------------------------"
        for i in range(0,len(codePlugin[-1]['subject'])):
            #下面if判断语句主要为保留第一个添加日志AUTO_TEST。。。文件里“自动化测试报告”字样，去除后续添加日志文件相应的字样
            if i==0:
                msg.attach(MIMEText(open(codePlugin[-1]['subject'][i],"r").read(),_subtype='plain',_charset='gb2312'))
                msg.attach(MIMEText(k,_subtype='plain',_charset='gb2312'))
            else:
                Auto_test=open(codePlugin[-1]['subject'][i],"r").readlines()
                text=''
                for i in range(5,len(Auto_test)):
                    text=text+Auto_test[i]
                msg.attach(MIMEText(text,_subtype='plain',_charset='gb2312'))
                msg.attach(MIMEText(k,_subtype='plain',_charset='gb2312'))
        test = '\r'+ '\r' + '\r'
        msg.attach(MIMEText( test ,email_Flag, 'utf-8' ))


        #mitFile =MIMEText(open(plugin['subject']).read())
        #mitFile['Content-Type']='application/octet-stream'
        #tmp_str = 'attachment;filename ="' + plugin['subject'].split('\\')[-1] + '"'
        #mitFile['Content-Disposition']=tmp_str
        mitFile = MIMEApplication( open(codePlugin[0]['subject'],'rb').read(), )
        mitFile.add_header( 'content-disposition', 'attachment', filename=codePlugin[0]['subject'].split('\\')[-1] )
        msg.attach( mitFile )

        try:

            #self.email = smtplib.SMTP(self.server,self.port,self.timeout)

            self.email.connect(self.server)

            self.email.ehlo()
            self.email.starttls()
            self.email.ehlo()

            self.email.login(self.username,self.password)
            to_list.extend(cc_list)
            self.email.sendmail(self.postfix,to_list,msg.as_string())
            #self.email.sendmail(self.postfix,cc_list,msg.as_string())
            time.sleep(5)
            self.result = True

        except Exception,e:
            print str(e)
            self.result =False

    def getresult(self):
        if self.result:
            print 'send email success'
        else:
            print 'send email fail'
        return self.result

    def close(self):
        self.email.quit()

    def read_mail_to_cc_list(self,filename=''):
        #tmp_dic = {}
        #print '***********read_mail_to_cc_list fuction**********'
        if len(filename)==0:
            path1 = os.path.abspath(sys.argv[0])
            filepath = os.path.dirname(path1)
            filepath_foxmail = filepath + '\\auto_conf'
            if os.path.exists(filepath_foxmail) == False:
                msg = filepath_foxmail  + " not exists"
                print msg
                log_print(msg)
                return False
        filename = filepath_foxmail + '\\foxmail.conf'
        if os.path.isfile(filename) ==False:
            msg = filename  + " not exists"
            print msg
            info_public(msg)
            return False
        file_object = open(filename,"r")
        textlist = file_object.readlines()
        file_object.close()

        self.email_cc =[]
        self.email_to =[]
        self.email_fail_ccto = []
        foxmail_email=''
        foxmail_email_people=[]
        #print '*********************'
        for line in textlist:
            foxmail_email =(line.split('$'))[0].strip()
            print line
            if self.email_dic.has_key(foxmail_email):
                if self.email_dic[foxmail_email] == 1:
                    [self.email_to.append(x.strip()) for x in (line.split('$'))[1].split(',')]
                elif self.email_dic[foxmail_email] == 2:
                    [self.email_cc.append(x.strip()) for x in (line.split('$'))[1].split(',')]
                elif self.email_dic[foxmail_email] == 3:

                    self.username = self.postfix = (line.split('$'))[1].split(',')[0].strip()
                    #print 'self.username,self.postfix',self.username,self.postfix
                elif self.email_dic[foxmail_email] == 4:
                    self.password  = (line.split('$'))[1].split(',')[0].strip()
                    #print 'self.password',self.password
                elif self.email_dic[foxmail_email] == 5:
                    self.server = (line.split('$'))[1].split(',')[0].strip()
                elif self.email_dic[foxmail_email] == 6:
                    self.timeout = (line.split('$'))[1].split(',')[0].strip()
                elif self.email_dic[foxmail_email] == 7:
                    self.port  = (line.split('$'))[1].split(',')[0].strip()
                elif self.email_dic[foxmail_email] == 8:
                    self.dic_email_file['send_email_Flag']  = (line.split('$'))[1].split(',')[0].strip()
                elif self.email_dic[foxmail_email] == 9:
                    [self.email_fail_ccto.append(x.strip()) for x in (line.split('$'))[1].split(',')]
                    #print 'send_email_Flag:',self.dic_email_file['send_email_Flag']
                    #print '##########################\n'
        self.dic_email_file['mailto_list'] = self.email_to
        self.dic_email_file['mailcc_fail_list'] = self.email_fail_ccto
        self.dic_email_file['mailcc_list'] = self.email_cc
        self.dic_email_file['mail_user'] = self.username
        self.dic_email_file['mail_postfix'] = self.postfix
        self.dic_email_file['mail_passwd'] = self.password
        self.dic_email_file['mail_smtpserver'] = self.server
        self.dic_email_file['mail_timeout'] = self.timeout
        self.dic_email_file['mail_port'] = self.port

        #print 'self.dic_email_file:',self.dic_email_file
        #self.dic_email_file={'mailto_list':self.email_to,'mailcc_list':self.email_cc,'mail_user':self.username,'mail_postfix':self.postfix,'mail_passwd':self.password,'mail_smtpserver':self.server,'mail_timeout':self.timeout,'mail_port':self.port}
        #return tmp_dic
        return True

'''
if __name__=='__main__':

    version = 'MIPS_1018R31T2.2_P3_ZTE'
    mailto_list=['zhangd@zoomnetcom.com','zhangd@zoomnetcom.com','leixw@zoomnetcom.com','wangtf@zoomnetcom.com','caohzh@zoomnetcom.com','yaoj@zoomnetcom.com','luzw@zoomnetcom.com']
    mailcc_list=["zhangdong@zoomnetcom.com","xueyd@zoomnetcom.com"]
    sub = 'this is the AC version: ' + version + ' auto test_redpower.py result'
    content ='Dear all:'  +'\r' + 'this is the AC version: '+version +' autoest result'+'\r'+'Please see the Plugin'
    text='test_redpower.py'
    email_Flag = 'plain'
    codePlugin = [{'subject' : 'E:\\Simu_server\\11\\result\\result20130416_142701\\AUTO_TEST_REPORT_MIPS_1018R31T2.2_P3_ZTE_20130416_142702.txt', 'content' : '1abc'}]
    testmail = smtpemail()
    testmail.read_mail_to_cc_list()
    print 'testmail.dic_email_file:', testmail.dic_email_file
    mailto_list = testmail.dic_email_file['mailto_list']
    mailcc_list = testmail.dic_email_file['mailcc_list']
    testmail.send_mail_text(mailto_list,mailcc_list,sub,content,codePlugin,version,text,email_Flag)
    testmail.getresult()
'''

