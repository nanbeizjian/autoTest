#-*- coding: UTF-8 -*-
import time
import os
import logging
import re
#import filecmp
import sys
import codecs
from SMTP_email import *
import shutil
from stat import ST_CTIME, ST_MTIME

#import win32gui, win32ui, win32con, win32api
#sys.path.append(r'F:\Python27\Lib')
#import Image
import xlrd
import random
from xlutils.copy import copy
copyFileCounts  = 0
WIDTH_STR = 25
WIDTH_STR_VALUE = 80


def log_print(mes):
    print mes
    sys.stdout.flush()
    info_public(mes)

def info_public(s,LogPath='c:\Simu_server\AutoTestLog.log'):
    #global LOG
    #create log object
    if (os.path.isfile(LogPath))==False:
        path1 = os.path.abspath(sys.argv[0])
        filepath = os.path.dirname(path1)
        LogPath = filepath + "\\AutoTestLog.log"
        #print "public 31: ",LogPath
        f=open(LogPath,'a')
        f.close()
    LOG= logging.getLogger("WtLog")
    #set log level.have 5 kinds.(DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG.setLevel(logging.INFO )
    #create handler,create file name
    handler =logging.FileHandler(LogPath)
    #define format you want to show
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    #input your format
    handler.setFormatter(formatter)

    #add your handler
    LOG.addHandler(handler)
    #write log informain
    LOG.info(s)
    LOG.removeHandler(handler)

def path_Rm_file(path,file_find):
    for root, dirs, files in os.walk(path, False):
        for name in files:
            if name.find(file_find)>-1:
                os.remove(os.path.join(root, name))
    return True

def GetFileList(dir, fileList):
    newDir = dir
    if os.path.isfile(dir):
        fileList.append(dir.decode('gbk'))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            #如果需要忽略某些文件夹，使用以下代码
            # #if s == "xxx":
            # continue
            newDir=os.path.join(dir,s)
            GetFileList(newDir, fileList)
    return fileList

#remove the  dir of path
def path_Rm(path):
    for root, dirs, files in os.walk(path, False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    return True

#copy dir from old to new
def path_copy(Oldpath,Newpath):
    os.chdir(Oldpath)
    fromdir = Oldpath
    todir = Newpath
    for root,dirs,files in os.walk(fromdir):
        for filename in files:
            path=os.path.join(root,filename)
            shutil.copyfile(path,'%s/%s'%(todir,filename))
            #stat1=os.stat(os.path.join(fromdir,filename))
            #os.utime(os.path.join(todir,filename),(stat1[ST_CTIME], stat1[ST_MTIME]))
    return True

copyFileCounts = 0

#copy files from sourceDir to targetDir
def copyFiles(sourceDir, targetDir):
    global copyFileCounts
    print sourceDir
    print "%s ��ǰ�����ļ���%s�Ѵ���%s ���ļ�" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), sourceDir,copyFileCounts)
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)

        if os.path.isfile(sourceF):
            #����Ŀ¼
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            copyFileCounts += 1

            #�ļ������ڣ����ߴ��ڵ��Ǵ�С��ͬ������
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                #2�����ļ�
                open(targetF, "wb").write(open(sourceF, "rb").read())
                print "%s %s �������" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), targetF)
            else:
                print "%s %s �Ѵ��ڣ����ظ�����" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), targetF)
        if os.path.isdir(sourceF):
            copyFiles(sourceF, targetF)
#get the subpath from path
def Getfindpath(path,findstr=''):
    list_path = path.split('\\')
    parentpath = ''
    for i in range(len(list_path)):
        if i==0:
            parentpath=list_path[i]
        else:
            parentpath = parentpath + '\\'+list_path[i]
        if len(findstr)==0:
            continue
        if list_path[i].find(findstr)>-1:
            break
    return parentpath
#check the file exist
def file_exist(file):
    if os.path.isfile(file) ==False:
        msg = file  + "not exists"
        print msg
        info_public(msg)
        return False
    return True
#check the path exist
def path_exist(path):
    if os.path.exists(path) ==False:
        msg = path  + "not exists"
        print msg
        info_public(msg)
        return False
    return True

