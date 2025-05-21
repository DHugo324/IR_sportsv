import os
import json
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer, util
import torch

# 1. 載入模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 2. 讀取所有文章（原始資料）
folder_path = "articles/predicted_articles"
articles = {}
corpus_embeddings = []
article_ids = []
article_dates = {}

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        article_id = data["id"]
        title = data["title"]
        tags = " ".join(data.get("tags", []))
        body = "".join(data["article-content"])
        full_text = title + "。" + tags + "。" + body

        date_str = data["date"]
        date_obj = datetime.strptime(date_str, "%Y/%m/%d")
        article_dates[article_id] = date_obj

        embedding = model.encode(full_text, convert_to_tensor=True, normalize_embeddings=True)

        articles[article_id] = full_text
        corpus_embeddings.append(embedding)
        article_ids.append(article_id)

# 3. 讀取查詢文章
target_id = "118870"
target_file_path = os.path.join(folder_path, f"{target_id}.json")

with open(target_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

target_date = datetime.strptime(data["date"], "%Y/%m/%d")
target_text = data["title"] + "。" + " ".join(data.get("tags", [])) + "。" + "".join(data["article-content"])

# 4. 建立查詢文章 embedding
target_embedding = model.encode(target_text, convert_to_tensor=True, normalize_embeddings=True)

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
if not filtered_embeddings:
    print("⚠️ 沒有在 ±10 天內的其他文章可供比較。")
else:
    filtered_tensor = torch.stack(filtered_embeddings)
    cos_scores = util.cos_sim(target_embedding, filtered_tensor)[0]

    # 7. 找出前3篇最相似
    top_results = sorted(list(enumerate(cos_scores)), key=lambda x: x[1], reverse=True)

    print(f"🔍 和文章 {target_id} 最相似的3篇文章（限定 ±10 天內）：\n")
    for idx, score in top_results[:3]:
        similar_id = filtered_ids[idx]
        print(f"📄 文章 ID：{similar_id}, 相似度：{score:.4f}")
        print(f"➡️ 文章片段：{articles[similar_id][:50]}...\n")
