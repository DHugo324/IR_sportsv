import os
import json
import torch
from transformers import BertTokenizerFast, BertForSequenceClassification

# 模型與路徑
MODEL_DIR = "./bert_output/basketball-bert"
INPUT_DIR = "./articles/unlabeled_articles"
OUTPUT_DIR = "./articles/predicted_articles"

# 類別標籤對應
label_map = {
    0: "賽事戰報",
    1: "球隊分析",
    2: "球員焦點",
    3: "交易與簽約",
    4: "教練與管理層",
    5: "選秀觀察",
    6: "歷史與專題"
}

# 載入模型與 tokenizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = BertTokenizerFast.from_pretrained(MODEL_DIR)
model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
model.to(device)
model.eval()

def predict(text):
    encoding = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    encoding = {k: v.to(device) for k, v in encoding.items()}
    with torch.no_grad():
        output = model(**encoding)
        pred = torch.argmax(output.logits, dim=1).item()
    return label_map[pred]

# 預測並輸出至新資料夾
os.makedirs(OUTPUT_DIR, exist_ok=True)
count = 0

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".json"):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        content = " ".join(data.get("article-content", []))
        if not content.strip():
            continue

        prediction = predict(content)
        data["predicted_category"] = prediction

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ {filename} → {prediction}")
        count += 1

    except Exception as e:
        print(f"❌ 錯誤處理 {filename}：{e}")
print(f"\n🎉 預測完成，共輸出 {count} 篇至：{OUTPUT_DIR}")