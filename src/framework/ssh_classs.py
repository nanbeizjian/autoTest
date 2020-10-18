#-*- coding: UTF-8 -*-

import paramiko
import string
import re
import time
from public import *
from src.framework.logger import Logger
logger = Logger("XXXXX页面").getlog()

class mySSH:
    def __init__(self,HOST='',PORT='22',USERNAME='root',PASSWORD='system',Flag='chan',TimeOUT='10'):
        self.host=HOST
        self.port=string.atoi(PORT)
        self.username=USERNAME
        self.password=PASSWORD
        self.timeout=string.atoi(TimeOUT)
        self.flag = Flag
        self.re_msg=''
        self.trans=''
        self.chan=''
        self.ssh=''



    #初始化ssh连接
    def connect(self):
        try:
            if self.flag == 'client':
                self.ssh=paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.host,self.port,self.username,self.password)
            else:
                self.trans=paramiko.Transport((self.host,self.port))
                self.trans.connect(username=self.username,password=self.password)
                self.chan = self.trans.open_session()
                self.chan.settimeout(self.timeout)
                self.chan.get_pty()
                self.chan.invoke_shell()
                # 如果没有抛出异常说明连接成功，直接返回
                print u'ssh连接%s成功' % self.host
                # 接收到的网络数据解码为str
                time.sleep(0.5)
                print self.chan.recv(65535).decode('utf-8')
        except Exception,exce:
            logger.error(exce)
            logger.error("can not open host")
            if self.trans !='':
                self.trans.close()
            if self.chan !='':
                self.chan.close()
            return False
        return True
    #关闭ssh连接
    def close(self):
        if self.flag == 'client':
            self.ssh.close()
        else:
            self.chan.close()
            self.trans.close()
        return True

    def chan_send_keys(self,sendMsg,waitMsg,timeout=10):
        #执行sendMsg 并将回显结果返回给self.re_msg
        sendMsg += '\n'
        self.chan.send(sendMsg)
        begin_time = time.time()
        while True:
            try:
                time.sleep(0.3)
                msg = self.chan.recv(65535)
                #logger.error(msg)
                mre=re.compile("---more---")
                wait=re.compile(waitMsg)
                result_more = mre.search(msg)
                result_wait = wait.search(msg)
                self.re_msg  = self.re_msg + msg.strip()
                if (result_more or (not result_wait)):
                    #返回字符中假如能够找到'---more---'或者没有找到waitMsg的情况下，循环输入'空格+enter'
                    self.re_msg=mre.sub('',self.re_msg)
                    self.re_msg=self.re_msg.replace('\r\n','@@')    #当遇到more时，会将more剔除。然后为了连接被more打断的本来在同一行的
                    self.re_msg=self.re_msg.rstrip()                #回显信息，会考虑在被打断的位置使用rstrip去除右边的空白符，但是在此之前要保护
                    self.re_msg=self.re_msg.replace('@@','\r\n')    #‘\r\n’不被误剔除，所以先将'\r\n'先用@@替换之后再换回来
                    self.chan.send("  "+'\n')
                    if timeout< (time.time() - begin_time):
                        #没有等到waitMsg，超时退出
                        raise Exception,'Timeout waitting for waitMsg'
                else:
                    #返回字符中没有找到'---more---'且查找到waitMsg的情况下，退出循环
                    break
            finally:
                pass



    #下发相关配置
    def mycommand(self,sendMsg,waitMsg='#',TIMEOUT='10'):
        timeout = int(TIMEOUT)
        self.re_msg = ''
        try:
            if self.flag == 'client':
                stdin,stdout,stderr=self.ssh.exec_command(sendMsg,get_pty=True,timeout=timeout)
                self.re_msg=stdout.read()
                regex=re.compile('not found')
                re_result=regex.findall(self.re_msg)
                if len(re_result) !=0:
                    raise Exception,self.re_msg
                logger.error(self.re_msg)
            else:
                # chan模式执行命令
                self.chan_send_keys(sendMsg,waitMsg,timeout)
                logger.error(self.re_msg)
        except Exception,exce:
            logger.error(exce)
            logger.error(self.re_msg)
            logger.error("execute command Exception")
            return False,self.re_msg
        return True,self.re_msg


    #配置下发的回显信息中查找是否有指定的字符串
    def find_command(self,sendMsg,waitMsg,findStr,TIMEOUT='10'):
        #timewait=string.atoi(timew)
        #echo_info=''
        self.mycommand(sendMsg,waitMsg,TIMEOUT)
        regex = re.compile(findStr)
        re_result=regex.findall(self.re_msg)
        if re_result:
            msg = "find "+findStr+' successful'
            logger.error(msg)
            return True,self.re_msg
        else:
            msg="can't find "+findStr+" in echo"
            logger.error(msg)
            return False,self.re_msg

    def find_command_not_contain(self,sendMsg,waitStr,not_findStr,timew='2'):
        timewait=string.atoi(timew)
        echo_info=''
        try:
            stdin,stdout,stderr=self.ssh.exec_command(sendMsg)
            time.sleep(timewait)
            echo_info=stdout.read()
        except Exception,exce:
            logger.error(exce)
            logger.error("execute command Exception")
            return False
        logger.error(echo_info)
        regex = re.compile(not_findStr)
        re_result=regex.findall(echo_info)
        if re_result:
            msg = "find \""+not_findStr+'\"in echo,error!'
            logger.error(msg)
            return False
        else:
            msg="have not find \""+not_findStr+"\" in echo,successful"
            logger.error(msg)
            return True

    #下发一条命令从返回值查找是否存在多关键字
    def find_command_Multi(self,sendMsg,waitMsg,FINDSTR_str_T,A_TIMEOUT='10',Multi_FLAG='1',NUM='1',order_flag='0'):
        msg = '***********find_command_Multi function*************'
        logger.error(msg)
        tmp_num = 1
        TIMEOUT = string.atoi(A_TIMEOUT)
        num = string.atoi(NUM)
        FINDSTR = self.Mult_find_str(FINDSTR_str_T)
        while True:
            self.mycommand(sendMsg,waitMsg,TIMEOUT)
            #order_flag=1,表示乱序
            if order_flag=='1':
                re_result=True
                Find_str=FINDSTR_str_T.split(' ')
                logger.error('Find all str:'+str(Find_str))
                for strj in Find_str:
                    #regex = re.compile(strj)
                    tmp_result = re.findall(strj,self.re_msg,re.S)
                    logger.error('Find single str:'+str(tmp_result))
                    if not tmp_result:
                        re_result=False
                        return False,self.re_msg
            else :
                if Multi_FLAG=='1':
                    re_result = re.findall(FINDSTR,self.re_msg,re.S)
                else:
                    re_result=re.findall(FINDSTR,self.re_msg)
            if re_result:
                print_mes = "find this command "+FINDSTR_str_T
                logger.error(print_mes)
                return True,self.re_msg
            else:
                tmp_num = tmp_num +1
                if tmp_num>num:
                    print_mes = 'error: ' +FINDSTR_str_T + ' not find'
                    logger.error(print_mes)
                    self.error_NG= print_mes
                    return False,self.re_msg
                time.sleep(1)

    def Mult_find_str(self,FINDSTR_str_T):
        #msg = '*******Multi_find_str function********'
        #logger.error(msg)
        str_re =''
        FINDSTR_LIST=[]
        tmp_num = 0
        #FINDSTR_LIST = FINDSTR_str_T.split(' ')
        #print '************\n' ,FINDSTR_str_T.split(' ')
        for str in FINDSTR_str_T.split(' '):
            if len(str)>0:
                FINDSTR_LIST.append(str)
        #print FINDSTR_LIST
        for str in FINDSTR_LIST:
            if tmp_num==0:
                str_re = str
            else:
                str_re = str_re + '.+' + str
            tmp_num = tmp_num +1
        print_msg = '******* str_re*******\n'+str_re
        logger.error(print_msg)
        return str_re

    #获取命令回显信息中想要的任意值与阀值进行比较
    def value_keep(self,sendMsg,waitMsg,FINDSTR_str,keyword='accomm_keep',TIMEOUTSTR='2',queue='1',get_flag='END',delete_str='NULL',separator=''):
        if len(separator)==0:
            separator=' '
        TIMEOUT = string.atoi(TIMEOUTSTR)
        self.mycommand(sendMsg,waitMsg,TIMEOUT)
        list = []
        v_list =[]
        g_vlist=[]
        if get_flag == 'ALL_ECHO':
            #如果get_flag值为ALL_ECHO，直接用所有SENDSTR的回显信息进行比较
            tmp_echo_info = self.re_msg.replace('\r','').replace('\n','').replace(' ','').replace(waitMsg,'').replace('\x00','')
			#用''替换回显信息中的空格、回车
            #去除首尾两端的WAITSTR方便对比
            g_vlist = [tmp_echo_info]
        else:
            #如果get_flag值为其他，选出第几行或者所有的行进行比较
            list = self.find_msg(FINDSTR_str)     #找到所有包含FINDSTR_str_T关键字的行，每一行作为list的一个元素
            v_list=self.value_list(list,get_flag)   #get_flag选出第几行或者所有的行
            g_vlist = self.get_value_list(v_list,queue,separator,delete_str)   #通过queue在每行中寻找想要获取的值
        result_flag = False
        read_str =''
        write_value=''
        tmp_p = os.path.abspath(sys.argv[0])
        parent_path = Getfindpath(tmp_p,'SDN_')
        find_p = find_path('tmp_date',parent_path)
        filename = find_p +'\\resource.log'
        pre_value = ''
        if keyword.find('keep')>-1:
            try:
                read_str=readfile(filename,keyword)
            except Exception,exec_str:
                logger.error(exec_str)
                return False
            logger.error(read_str)
            if len(read_str)>0:
                #修改上次已存在的值
                pre_value = read_str
                msg="This time I modify the value"
                logger.error(msg)
                msg='Last time value is: '+pre_value
                logger.error(msg)
                msg='Now value is: '+g_vlist[0]
                logger.error(msg)
                try:
                    writefile(filename,keyword,g_vlist[0])
                except Exception,exec_str:
                    logger.error(exec_str)
                    return False
            else :
                keep_value = g_vlist[0]
                logger.error('The first time to key : '+keep_value)
                try:
                    writefile(filename,keyword,keep_value)
                except Exception,exec_str:
                    logger.error(exec_str)
                    return False
            return True
        msg='False! the keep value should be named contain "keep" !'
        logger.error(msg)
        return False

    def value_compare(self,sendMsg,waitMsg,FINDSTR_str_T,keyword='accomm_mem',comp_value='0',TIMEOUTSTR='2', queue='1',get_flag='END',delete_str='NULL',comp_flag='EQUAL' ,separator=''):
        if len(separator)==0:
            separator=' '
        TIMEOUT = string.atoi(TIMEOUTSTR)
        self.mycommand(sendMsg,waitMsg,TIMEOUT)
        list = []
        v_list =[]
        g_vlist=[]
        if get_flag == 'ALL_ECHO':
            #如果get_flag值为ALL_ECHO，直接用所有SENDSTR的回显信息进行比较
            tmp_echo_info = self.re_msg.replace('\r','').replace('\n','').replace(' ','').replace(waitMsg,'').replace('\x00','')
			#用''替换回显信息中的空格、回车
            #去除首尾两端的WAITSTR方便对比
            g_vlist = [tmp_echo_info]
        else:
            #如果get_flag值为其他，选出第几行或者所有的行进行比较
            list = self.find_msg(FINDSTR_str_T)     #找到所有包含FINDSTR_str_T关键字的行，每一行作为list的一个元素
            v_list=self.value_list(list,get_flag)   #get_flag选出第几行或者所有的行
            g_vlist = self.get_value_list(v_list,queue,separator,delete_str)   #通过queue在每行中寻找想要获取的值
        result_flag = False
        read_str =''
        write_value=''
        tmp_p = os.path.abspath(sys.argv[0])
        parent_path = Getfindpath(tmp_p,'SDN_')
        find_p = find_path('tmp_date',parent_path)
        filename = find_p +'\\resource.log'
        pre_value = ''
        if keyword.find('keep')>-1:
            try:
                read_str=readfile(filename,keyword)
            except Exception,exec_str:
                logger.error(exec_str)
                return False
            logger.error(read_str)
            if len(read_str)>0:
                #偶数次使用get_value命令，则取出文件中上次保存的值，与此次比较，并仍将keyword的值置为10086
                pre_value = read_str
                msg='Now,this values is',g_vlist
                logger.error(msg)
                msg='The keep value is',pre_value
                logger.error(msg)
                msg = 'This time I compare'
                logger.error(msg)
                if keyword.find('date')>-1:
                    result_flag = self.date_cmp(g_vlist,comp_value,keyword,comp_flag,pre_value)
                else:
                    result_flag = self.cmp_keep_value(g_vlist,comp_value,keyword,comp_flag,pre_value)
                return result_flag
            #首次使用get_value命令
            else :
                msg='False! You never keep '+keyword+" before"
                logger.error(msg)
                return False
        write_value = comp_value
        writefile(filename,keyword,write_value)
        #add by zhumingxing 20131227
        if keyword == "MIB_Flag":
           logger.error("this is mib value compare opearate!")
           comp_value = globle_dic.Ret_MIB_Node
        #end add
        result_flag = self.cmp_value(g_vlist,comp_value,keyword,comp_flag)
        time.sleep(1)
        print 'result_flag is: ',result_flag
        return result_flag

    #查找子串
    def find_msg(self,FINDSTR_str):
        #print '***********find_msg fuction *************'
        split_str ='\r'
        list=[]
        logger.error('in find_msg function 516: '+self.re_msg)
        for str in self.re_msg.split(split_str):
            if str.find(FINDSTR_str)>-1:
                list.append(str)
        return list

    #根据表示符get_flag获取信息列表
    def value_list(self,list,get_flag):
        logger.error ('**************value_list fuction*************')
        #print list
        #logger.error(list)
        tmp_list=[]
        if get_flag=='END':
            tmp_list.append(list[-1].strip())
        elif get_flag=='BEGIN':
            tmp_list.append(list[0].strip())
        elif  get_flag=='ALL':
            for x in list:
                tmp_list.append(x.strip())
        else:
            get_flag=int(get_flag)
            if get_flag <= len(list):
                tmp_list.append(list[get_flag -1 ])
        logger.error(tmp_list)
        return tmp_list

    #获取信息列表
    def get_value_list(self,list,queue,separator,del_str='NULL'):
        logger.error ('***************get_value_list fuction')
        #print '************list***********\n',list
        if separator == 'douhao':
            separator = ','
        re_list=[]
        tmp_str = ''
        msg = 'list is 257:'+str(list)
        #logger.error(msg)
        for i in list:
            print 'in for loop 445.'
            if queue == 'ALL':
                re_list.append(i)
                continue

            tmp_list =[]
            for x in i.split(separator):
                if len(x)>0:
                    tmp_list.append(x.strip())
            msg = '\n*********tmp_list*******\n'+str(tmp_list)
            logger.error(msg)
            if len(tmp_list)>= string.atoi(queue):
                print "471 queue is :",queue
                if string.atoi(queue)>=0:
                    tmp_string = tmp_list[string.atoi(queue)-1]
                else:
                    tmp_string = tmp_list[string.atoi(queue)]

                if del_str == 'NULL':
                    tmp_str= tmp_string
                else:
                    tmp_str = tmp_string.replace(del_str,'')

                re_list.append(tmp_str)
        msg = 're_list in get_value list is: '+str(re_list)
        logger.error(msg)
        return re_list

    #value_comprae子函数，日期比较
    def date_cmp(self,list,comp_value,keyword,comp_flag,PreValue=''):
        logger.error ('****************date_cmp fuction')
        cmp_flag = True
        if len(list)<=0:
            cmp_flag = False
            self.error_NG ='NG  error:not get ' + keyword +' the value'
            return cmp_flag

        if comp_flag=='BIG':
            x = list[0]
            logger.error('value of '+keyword+' is:'+x)
            logger.error('comp_value is: '+comp_value)
            logger.error('last time value  is: '+PreValue)
            if x.count('-') > 1:
                lasttime = time.mktime(time.strptime(PreValue,"%Y-%m-%d %H:%M:%S"))
                nowtime = time.mktime(time.strptime(x,"%Y-%m-%d %H:%M:%S"))
            else:
                if PreValue.find('CST') > -1:
                    GMT_PreValue = PreValue.replace('CST','GMT')
                    lasttime = time.mktime(time.strptime(PreValue,"%a %b %d %H:%M:%S %Z %Y")) + 8*60*60
                else:
                    lasttime = time.mktime(time.strptime(PreValue,"%a %b %d %H:%M:%S %Z %Y"))
                if x.find('CST') > -1:
                    GMT_x = x.strip().replace('CST','GMT')
                    nowtime = time.mktime(time.strptime(x,"%a %b %d %H:%M:%S %Z %Y"))+ 8*60*60
                else:
                    nowtime = time.mktime(time.strptime(x,"%a %b %d %H:%M:%S %Z %Y"))

            msg1 = 'the time-stamp of '+PreValue+' is: '+str(lasttime)
            msg2 = 'the time-stamp now '+x+' is: '+str(nowtime)
            logger.error(msg1)
            logger.error(msg2)
            if nowtime - lasttime > float(comp_value):
                cmp_flag =False
                self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is bigger then ' + comp_value
                return cmp_flag

        elif comp_flag=='SMALL':
            x=list[0]
            logger.error('value of '+keyword+' is:'+x)
            logger.error('comp_value is: '+comp_value)
            logger.error('last time value  is: '+PreValue)
            if x.count('-') > 1:
                lasttime = time.mktime(time.strptime(PreValue,"%Y-%m-%d %H:%M:%S"))
                nowtime = time.mktime(time.strptime(x,"%Y-%m-%d %H:%M:%S"))
            else:
                if PreValue.find('CST') > -1:
                    GMT_PreValue = PreValue.replace('CST','GMT')
                    lasttime = time.mktime(time.strptime(PreValue,"%a %b %d %H:%M:%S %Z %Y")) + 8*60*60
                else:
                    lasttime = time.mktime(time.strptime(PreValue,"%a %b %d %H:%M:%S %Z %Y"))
                if x.find('CST') > -1:
                    GMT_x = x.strip().replace('CST','GMT')
                    nowtime = time.mktime(time.strptime(x,"%a %b %d %H:%M:%S %Z %Y"))+ 8*60*60
                else:
                    nowtime = time.mktime(time.strptime(x,"%a %b %d %H:%M:%S %Z %Y"))

                msg1 = 'the time-stamp of '+PreValue+' is: '+str(lasttime)
                msg2 = 'the time-stamp now '+x+' is: '+str(nowtime)
                logger.error(msg1)
                logger.error(msg2)
                if nowtime - lasttime < float(comp_value):
                    cmp_flag = False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is smaller then ' + comp_value
                    return cmp_flag

    #getvalue子函数，值比较
    def cmp_value(self,list,comp_value,keyword,comp_flag):
        #print '***********get_value_list fuction *************'
        cmp_flag = True
        if len(list)<=0:
            cmp_flag = False
            self.error_NG ='NG  error:not get ' + keyword +' the value'
            return cmp_flag

        if comp_flag=='BIG':
            for x in list:
                logger.error('value of '+keyword+' is:'+x)
                logger.error('comp_value is: '+comp_value)
                if float(x.strip()) > float(comp_value):
                    cmp_flag = False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is bigger then ' + str(comp_value)
                    #print 'self.error_NG ',self.error_NG
                    return cmp_flag
        elif comp_flag=='SMALL':
            for x in list:
                logger.error('value of '+keyword+' is:'+x)
                logger.error('comp_value is: '+comp_value)
                if float(x.strip()) < float(comp_value):
                    cmp_flag = False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is smaller then ' + str(comp_value)
                    #print 'self.error_NG ',self.error_NG
                    return cmp_flag
        elif comp_flag=='EQUAL':
            for x in list:
                logger.error('value of '+keyword+' is:'+x)
                logger.error('comp_value is: '+comp_value)
                if (x.strip()).isdigit() != 1:
                    #add by zhumingxing 20131227
                    if keyword == "MIB_Flag":
                       if comp_value.find(x.strip()) == -1:
                          return False
                       else:
                          return True
                    #end add
                    if x.strip() != comp_value:
                        cmp_flag = False
                        self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is not equal to ' + str(comp_value)
                        return cmp_flag
                elif float(x.strip())!= float(comp_value):
                    cmp_flag = False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip()+' is not equal to ' + str(comp_value)
                    #print 'self.error_NG ',self.error_NG
                    return cmp_flag
        return cmp_flag


    #value_comprae子函数，值比较
    def cmp_keep_value(self,list,comp_value,keyword,comp_flag,PreValue=''):
        logger.error ('****************cmp_keep_value fuction')
        cmp_flag = True
        pre_flag = len(PreValue)
        if len(list)<=0:
            cmp_flag = False
            self.error_NG ='NG  error:not get ' + keyword +' the value'
            return cmp_flag

        if comp_flag=='BIG':
            for x in list:
                self.value_now = x
                logger.error('value of '+keyword+' is:'+x)
                logger.error('comp_value is: '+comp_value)
                logger.error('last time value  is: '+PreValue)
                if float(x.strip()) - float(PreValue) > float(comp_value):
                    cmp_flag =False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is bigger then ' + comp_value
                    return cmp_flag

        elif comp_flag=='SMALL':
            for x in list:
                self.value_now = x
                logger.error('value of '+keyword+' is:'+x)
                logger.error('comp_value is: '+comp_value)
                logger.error('last time value  is: '+PreValue)
                if float(x.strip()) - float(PreValue) < float(comp_value):
                    cmp_flag = False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is smaller then ' + comp_value
                    return cmp_flag

        elif comp_flag=='EQUAL':
            for x in list:
                self.value_now = x
                logger.error('comp_value is: '+comp_value)
                logger.error('value of '+keyword+' is: '+x)
                logger.error('last time value is:    '+PreValue)
                if x.strip().isdigit() == 0:
                    if x.strip() != PreValue:
                        cmp_flag=False
                        self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is not equal to ' + comp_value
                        return cmp_flag
                elif float(x.strip()) - float(PreValue) != float(comp_value):
                    cmp_flag = False
                    self.error_NG ='NG  error: ' + keyword + ' get value ' + x.strip() +' is not equal to ' + comp_value
                    return cmp_flag
        return cmp_flag

