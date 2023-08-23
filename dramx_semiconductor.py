import os
import requests
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import re

# 基础URL
base_url = "https://www.dramx.com/Search/"

# 要搜索的关键词列表
# 更改这里即可
keywords = ["市场", "金融", "数据分析"]  # 您可以根据实际需求添加更多关键词

# 构建一个文件夹来保存文章
crawl_texts_dir = "CrawlTexts"
if not os.path.exists(crawl_texts_dir):
    os.mkdir(crawl_texts_dir)
output_dir = os.path.join(crawl_texts_dir, "Dramx")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

# 遍历关键词列表
for keyword in keywords:
    keyword_dir = os.path.join(output_dir, keyword)
    if not os.path.exists(keyword_dir):
        os.mkdir(keyword_dir)

    # 对关键词进行URL编码
    encoded_keyword = quote(keyword)

    # 构建搜索链接
    search_url = f"https://www.dramx.com/Search/{encoded_keyword}/"

    print(f"搜索关键词 '{keyword}' 的文章：")
    page = 1

    while True:
        # 根据页数构建不同的分页链接格式
        if page == 1:
            page_url = search_url
            print(page_url)
        else:
            page_url = urljoin(search_url, f"{page}.html")
            print(page_url)

        # 发起HTTP请求
        response = requests.get(page_url)
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(response.content, "html.parser")

            # 在解析后的内容中查找含有关键词的文章链接
            es_result_div = soup.find("div", class_="ES-result")
            if es_result_div:
                article_div = es_result_div.find("div")  # 找到没有名字的内层div，存放真正的文章链接
                articles = article_div.find_all("a", string=lambda text: text != "查看更多")
                if articles:
                    for article in articles:
                        article_title = article.get_text()
                        article_link = article["href"]
                        full_article_link = urljoin(base_url, article_link)  # 构建完整的文章链接

                        print(f"标题：{article_title}")
                        print(f"链接：{full_article_link}")

                        # 下载文章内容并保存到本地txt文件
                        article_response = requests.get(full_article_link)
                        if article_response.status_code == 200:
                            article_content = article_response.text
                            plain_text_content = BeautifulSoup(article_content, "html.parser").get_text()
                            # 在这里处理文件名，清理非法字符
                            cleaned_article_title = re.sub(r'[^\w\s-]', '', article_title)
                            cleaned_article_title = re.sub(r'\s+', '-', cleaned_article_title).strip()

                            filename = os.path.join(keyword_dir, f"{cleaned_article_title}.txt")
                            with open(filename, "w", encoding="utf-8") as file:
                                file.write(f"标题：{article_title}\n")
                                file.write(f"链接：{full_article_link}\n")
                                file.write(plain_text_content)  # 保存纯文本内容
                            print(f"已保存到文件：{filename}")
                        else:
                            print(f"无法下载文章内容：{article_title}")

                        print("-" * 50)
                else:
                    print(f"未找到含有关键词 '{keyword}' 的文章")
                    break
            else:
                print(f"未找到ES-result div元素")
                break

            # 查找下一页的超链接
            jogger_div = es_result_div.find("div", class_="jogger")
            if jogger_div:
                next_page_link = jogger_div.find_all("a")[-1]  # 找到最后一个 a 标签
                next_page_url = urljoin(base_url, next_page_link["href"])
                page = int(re.search(r'/(\d+)\.html', next_page_url).group(1))  # 提取页数
            else:
                break
        else:
            print(f"无法连接到搜索链接：{page_url}")
            break
