import os
import json
import pandas as pd

# 設定資料夾路徑
INPUT_DIR = './articles/training_articles'
OUTPUT_CSV = './articles/training_data.csv'

# 類別標籤對應表
label_map = {
    "賽事戰報": 0,
    "球隊分析": 1,
    "球員焦點": 2,
    "交易與簽約": 3,
    "教練與管理層": 4,
    "選秀觀察": 5,
    "歷史與專題": 6
}

data = []

for filename in os.listdir(INPUT_DIR):
    if filename.endswith('.json'):
        path = os.path.join(INPUT_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                article = json.load(f)
                content = article.get("article-content", [])
                title = article.get("title", "").strip()  # 取得標題
                content = article.get("article-content", [])
                text = " ".join(content)  
                # text = f"{title} " + " ".join(content) # 合併內容

                categories = article.get("category", [])
                if not categories:
                    continue  # 跳過未標記的

                # 假設每篇文章只有一個標籤
                main_cat = categories[0]
                if main_cat not in label_map:
                    continue  # 非法標籤

                label = label_map[main_cat]
                data.append({"text": text.strip(), "label": label})

        except Exception as e:
            print(f"❗ 無法處理 {filename}: {e}")

# 建立資料表並存成 CSV
df = pd.DataFrame(data)
df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"✅ 已轉換 {len(df)} 筆資料並輸出至 {OUTPUT_CSV}")
