import os
import json
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer, util
import torch

# 1. 載入中文 SBERT 模型
model = SentenceTransformer('shibing624/text2vec-base-chinese')

# 2. 讀取所有文章（原始資料）
folder_path = "articles/predicted_articles"
articles = {}
corpus_embeddings = []
article_ids = []
article_dates = {}  # 儲存每篇文章的日期

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        article_id = data["id"]
        title = data["title"]
        tags = " ".join(data.get("tags", []))
        body = "".join(data["article-content"])
        date_str = data["date"]
        date_obj = datetime.strptime(date_str, "%Y/%m/%d")
        article_dates[article_id] = date_obj

        # 各自計算 embedding 再平均（標題、tag、內文）
        title_emb = model.encode(title, convert_to_tensor=True, normalize_embeddings=True)
        tag_emb = model.encode(tags, convert_to_tensor=True, normalize_embeddings=True)
        body_emb = model.encode(body, convert_to_tensor=True, normalize_embeddings=True)
        combined_emb = (title_emb + tag_emb + body_emb) / 3

        articles[article_id] = title + "。" + tags + "。" + body
        corpus_embeddings.append(combined_emb)
        article_ids.append(article_id)

# 3. 指定查詢文章 ID
target_id = "118870"
target_title = ""
target_tags = ""
target_body = ""
target_date = None

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data["id"] == target_id:
            target_title = data["title"]
            target_tags = " ".join(data.get("tags", []))
            target_body = "".join(data["article-content"])
            target_date = datetime.strptime(data["date"], "%Y/%m/%d")
            break

# 4. 建立查詢文章 embedding（標題 + tag + 內文平均）
target_title_emb = model.encode(target_title, convert_to_tensor=True, normalize_embeddings=True)
target_tag_emb = model.encode(target_tags, convert_to_tensor=True, normalize_embeddings=True)
target_body_emb = model.encode(target_body, convert_to_tensor=True, normalize_embeddings=True)
target_embedding = (target_title_emb + target_tag_emb + target_body_emb) / 3

# 5. 過濾日期 ±10 天內的文章
start_date = target_date - timedelta(days=10)
end_date = target_date + timedelta(days=10)

filtered_embeddings = []
filtered_ids = []

for i, aid in enumerate(article_ids):
    if aid == target_id:
        continue
    article_date = article_dates[aid]
    if start_date <= article_date <= end_date:
        filtered_embeddings.append(corpus_embeddings[i])
        filtered_ids.append(aid)

# 6. 計算相似度（cosine similarity）
filtered_tensor = torch.stack(filtered_embeddings)
cos_scores = util.cos_sim(target_embedding, filtered_tensor)[0]

# 7. 找出前3篇最相似
top_results = sorted(list(enumerate(cos_scores)), key=lambda x: x[1], reverse=True)

print(f"🔍 和文章 {target_id} 最相似的3篇文章（限定 ±10 天內）：\n")
count = 0
for idx, score in top_results:
    similar_id = filtered_ids[idx]
    print(f"📄 文章 ID：{similar_id}, 相似度：{score:.4f}")
    print(f"➡️ 文章標題：{articles[similar_id][:50]}...\n")
    count += 1
    if count == 3:
        break