#send email
def lotus_send(version,codePlugin,text='sdn',email_Flag = 'plain',list_result=[]):
        f = codecs.open(codePlugin[1]['subject'][0],'r','gbk')
        lines = f.readlines()
        content = unicode(''.join(lines))
        #content ='Dear all:' + '\r' + 'SDN设备 : ' + version + '版本，自动化测试结果如下，详情请查看附件！' + '\r' + '\r' + '\r' + '\r'.join(lines)
        f.close()
        if len(list_result) == 0:
            sub =  '【自动化测试】SDN设备' + version + '版本测试结果'
        else:
            sub =  '【自动化测试】SDN设备' + version + '版本测试结果' + '/'.join(list_result) + ' = '  + str(string.atoi(list_result[0])*100/string.atoi(list_result[1])) + '%'

        #email_Flag = 'plain'
        #codePlugin = [{'subject' : 'E:\\Simu_server\\result\\result__step1_ac_20130311_104552.txt', 'content' : '1abc'}, {'subject' : 'E:\\Simu_server\\result\\result__step1_ac_20130313_104443.txt', 'content' : '2abc'}]
        testmail =  smtpemail()
        testmail.read_mail_to_cc_list()
        print 'dic_email_file read:', testmail.dic_email_file
        mailto_list = testmail.dic_email_file['mailto_list']
        rate = string.atoi(list_result[0])*100/string.atoi(list_result[1])
        if rate < 100:
            print 'mailcc_fail_list is:',testmail.dic_email_file['mailcc_fail_list']
            mailcc_list = testmail.dic_email_file['mailcc_list']
            mailcc_fail_list = testmail.dic_email_file['mailcc_fail_list']
            mailcc_list.extend(mailcc_fail_list)
        else:
            mailcc_list = testmail.dic_email_file['mailcc_list']
        print 'mailcc_list is:',mailcc_list
        send_flag = testmail.dic_email_file['send_email_Flag']
        if send_flag=='1':
            testmail.send_mail_text(mailto_list,mailcc_list,sub,content,codePlugin,version,text,email_Flag)
            testmail.getresult()
        return True

#kill program
def kill_program(pidname = 'iexplore.exe',findstr='Explorer'):
        result =False
        REC_read= 'wmic process where caption="'+pidname+'" get caption,commandline /value'
        REC_kill=  'TASKKILL /F /IM ' + pidname
        print_mes = os.popen(REC_read).read()
        print print_mes
        info_public(print_mes)
        if print_mes.find(findstr)>-1:
            print_mes = os.popen(REC_kill).read()
            print print_mes
            info_public(print_mes)
        return result


def file_cmp(file1,file2):

    return True

#remove file
def clear_env_rm_file(file):
    os.remove(file)
    if file_exist(file):
        os.remove(file)
    fp = open(file, 'a')
    fp.close()
    return True

#If the file in a folder
def find_path(pathname,path):
    abspath=''
    for root, dirs, files in os.walk(path, False):
        for name in dirs:
            if name.find(pathname)>-1:
                abspath = os.path.join(root,name)
                break
    return abspath

#read file return list separate "$"
def readfile(filename,findstr,separator='$'):
    value = ''
    file_object = open(filename,"r")
    textlist = file_object.readlines()
    file_object.close()
    for x in textlist:
        if x.find(findstr)>-1:
            value = x.split(separator)[-1].strip()
    return value
#count file lines
def count_line_file(filename):
        count=-1
        file_object1 = open(filename,'r')
        textlist = file_object1.readlines()
        count=len(textlist)
        file_object1.close()
        return count
#write file
def writefile(filename,findstr,value,separator='$',file_mode ='tmp_resource.log'):
    #print 'writefile:',filename,findstr,value
    file_object = open(filename,"r")
    textlist = file_object.readlines()
    file_object.close()
    path1 = os.path.dirname(filename)
    new_filename =path1 + '\\' + file_mode
    if file_exist(new_filename):
        os.remove(new_filename)
    fp = open(new_filename, 'a')

    writefile_flag = False
    for x in textlist:
        if x.find(findstr)>-1:
            #print x
            #fp.write('\n')
            tmp_str= x.split(separator)[0]+separator +'\t'+ value + '\n'

            fp.write(tmp_str)
            msg = 'I write : ',tmp_str
            log_print(msg)
            writefile_flag = True

        else:
            fp.write(x)
    if writefile_flag==False:

        #tmp_str= x.split(separator)[0]+separator
        #tmp_str = tmp_str.ljust(WIDTH_STR) + value
        #tmp_str = tmp_str.rjust(WIDTH_STR_VALUE)
        tmp_str=findstr +separator + '\t'+value + '\n'
        msg = 'I write : ',tmp_str
        log_print(msg)
        fp.write(tmp_str)


    fp.close()

    #time.sleep(20)
    shutil.copy(new_filename,filename)

    return

def cmd_command(command,find_str,line_index='0',str_count='3'):
    tmp_count=1
    count=string.atoi(str_count)
    while True:
        info = os.popen(command).read().strip()
        tmp_index=string.atoi(line_index)
        re_line=re.compile("\n")
        re_list=re_line.split(info)
        length=len(re_list)
        if tmp_index>=0:
            index=tmp_index
        else:
            index=length+tmp_index
        if index>length:
            msg="the index is out of list length"
            log_print(msg)
            return False
        some_last=''
        for i in range(index,length):
            some_last=some_last+re_list[i]+'\n'
        msg = "some_last is:\n"+some_last
        log_print(msg)
        regex = re.compile(find_str)
        re_result=regex.search(some_last)
        print re_result
        if re_result:
            log_print("find this command ")
            break
        else:
            tmp_count+=1
            if tmp_count>count:
                log_print("this command not find")
                return False
            continue
    return True

