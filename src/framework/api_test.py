#-*- coding: UTF-8 -*-
import requests
from src.framework.public import *


class APITEST:
    def sendPostInJson(self,url,data="",header=""):
        urlLog = "The post request url is: " + url
        dataLog = "The post request data is: " + data
        headerLog = "The post request header is: " +header
        log_print(urlLog)
        log_print(dataLog)
        log_print(headerLog)
        try:
            r=requests.post(url,data,header)
            log_print(r.text)
            log_print("Send post request successful")
        except Exception,exce:
            r=None
            log_print("Send post request failed!")
        return r

    def sendGet(self,url,params=""):
        urlLog = "The get request url is: " + url
        paramsLog = "The get request params is: " + params
        log_print(urlLog)
        log_print(paramsLog)
        try:
            r=requests.get(url,params)
            log_print('The respone body is: '+ r.text)
            log_print("Send get request successful")
        except Exception,exce:
            r=None
            log_print("Send get request failed!")
        return r

