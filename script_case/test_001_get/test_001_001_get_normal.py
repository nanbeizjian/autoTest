import unittest
from src.framework.public import *
import src.framework.api_test as api_test



class Get(unittest.TestCase):
    #https://oauth-api.cloud.huawei.com/rest.php?nsp_svc=nsp.scope.app.get&appid=102538625&type=2
    #https://oauth-api.cloud.huawei.com/rest.php?nsp_svc=huawei.oauth2.user.getTokenInfo&access_token=CgB6e3x9CRRP6r8lSOpVSWzVSnmI9DSKJdo6PngAsDlEJGWnHqB3Lv9YXAQpjNO/mTfiJjakayLGTF5V1wwzI89Q

    def setUp(self):
        log_print('Start to execute script :'+ os.path.abspath(__file__))

    def tearDown(self):
        log_print('Finish to execute script :'+ os.path.abspath(__file__))

    def test_001_001_01(self):
        tmpUrl = "https://oauth-api.cloud.huawei.com/rest.php"
        tmpParams = "nsp_svc=nsp.scope.app.get&appid=102538625&type=2"
        get=api_test.APITEST()
        re=get.sendGet(tmpUrl,tmpParams)
        self.assertEqual(re.status_code,200)
