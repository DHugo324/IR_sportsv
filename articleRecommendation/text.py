import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 設定 User-Agent，避免被網站封鎖
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# 設定要爬取的最大頁數
MAX_PAGES = 2
OUTPUT_FILE = "basketball_text.txt"

def get_article_links(page_num):
    """ 爬取指定頁數的文章連結及發佈日期 """
    url = f'https://www.sportsv.net/basketball?page={page_num}#latest_articles'
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"  第 {page_num} 頁請求失敗：{e}")
        return []  # 返回空列表

    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.find_all('div', class_='col-md-7')

    links_with_dates = []
    for article in articles:
        # 抓取文章連結
        h3_tag = article.find('h3')  # 找 h3
        if h3_tag:
            link_tag = h3_tag.find('a')  # 找 a
            if link_tag and link_tag.get('href'):
                link = link_tag.get('href')
                if link.startswith('/'):  # 確保只加入完整網址
                    link = "https://www.sportsv.net" + link
                
                # 抓取文章的發佈日期
                date_tag = article.find('div', class_='date')  # 找到 <div class="date">2025/04/03</div>
                date = None
                if date_tag:
                    date_text = date_tag.text.strip()
                    date = date_text  # 直接存成字串
                
                links_with_dates.append((link, date))
    
    return links_with_dates


def is_article_before_2020(date):
    """ 檢查文章日期是否在 2020 年之前 """
    if date:
        try:
            article_date = datetime.strptime(date, '%Y/%m/%d')  # 解析 YYYY/MM/DD 格式
            return article_date.year > 2020
        except ValueError:
            return False
    return False


def get_article_content(base_url):
    """ 爬取文章內文（包含多頁） """
    full_content = ""
    
    # 先找到該文章的最大頁數
    try:
        res = requests.get(base_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"  爬取 {base_url} 失敗：{e}")
        return None
    
    soup = BeautifulSoup(res.text, 'html.parser')

    # 找到所有頁碼
    page_links = soup.select("a[href*='?page=']")
    max_page = 1  # 預設只有 1 頁
    for link in page_links:
        if 'page=' in link['href']:
            try:
                page_num = int(link['href'].split('page=')[-1].split('#')[0])  # 抓出頁碼數字
                max_page = max(max_page, page_num)  # 取最大頁數
            except ValueError:
                continue

    # 依序爬取所有頁數
    for page in range(1, max_page + 1):
        page_url = base_url if page == 1 else f"{base_url}?page={page}#article_top"
        print(f"     爬取第 {page} 頁內文：{page_url}")

        try:
            res = requests.get(page_url, headers=HEADERS, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"     爬取 {page_url} 失敗：{e}")
            break  # 如果請求失敗，結束該文章的爬取

        soup = BeautifulSoup(res.text, 'html.parser')

        # 抓取內文
        content_tags = soup.find_all("p")
        content = "\n".join(p.text.strip() for p in content_tags if p.text.strip())

        if not content:
            break  # 如果該頁沒有內文，停止抓取

        full_content += content + "\n\n"

    return full_content if full_content else None


def save_article_content(content):
    """ 將文章內文儲存到檔案 """
    with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
        file.write(content + "\n\n" + "="*80 + "\n\n")  # 分隔不同文章


def main():
    # 清空舊的內容
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

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
                content = get_article_content(url)
                if content:
                    save_article_content(content)
                    print(f"   完成：{url}")
                else:
                    print(f"   失敗：{url}")
            else:
                print(f"   跳過：{url} (日期：{date})")

    print(f"✅ 所有符合條件的文章內文已存入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
