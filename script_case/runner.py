#-*- coding: UTF-8 -*-
import unittest
import time
import os
import logging
#from HTMLTestRunner import HTMLTestRunner
from src.framework.HTMLTestRunner import HTMLTestRunner
import shutil

# 获取项目的根目录
now = time.strftime('%Y%m%d%H%M%S')  # 获取当前时间戳
script_dir = os.path.join(os.getcwd())
work_dir=script_dir.split('script_case')[0]
#创建当前报告目录
current_report_dir=work_dir + '/report/' + now
os.mkdir(current_report_dir)



# 自动搜索项目根目录下的所有case，构造测试集；返回TestSuite对象
discover = unittest.defaultTestLoader.discover(script_dir, pattern='test_*.py')

# 实例化TextTestRunner类
# runner = unittest.TextTestRunner(verbosity=2)


tmp_result = work_dir + '/report/' + now +'/result.html'  # 测试报告的完整路径
log = work_dir + '/report/' + now + '/log.txt'  # 日志的完整路径

logging.basicConfig(filename=log, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # filename 日志文件路径 level 日志的级别 format 格式

fp = open(tmp_result, 'wb')  # wb方式写入
runner = HTMLTestRunner(stream=fp, title='测试报告', description='aguest_master项目用例执行情况', verbosity=2)  # 构造runner

# 使用run()方法运行测试套件（即运行测试套件中的所有用例）
runner.run(discover)

