#!/usr/bin/python
# coding:utf-8

import cartoon_dog

if __name__ == '__main__':
    site = 'http://www.u17.com/comic/3166.html'

    crawler = cartoon_dog.cartoon_dog.CartoonDog(
        site=site,  # 漫画首页
        begin=0,  # 起始章节
        end=2,  # 结束章节
        save_folder='D:\\yanjiali',  # 保存路径，不存在会自动创建
        browser=cartoon_dog.cartoon_dog.BrowserType.PHANTOMJS,  # 浏览器类型：FIREFOX，CHROME，SAFARI，IE，PHANTOMJS
        driver='D:\\app\\phantomjs\\bin\\phantomjs.exe'  # 驱动程序路径，firefox不需要
    )

    crawler.start()
