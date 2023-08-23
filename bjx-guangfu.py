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
    keyword_dir = os.path.join("CrawlTexts\Guangfu", keyword)
    if not os.path.exists(keyword_dir):
        os.mkdir(keyword_dir)

    # 对关键词进行URL编码
    encoded_keyword = quote(keyword)

    # 构建搜索链接
    search_url = f"https://guangfu.bjx.com.cn/search/?kw={encoded_keyword}&type=5"

    print(f"搜索关键词 '{keyword}' 的文章：")
    page = 1

    while True:
        # 构建分页链接
        page_url = search_url + f"&index={page}"

        # 使用Selenium打开网页
        driver.get(page_url)
        time.sleep(3)  # 等待页面加载

        # 获取页面内容
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, "html.parser")

        # 解析页面内容，查找含有关键词的文章链接
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

                        # 使用Selenium打开文章链接
                        driver.get(full_article_link)
                        time.sleep(3)  # 等待页面加载

                        # 获取文章内容
                        article_element = driver.find_element(By.CSS_SELECTOR, ".cc-article")
                        article_content = article_element.text

                        # 在这里处理文件名，清理非法字符
                        cleaned_article_title = re.sub(r'[^\w\s-]', '', article_title)
                        cleaned_article_title = re.sub(r'\s+', '-', cleaned_article_title).strip()

                        # 构建保存文件的路径
                        filename = os.path.join(keyword_dir, f"{cleaned_article_title}.txt")
                        with open(filename, "w", encoding="utf-8") as file:
                            file.write(f"标题：{article_title}\n")
                            file.write(f"链接：{full_article_link}\n")
                            file.write(article_content)  # 保存文章内容
                        print(f"已保存到文件：{filename}")

                        print("-" * 50)
            else:
                print(f"未找到含有关键词 '{keyword}' 的文章")
                break
        else:
            print(f"未找到cc-list div元素")
            break

        # 转到下一页
        page += 1

# 关闭浏览器窗口
driver.quit()