#! /usr/bin/python
# coding:utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib2
import logging
import os


class Enum(tuple):
    __getattr__ = tuple.index


BrowserType = Enum(['FIREFOX', 'CHROME', 'IE', 'SAFARI', 'PHANTOMJS'])


class CartoonDog:
    def __init__(self, site, save_folder='/root/Downloads',
                 browser=BrowserType.FIREFOX, driver=None):
        """
        :param site: 漫画的首页面
        :param begin: 章节的开始(含),0表示第一章
        :param end: 章节的结束(含),-1表示到结尾
        :param browser: 浏览器类型
        :param driver: 驱动，如果驱动程序在可访问的位置，这个参数非必须，对于PhantomJs，驱动程序就是改程序的地址
        """
        self.site = site
        self.title = None
        self.save_folder = save_folder
        self.curpage_image_list = []
        self.headers = {'Referer': site}

        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)

        if BrowserType.FIREFOX == browser:
            self.browser = webdriver.Firefox()
        elif BrowserType.CHROME == browser:
            self.browser = webdriver.Chrome(driver)
        elif BrowserType.IE == browser:
            self.browser = webdriver.Ie(driver)
        elif BrowserType.SAFARI == browser:
            self.browser = webdriver.Safari(driver)
        elif BrowserType.PHANTOMJS == browser:
            cap = dict(DesiredCapabilities.PHANTOMJS.copy())
            for key, value in self.headers.items():
                cap['{0}'.format(key)] = value
            self.browser = webdriver.PhantomJS(executable_path=driver, desired_capabilities=cap)
        else:
            raise TypeError('UNKNOWN BROWSER TYPE: %s' % browser)
        self.browser.get(self.site)
        self.__get_curpage_image_list()

        # if self.begin >= len(self.chapter_list) or (
        #                 0 <= self.end <= self.begin):
        #     raise Exception('the begin and end index of chapter is illegal')
        logging.basicConfig(
            format='[%(asctime)s] %(levelname)s::%(module)s::%(funcName)s() %(message)s',
            level=logging.INFO)

    def __del__(self):
        self.browser.quit()

    def __get_curpage_image_list(self):
        """
        获取当前页图片列表
        :return: None
        """
        self.browser.get(self.site)
        if self.title is None:
            self.title = self.browser.find_element_by_class_name('article-title').text
        curpage_image_list = self.browser.find_elements_by_css_selector('.article-content p img')

        for image_elem in curpage_image_list:
            self.curpage_image_list.append(image_elem.get_attribute('src'))

    # @staticmethod
    def __download(self, url, save_path, try_time=5, timeout=100):
        """
        下载
        :param url:
        :param save_path:
        :param try_time:
        :param timeout:
        :return:
        """
        while try_time > 0:
            try:
                request = urllib2.Request(url, headers=self.headers)
                content = urllib2.urlopen(request, timeout=timeout).read()
                with open(save_path, 'wb') as fp:
                    fp.write(content)
                break
            except Exception, et:
                logging.error(et, exc_info=True)
                try_time -= 1
                if try_time == 0:
                    logging.error(
                        'cannot download: %s to %s' % (url, save_path))

    def download_image(self, save_folder=None):
        """
        下载image
        :param save_folder: 保存路径
        :return:
        """
        save_folder = save_folder if save_folder is not None else self.save_folder

        save_folder = os.path.join(save_folder, self.title)
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        while True:
            for image_url in self.curpage_image_list:
                save_image_name = os.path.join(save_folder, ('%5s' % image_url.split('-')[-1]))
                self.__download(image_url, save_image_name)
            try:
                # 通过模拟点击加载下一页，如果已经是最后一页，会有弹窗提示，通过这个确定章节是否下完
                finish = self.browser.find_element_by_class_name('next-page').click()
            except NoSuchElementException, e:
                logging.info('There is no more page %s' % e)
                break
        logging.info('#### DOWNLOAD CHAPTER COMPLETE ####')

    def get_chapter_list(self):
        return self.curpage_image_list

    def start(self):

        self.download_image()


if __name__ == '__main__':
    # site = 'http://yxpjw.club/Girlt/2017/0918/3902.html'
    # headers = {'Referer': site}
    # driver = 'D:\\app\\phantomjs\\bin\\phantomjs.exe'
    # cap = dict(DesiredCapabilities.PHANTOMJS.copy())
    # for key, value in headers.items():
    #     cap['{0}'.format(key)] = value
    # browser = webdriver.PhantomJS(executable_path=driver, desired_capabilities=cap)
    # browser.get(site)
    # title = browser.find_element_by_class_name('article-title').text
    # print title
    # chapterList = browser.find_elements_by_name('article')
    # print chapterList


    image_util = CartoonDog(
        site='http://yxpjw.club/Girlt/2017/0918/3902.html',
        save_folder='D:\\yxpjw.club',
        browser=BrowserType.PHANTOMJS,
        driver='D:\\app\\phantomjs\\bin\\phantomjs.exe'
    )

    image_util.start()

    # print image_util.title
    # print image_util.get_chapter_list()
