import os
import json
from datetime import datetime
from article_crawler import get_article_soup, get_article_id, get_article_content

while True:
    START_PAGES = int(input("請輸入爬取起始頁數："))  # 爬取的起始頁數
    END_PAGES = int(input("請輸入爬取結束頁數："))  # 爬取的結束頁數
    if START_PAGES > END_PAGES:
        print("起始頁數必須小於或等於結束頁數，請重新輸入。")
    else:
        break
OUTPUT_DIR = "../articles"  # 儲存資料的資料夾

def get_basketball_article_ids(page_num): # 爬取籃球專區的文章ID
    url = f'https://www.sportsv.net/basketball?page={page_num}#latest_articles'
    soup = get_article_soup(url) # 獲取頁面內容
    if soup is None:
        print(f"  第 {page_num} 頁請求失敗")
        return []
    latest_articles_section = soup.find('section', id='latest_articles')
    if latest_articles_section is None:
        print(f"  第 {page_num} 頁未找到最新文章區域")
        return []
    articles = latest_articles_section.find_all('div', class_='col-md-7')
    ids = [] # 儲存文章id
    for article in articles:
        h3_tag = article.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag and link_tag.get('href'):
                link = link_tag.get('href')
                id = get_article_id(link) # 文章ID
                # if link.startswith('/'):
                #     link = "https://www.sportsv.net" + link
                ids.append(id)

    return ids

def get_basketball_article_links(page_num): # 爬取籃球專區的文章連結
    url = f'https://www.sportsv.net/basketball?page={page_num}#latest_articles'
    soup = get_article_soup(url)
    if soup is None:
        print(f"  第 {page_num} 頁請求失敗")
        return []
    latest_articles_section = soup.find('section', id='latest_articles')
    if latest_articles_section is None:
        print(f"  第 {page_num} 頁未找到最新文章區域")
        return []
    articles = latest_articles_section.find_all('div', class_='col-md-7')
    links = []
    for article in articles:
        h3_tag = article.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag and link_tag.get('href'):
                link = link_tag.get('href')
                if link.startswith('/'):
                    link = "https://www.sportsv.net" + link
                links.append(link)
    return links

def save_article_to_json(article_data):
    article_id = article_data.get("id") or get_article_id(article_data.get("url", "unknown"))
    base_dir = os.path.join(os.path.dirname(__file__), OUTPUT_DIR)
    os.makedirs(base_dir, exist_ok=True)
    filename = f"{article_id}.json"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(article_data, file, indent=4, ensure_ascii=False)

def check_article_exists(article_id): # 檢查文章是否已存在
    base_dir = os.path.join(os.path.dirname(__file__), OUTPUT_DIR)
    filename = f"{article_id}.json"
    filepath = os.path.join(base_dir, filename)
    return os.path.exists(filepath)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)  # 如果資料夾不存在則創建
    print(f"✅ 開始爬取籃球專區最新文章...")
    print(f"  爬取頁數範圍：{START_PAGES} ~ {END_PAGES}")
    print(f"  儲存資料夾：{OUTPUT_DIR}")

    for i in range(START_PAGES, END_PAGES + 1):
        print(f" 正在抓取第 {i} 頁文章連結...")
        links = get_basketball_article_links(i)
        if not links:
            print(f" 第 {i} 頁沒有找到文章，跳過。")
            continue
        for index, url in enumerate(links, start=1):
            id = get_article_id(url)
            if check_article_exists(id):
                print(f"   ❌ 已存在文章ID：{id}")
                continue
            print(f" [{index}/{len(links)}] 爬取中：{url}")
            article_data = get_article_content(url)
            if article_data and article_data.get("article-content"):
                save_article_to_json(article_data)
                print(f"   ✅ 完成並儲存：{url}")
            else:
                print(f"   ❌ 失敗：{url}")

    print(f"✅ 所有符合條件的文章已儲存至資料夾 {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
