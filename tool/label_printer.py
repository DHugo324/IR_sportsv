import os
import json

ARTICLE_DIR = './articles/unlabeled_articles'
OUTPUT_FILE = 'labeled_summary.txt'

def generate_summary():
    grouped = {}
    uncategorized = []

    for fname in os.listdir(ARTICLE_DIR):
        if not fname.endswith('.json'):
            continue

        path = os.path.join(ARTICLE_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                title = data.get('title', '（無標題）')
                article_id = data.get('id', '無ID')
                display = f" - {title} ({article_id})"

                categories = data.get('category', [])
                if categories:
                    for cat in categories:
                        grouped.setdefault(cat, []).append(display)
                else:
                    uncategorized.append(display)

        except Exception as e:
            print(f"❌ 錯誤：無法讀取 {fname} - {e}")

    # 輸出結果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for cat, articles in grouped.items():
            out.write(f"{cat}（{len(articles)} 篇）:\n")
            for title in articles:
                out.write(f"{title}\n")
            out.write("\n")

        if uncategorized:
            out.write(f"未分類（{len(uncategorized)} 篇）:\n")
            for title in uncategorized:
                out.write(f"{title}\n")
            out.write("\n")

    print(f"✅ 已輸出到 {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_summary()