def window_capture(dpath):
    '''''
截屏函数,调用方法window_capture('d:\\') ,参数为指定保存的目录
返回图片文件名,文件名格式:日期.jpg 如:2009328224853.jpg
    '''
    hwnd = 0
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC=win32ui.CreateDCFromHandle(hwndDC)
    saveDC=mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    MoniterDev=win32api.EnumDisplayMonitors(None,None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    #print w,h　　　＃图片大小
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0,0),(w, h) , mfcDC, (0,0), win32con.SRCCOPY)
    cc=time.gmtime()
    bmpname=str(cc[0])+str(cc[1])+str(cc[2])+str(cc[3]+8)+str(cc[4])+str(cc[5])+'.bmp'
    saveBitMap.SaveBitmapFile(saveDC, bmpname)
    Image.open(bmpname).save(bmpname[:-4]+".jpg")
    os.remove(bmpname)
    jpgname=bmpname[:-4]+'.jpg'
    djpgname=dpath+jpgname
    copy_command = "move %s %s" % (jpgname, djpgname)
    os.popen(copy_command)
    return bmpname[:-4]+'.jpg'

def write_excel(filename,sheetname,var_name,par_version):
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

def regex_add_esc(str):
    fbsArr = [ "\\", "$", "(", ")", "*", "+", ".", "[", "]", "?", "^", "{", "}", "|"]
    for key in fbsArr:
        if str.find(key)>=0:
            str = str.replace(key, "\\"+key)
    return str

def randomstrs(base_str,maxlength,fixedlength='0',fixedrangelength=False):
    random_str = ''
    startlength = 0
    length = len(base_str) - 1
    if fixedlength == '0':
        if fixedrangelength :
            randomlength = random.randint(fixedrangelength[0],fixedrangelength[1])
        else:
            randomlength = random.randint(1,maxlength)
    else:
        randomlength = fixedlength

    for i in range(startlength,randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


#生成标准A、B、C类中的一个单播ip地址，当指定ip时，会生成同网段单播ip地址，并返回掩码地址
def get_random_unicast_ip(ip=''):
    if ip =='':
        randomipheadlist=[]
        randomipheadlist.append(random.randint(1,126))
        randomipheadlist.append(random.randint(128,191))
        randomipheadlist.append(random.randint(192,223))
        randomiphead=random.choice(randomipheadlist)
        randomseconditem=random.randint(0,255)
        randomthreeitem=random.randint(0,255)
        randomfouritem=random.randint(0,255)
        randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
        if randomiphead >= 1 and randomiphead <= 126:
            netmask='255.0.0.0'
            for i in range(10):
                if randomip==str(randomiphead)+'.255.255.255' or randomip==str(randomiphead)+'.0.0.0':
                    randomseconditem=random.randint(0,255)
                    randomthreeitem=random.randint(0,255)
                    randomfouritem=random.randint(0,255)
                    randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
                else :
                    break
        if randomiphead >= 128 and randomiphead <= 191:
            netmask='255.255.0.0'
            for i in range(10):
                if randomip==str(randomiphead)+'.'+str(randomseconditem)+'.255.255' or randomip==str(randomiphead)+'.'+str(randomseconditem)+'.0.0':
                    randomthreeitem=random.randint(0,255)
                    randomfouritem=random.randint(0,255)
                    randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
                else :
                    break
        if randomiphead >= 192 and randomiphead <= 223:
            netmask='255.255.255.0'
            for i in range(10):
                if randomip==str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.255' or randomip==str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.0':
                    randomfouritem=random.randint(0,255)
                    randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
                else :
                    break
    else:
        randomiphead,randomseconditem,randomthreeitem,randomfouritem=ip.split('.')
        randomip=ip
        if int(randomiphead) >= 1 and int(randomiphead) <= 126:
            netmask='255.0.0.0'
            randomseconditem=random.randint(0,255)
            randomthreeitem=random.randint(0,255)
            randomfouritem=random.randint(0,255)
            randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
            for i in range(10):
                if randomip==str(randomiphead)+'.255.255.255' or randomip==str(randomiphead)+'.0.0.0':
                    randomseconditem=random.randint(0,255)
                    randomthreeitem=random.randint(0,255)
                    randomfouritem=random.randint(0,255)
                    randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
                else :
                    break
        if int(randomiphead) >= 128 and int(randomiphead) <= 191:
            netmask='255.255.0.0'
            randomthreeitem=random.randint(0,255)
            randomfouritem=random.randint(0,255)
            randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
            for i in range(10):
                if randomip==str(randomiphead)+'.'+str(randomseconditem)+'.255.255' or randomip==str(randomiphead)+'.'+str(randomseconditem)+'.0.0':
                    randomthreeitem=random.randint(0,255)
                    randomfouritem=random.randint(0,255)
                    randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
                else :
                    break
        if int(randomiphead) >= 192 and int(randomiphead) <= 223:
            netmask='255.255.255.0'
            randomfouritem=random.randint(0,255)
            randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
            for i in range(10):
                if randomip==str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.255' or randomip==str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.0':
                    randomfouritem=random.randint(0,255)
                    randomip=str(randomiphead)+'.'+str(randomseconditem)+'.'+str(randomthreeitem)+'.'+str(randomfouritem)
                else :
                    break

    return randomip,netmask