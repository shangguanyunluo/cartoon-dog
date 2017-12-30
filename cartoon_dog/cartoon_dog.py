#! /usr/bin/python
# coding:utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import urllib2
import logging
import os


class Enum(tuple):
    __getattr__ = tuple.index


BrowserType = Enum(['FIREFOX', 'CHROME', 'IE', 'SAFARI', 'PHANTOMJS'])


class CartoonDog:
    def __init__(self, site, begin=0, end=-1, save_folder='/root/Downloads',
                 browser=BrowserType.FIREFOX, driver=None):
        """
        :param site: 漫画的首页面
        :param begin: 章节的开始(含),0表示第一章
        :param end: 章节的结束(含),-1表示到结尾
        :param browser: 浏览器类型
        :param driver: 驱动，如果驱动程序在可访问的位置，这个参数非必须，对于PhantomJs，驱动程序就是改程序的地址
        """
        self.site = site
        self.begin = begin
        self.end = end
        self.save_folder = save_folder
        self.chapter_list = []

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
            self.browser = webdriver.PhantomJS(driver)
        else:
            raise TypeError('UNKNOWN BROWSER TYPE: %s' % browser)

        self.__get_chapter_list()

        if self.begin >= len(self.chapter_list) or (
                        0 <= self.end <= self.begin):
            raise Exception('the begin and end index of chapter is illegal')
        logging.basicConfig(
            format='[%(asctime)s] %(levelname)s::%(module)s::%(funcName)s() %(message)s',
            level=logging.INFO)

    def __del__(self):
        self.browser.quit()

    def __get_chapter_list(self):
        """
        获取章节信息
        :return: None
        """
        self.browser.get(self.site)
        chapter_elem_list = self.browser.find_elements_by_css_selector(
            '.chapterlist_box ul li a')
        # chapter_elem_list.reverse()

        for chapter_elem in chapter_elem_list:
            self.chapter_list.append(
                (chapter_elem.get_attribute('title'), chapter_elem.get_attribute('href')))

    @staticmethod
    def __download(url, save_path, try_time=3, timeout=30):
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
                content = urllib2.urlopen(url, timeout=timeout).read()
                with open(save_path, 'wb') as fp:
                    fp.write(content)
                break
            except Exception, et:
                logging.error(et, exc_info=True)
                try_time -= 1
                if try_time == 0:
                    logging.error(
                        'cannot download: %s to %s' % (url, save_path))

    def download_chapter(self, chapter_idx, save_folder=None):
        """
        下载章节
        :param chapter_idx: 章节id
        :param save_folder: 保存路径
        :return:
        """
        chapter = self.chapter_list[chapter_idx]
        save_folder = save_folder if save_folder is not None else self.save_folder

        chapter_title = chapter[0]
        chapter_url = chapter[1]

        save_folder = os.path.join(save_folder, chapter_title)
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        self.browser.get(chapter_url)
        pageNum = 1
        curNum, totalNum = self.browser.find_element_by_class_name('pagenum').text.split('/')
        totalNum = int(totalNum)
        while True:
            image_url = self.browser.find_element_by_class_name('cur_img').get_attribute('src')
            save_image_name = os.path.join(save_folder,
                                           ('%5s' % pageNum) + '.' +
                                           os.path.basename(image_url).split(
                                               '.')[-1])
            self.__download(image_url, save_image_name)

            # 通过模拟点击加载下一页，如果已经是最后一页，会有弹窗提示，通过这个确定章节是否下完
            self.browser.find_element_by_css_selector('.next').click()
            try:
                # 没有结束弹窗，继续下载
                # self.browser.find_element_by_css_selector('#bgDiv')
                if pageNum <= totalNum:
                    pageNum += 1
                    continue
                else:
                    break

            except NoSuchElementException, e:
                logging.info('click next error %s' % e)
        logging.info('#### DOWNLOAD CHAPTER COMPLETE ####')

    def get_chapter_list(self):
        return self.chapter_list

    def start(self):
        begin = self.begin if self.begin >= 0 else 0
        end = self.end if self.end >= 0 else len(self.chapter_list)

        for chapter_idx in xrange(begin, end):
            self.download_chapter(chapter_idx)


if __name__ == '__main__':
    site = 'http://www.u17.com/comic/3166.html'

    crawler = CartoonDog(
        site=site,  # 漫画首页
        begin=0,  # 起始章节
        end=2,  # 结束章节
        save_folder='D:\\yanjiali',  # 保存路径，不存在会自动创建
        browser=BrowserType.PHANTOMJS,  # 浏览器类型：FIREFOX，CHROME，SAFARI，IE，PHANTOMJS
        driver='D:\\app\\phantomjs\\bin\\phantomjs.exe'  # 驱动程序路径，firefox不需要
    )

    crawler.start()