#获取命令的回显信息写入全局变量文件global_param.xls
    def get_global_param(self,sendMsg,waitMsg,FINDSTR_str_T,global_name,queue='1',get_flag='END',delstr='',separator=' ',listindex='ALL',TIMEOUTSTR='2',writeglobal=True):
        print '*******get_global_param function**********'
        #enter_key = self.tn_port()
        tmp_send = sendMsg
        TIMEOUT = string.atoi(TIMEOUTSTR)
        if type(listindex)==str:
            if listindex.isdigit():
                listindex=eval(listindex)
        self.mycommand(sendMsg,waitMsg,TIMEOUT)
        list = []
        v_list =[]
        g_vlist=[]
        #Flag = self.send_keys(tmp_send,enter_key,WAITSTR,TIMEOUT)
        #if Flag==False:
        #    return False
        list = self.find_msg(FINDSTR_str_T)     #找到所有包含FINDSTR_str_T关键字的行，每一行作为list的一个元素
        v_list=self.value_list(list,get_flag)   #get_flag选出第几行或者所有的行
        g_vlist = self.get_value_list(v_list,queue,separator,delstr)   #通过queue在每行中寻找想要获取的值
        if listindex == 'ALL':
            print u'捕获到的值为%s' % ' '.join(g_vlist)
            param_value=' '.join(g_vlist)
        else :
            if listindex >= len(g_vlist):
                listindex = 0
                print u'listindex大于捕获列表长度，将改为捕获第一项'
            print u'捕获到的值为%s' % g_vlist[listindex]
            param_value=g_vlist[listindex]
        if writeglobal :
            path1 = os.path.abspath(sys.argv[0])
            findstr = 'SDN'
            tmp_global_file ='\\global\\global_param.xls'
            path_parent = Getfindpath(path1,findstr)
            global_file = path_parent + tmp_global_file
            res=self.write_excel(global_file,'global',global_name,param_value)
        else :
            res=True
        return res,param_value

    #写excel文件
    def write_excel(self,filename,sheetname,var_name,par_version):
        print '********write_excel function***********'
        obj_source = xlrd.open_workbook(filename,formatting_info=True)
        source_table = obj_source.sheet_by_name(sheetname)
        nrows = source_table.nrows
        print 'the rows of file is:',nrows
        flag=False
        for x in range(nrows):
            if source_table.cell(x,0).value==var_name:
                flag=True
                break
        print "x is:",x
        sheet = copy(obj_source)
        print 'have get sheet'
        wbg = sheet.get_sheet(0)
        if flag==False:
            wbg.write(x+1,0,var_name)
            wbg.write(x+1,1,par_version)
        else:
            wbg.write(x,1,par_version)
        sheet.save(filename)
        return True