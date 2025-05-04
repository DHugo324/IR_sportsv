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
OUTPUT_DIR = "../articles/unlabeled_articles"  # 儲存資料的資料夾
ARTICLE_DIR = "../articles"
ID_LIST_FILE = "article_id_list.txt"  # 儲存文章ID的檔案名稱
def get_basketball_article_ids(page_num): # 爬取籃球專區的文章ID
    url = f'https://www.sportsv.net/basketball/nba?page={page_num}#latest_articles'
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
    url = f'https://www.sportsv.net/basketball/nba?page={page_num}#latest_articles'
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
    base_dir = os.path.join(os.path.dirname(__file__), ARTICLE_DIR)
    txt_filepath = os.path.join(base_dir, ID_LIST_FILE)
    # 確保 article_id 是字串，以進行比較
    article_id_str = str(article_id)
    # 檢查檔案是否存在
    if not os.path.exists(txt_filepath):
        print(f"警告：列表檔案 {txt_filepath} 不存在，視為 article_id 不存在。")
        return False
    try:
        # 打開檔案並逐行讀取
        with open(txt_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                # 去除行尾的換行符和可能的空白
                if line.strip() == article_id_str:
                    return True # 找到匹配項，返回 True
        # 遍歷完所有行都沒找到
        return False
    except Exception as e:
        print(f"讀取檔案 {txt_filepath} 時發生錯誤: {e}")
        return False # 讀取錯誤，視為 article_id 不存在

def add_article_id_to_list_file(article_id):
    article_id_str = str(article_id)
    if check_article_exists(article_id_str):
        # print(f"Article ID '{article_id_str}' 已存在於列表檔案中，無需重複添加。") # 可以選擇是否印出提示
        return # ID 已存在，直接返回
    # --- 如果 ID 不存在，則添加到檔案末尾 ---
    base_dir = os.path.join(os.path.dirname(__file__), ARTICLE_DIR)
    txt_filepath = os.path.join(base_dir, ID_LIST_FILE)
    # 確保目標目錄存在
    os.makedirs(base_dir, exist_ok=True)
    try:
        with open(txt_filepath, 'a', encoding='utf-8') as f:
            f.write(article_id_str + '\n') # 寫入 ID，並換行以便下一條記錄
        # print(f"Article ID '{article_id_str}' 已成功添加到列表檔案 {txt_filepath}。")

    except Exception as e:
        print(f"添加 Article ID '{article_id_str}' 到檔案 {txt_filepath} 時發生錯誤: {e}")

def main():
    base_dir = os.path.join(os.path.dirname(__file__), OUTPUT_DIR)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"✅ 資料夾 {base_dir} 不存在，已自動創建。")
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
                add_article_id_to_list_file(id)
                print(f"   ✅ 完成並儲存：{url}")
            else:
                print(f"   ❌ 失敗：{url}")

    print(f"✅ 所有符合條件的文章已儲存至資料夾 {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
