import os
import re
import time
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 设置Chrome浏览器的路径
chrome_binary_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 根据您的实际安装路径修改

# 设置ChromeOptions
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chrome_binary_path

# 创建Chrome WebDriver实例
driver = webdriver.Chrome(options=chrome_options)

# 基础URL
base_url = "https://guangfu.bjx.com.cn/search/"

# 要搜索的关键词列表
keywords = ["光伏", "太阳能", "新能源"]  # 您可以根据实际需求添加更多关键词

# 遍历关键词列表
for keyword in keywords:
    keyword_dir = os.path.join("CrawlTexts/Guangfu", keyword)
    if not os.path.exists(keyword_dir):
        os.mkdir(keyword_dir)

    # 对关键词进行URL编码
    encoded_keyword = quote(keyword)

    # 构建搜索链接
    search_url = f"https://guangfu.bjx.com.cn/search/?kw={encoded_keyword}&type=5"

    print(f"搜索关键词 '{keyword}' 的文章：")

    # 获取总页数
    driver.get(search_url)
    time.sleep(3)  # 等待页面加载
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, "html.parser")
    page_info = soup.find("div", class_="page-info")
    if page_info:
        total_pages = int(re.search(r"/ (\d+) 页", page_info.get_text()).group(1))
    else:
        total_pages = 1

    print(f"共 {total_pages} 页")

    for page in range(1, total_pages + 1):
        # 构建分页链接
        page_url = search_url + f"&index={page}"

        # 使用Selenium打开网页
        driver.get(page_url)
        time.sleep(3)  # 等待页面加载

        # 获取页面内容
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, "html.parser")

        # 在解析后的内容中查找含有关键词的文章链接
        cc_list_div = soup.find("div", class_="cc-list")
        if cc_list_div:
            items = cc_list_div.find_all("div", class_="item")
            if items:
                for item in items:
                    top_div = item.find("div", class_="top")
                    if top_div:
                        article_title = top_div.find("span").find("a").get_text()
                        article_link = top_div.find("span").find("a")["href"]
                        full_article_link = urljoin(base_url, article_link)  # 构建完整的文章链接

                        print(f"标题：{article_title}")
                        print(f"链接：{full_article_link}")

                        # TODO: 下载文章内容并保存到本地txt文件

                        print("-" * 50)
            else:
                print(f"未找到含有关键词 '{keyword}' 的文章")
        else:
            print(f"未找到cc-list div元素")

# 关闭浏览器窗口
driver.quit()
