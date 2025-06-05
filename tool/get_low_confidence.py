import os
import json
from collections import defaultdict
import move_file

SOURCE_DIR = './articles/predicted_articles'
OUTPUT_DIR = './articles/to_label'
N = 20  # 每類別選幾篇信心值最低的

os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_CATEGORIES = [
    "賽事戰報",
    "球隊分析",
    "球員焦點",
    "交易與簽約",
    "教練與管理層",
    "選秀觀察",
    "歷史與專題"
]

category_buckets = defaultdict(list)

# 讀取所有預測資料並分類
for filename in os.listdir(SOURCE_DIR):
    if not filename.endswith('.json'):
        continue
    path = os.path.join(SOURCE_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cat = data.get("predicted_category")
            conf = data.get("confidence")
            if cat in TARGET_CATEGORIES and isinstance(conf, float):
                category_buckets[cat].append((conf, filename, data))
    except Exception as e:
        print(f"⚠️ 讀取失敗 {filename}：{e}")

# 對每類挑最低信心值的 N 篇
print("\n📉 挑選信心值最低的文章供人工標註：")
for cat in TARGET_CATEGORIES:
    articles = sorted(category_buckets.get(cat, []), key=lambda x: x[0])  # 由小到大排序
    selected = articles[:N]

    print(f"\n--- 分類：{cat}（共 {len(articles)} 篇）---")
    for conf, filename, data in selected:
        article_id = data.get("id", "未知ID")
        print(f" - {article_id}（confidence={conf:.4f}）")

        # 修改格式
        data["category"] = [cat]
        data.pop("predicted_category", None)
        data.pop("confidence", None)

        # 輸出
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.remove(SOURCE_DIR + '/' + filename)  # 刪除原始檔案
        print(f"   🔗 原始檔案已刪除：{SOURCE_DIR}/{filename}")

print("\n✅ 所有低信心文章已輸出完成")
