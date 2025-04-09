import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

MAX_PAGES = 2
OUTPUT_FILE = "basketball_articles.json"
all_articles = []  # 儲存所有文章資料

def get_article_links(page_num):
    url = f'https://www.sportsv.net/basketball?page={page_num}#latest_articles'
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"  第 {page_num} 頁請求失敗：{e}")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.find_all('div', class_='col-md-7')

    links_with_dates = []
    for article in articles:
        h3_tag = article.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag and link_tag.get('href'):
                link = link_tag.get('href')
                if link.startswith('/'):
                    link = "https://www.sportsv.net" + link

                date_tag = article.find('div', class_='date')
                date = None
                if date_tag:
                    date_text = date_tag.text.strip()
                    date = date_text

                links_with_dates.append((link, date))

    return links_with_dates


def is_article_before_2020(date):
    if date:
        try:
            article_date = datetime.strptime(date, '%Y/%m/%d')
            return article_date.year > 2020
        except ValueError:
            return False
    return False


def get_article_content(url):
    full_content = ""
    title = ""
    author = ""
    tags = []
    article_id = ""

    match = re.search(r'/articles/(\d+)', url)
    if match:
        article_id = match.group(1)

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"  爬取 {url} 失敗：{e}")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')

    title_tag = soup.find('h1')
    if title_tag:
        title = title_tag.text.strip()

    author_tag = soup.find('div', class_='author_name')
    if author_tag and author_tag.find('a'):
        author = author_tag.find('a').text.strip()

    tag_list = soup.select('ul.tagcloud-list li a')
    tags = [tag.text.strip() for tag in tag_list]

    page_links = soup.select("a[href*='?page=']")
    max_page = 1
    for link in page_links:
        if 'page=' in link['href']:
            try:
                page_num = int(link['href'].split('page=')[-1].split('#')[0])
                max_page = max(max_page, page_num)
            except ValueError:
                continue

    for page in range(1, max_page + 1):
        page_url = url if page == 1 else f"{url}?page={page}#article_top"
        print(f"     爬取第 {page} 頁內文：{page_url}")

        try:
            res = requests.get(page_url, headers=HEADERS, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"     爬取 {page_url} 失敗：{e}")
            break

        soup = BeautifulSoup(res.text, 'html.parser')
        content_tags = soup.find_all("p")
        content = "\n".join(p.text.strip() for p in content_tags if p.text.strip())

        if not content:
            break

        full_content += content + "\n\n"

    return {
        "id": article_id,
        "topic": title,
        "author_name": author,
        "tags": tags,
        "article-content": full_content.strip() if full_content else None
    }


def save_articles_to_json(data_list, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_list, file, indent=4, ensure_ascii=False)


def main():
    global all_articles
    print(f"開始爬取 {MAX_PAGES} 頁的文章...")

    for i in range(1, MAX_PAGES + 1):
        print(f" 正在抓取第 {i} 頁文章連結...")

        links_with_dates = get_article_links(i)

        if not links_with_dates:
            print(f" 第 {i} 頁沒有找到文章，跳過。")
            continue

        for index, (url, date) in enumerate(links_with_dates, start=1):
            if is_article_before_2020(date):
                print(f" [{index}/{len(links_with_dates)}] 爬取中：{url} (日期：{date})")
                article_data = get_article_content(url)
                if article_data and article_data["article-content"]:
                    article_data["date"] = date  # 加入日期欄位
                    all_articles.append(article_data)
                    print(f"   完成：{url}")
                else:
                    print(f"   失敗：{url}")
            else:
                print(f"   跳過：{url} (日期：{date})")

    save_articles_to_json(all_articles, OUTPUT_FILE)
    print(f"✅ 所有符合條件的文章已存入 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
