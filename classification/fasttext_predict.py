import os
import json
import fasttext

INPUT_DIR = "./articles/unlabeled_articles"  # 未分類的 JSON 檔資料夾
OUTPUT_DIR = "./articles/predicted_articles"  # 預測後輸出的資料夾
MODEL_PATH = "./classification/category_classifier.bin"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 載入 FastText 模型
model = fasttext.load_model(MODEL_PATH)
print("✅ 模型已載入")

def predict_category(text):
    labels, probs = model.predict(text, k=1)
    return labels[0].replace("__label__", ""), probs[0]

def process_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 如果已經有 category，跳過
    if "category" in data:
        return

    content_list = data.get("article-content", [])
    full_text = " ".join(content_list).strip()
    if not full_text:
        return

    predicted_label, confidence = predict_category(full_text)

    data["predicted_category"] = predicted_label
    data["prediction_confidence"] = confidence

    filename = os.path.basename(filepath)
    out_path = os.path.join(OUTPUT_DIR, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    article_id = data.get("id", "unknown")
    title = data.get("title", "無標題")
    print(f"🔍 {article_id}《{title}》 → {predicted_label}（信心值：{confidence:.4f}）")

# 批次處理資料夾
files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
print(f"📁 發現 {len(files)} 個檔案，開始分類...\n")

for file in files:
    path = os.path.join(INPUT_DIR, file)
    process_json_file(path)

print("\n✅ 所有未分類文章已預測並儲存於：", OUTPUT_DIR)
