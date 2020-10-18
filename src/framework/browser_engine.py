from selenium import webdriver
import configparser
import sys, os
import logger


class Browser(object):

    # 打开浏览器
    def open_browser(self):
        config = configparser.ConfigParser()
        dir = os.path.abspath('.').split('src')[0]
        config.read(dir + "/config/config.ini")
        browser = config.get("browserType", "browserName")
        logger.info("You had select %s browser." % browser)
        url = config.get("testServer", "URL")
        if browser == "Firefox":
            self.driver = webdriver.Firefox()
        elif browser == "Chrome":
            self.driver = webdriver.Chrome()
        elif browser == "IE":
            self.driver = webdriver.Ie()
        self.driver.set_window_size(1920, 1080)  # 分辨率
        # self.driver.maximize_window()#最大化
        self.driver.get(url)
        return self.driver

        # 打开url站点

    def open_url(self, url):
        self.driver.get(url)

        # 关闭浏览器

    def quit_browser(self):
        self.driver.quit()

    # 浏览器前进操作
    def forward(self):
        self.driver.forward()

    # 浏览器后退操作
    def back(self):
        self.driver.back()

    # 隐式等待
    def wait(self, seconds):
        self.driver.implicitly_wait(seconds)
