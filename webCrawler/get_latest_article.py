import json
from article_crawler import get_article_soup, get_article_id, get_article_content

MAX_PAGES = 2 # 爬取的頁數
OUTPUT_FILE = "basketball_articles.json" # 儲存的檔案名稱
all_articles = []  # 儲存所有文章資料

def get_basketball_article_id_from_page(page_num): # 爬取籃球專區的文章ID
    url = f'https://www.sportsv.net/basketball?page={page_num}#latest_articles'
    soup = get_article_soup(url) # 獲取頁面內容
    if soup is None:
        print(f"  第 {page_num} 頁請求失敗")
        return []
    latest_articles_section = soup.find('section', id='latest_articles')
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
    soup = get_article_soup(url) # 獲取頁面內容
    if soup is None:
        print(f"  第 {page_num} 頁請求失敗")
        return []
    latest_articles_section = soup.find('section', id='latest_articles')
    articles = latest_articles_section.find_all('div', class_='col-md-7')

    links = [] # 儲存文章網址和日期
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

def save_articles_to_json(data_list, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_list, file, indent=4, ensure_ascii=False)

def main():
    global all_articles
    print(f"開始爬取 {MAX_PAGES} 頁的文章...")

    for i in range(1, MAX_PAGES + 1):
        print(f" 正在抓取第 {i} 頁文章連結...")

        links = get_basketball_article_links(i)

        if not links:
            print(f" 第 {i} 頁沒有找到文章，跳過。")
            continue

        for index, url in enumerate(links, start=1):
                print(f" [{index}/{len(links)}] 爬取中：{url})")
                article_data = get_article_content(url)
                if article_data and article_data["article-content"]:
                    all_articles.append(article_data)
                    print(f"   完成：{url}")
                else:
                    print(f"   失敗：{url}")

    save_articles_to_json(all_articles, OUTPUT_FILE)
    print(f"✅ 所有符合條件的文章已存入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
