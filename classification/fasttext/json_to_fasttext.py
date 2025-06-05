import os
import json

INPUT_DIR = "./articles/training_articles"  # 你放json檔的資料夾
OUTPUT_FILE = "./classification/fasttext_train.txt"  # FastText訓練輸出檔

def json_to_fasttext_line(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ 無法解析 JSON 檔案：{json_path}")
            return None
    
    # 只轉換有標記 category 的資料
    if "category" not in data or not data["category"]:
        return None

    label = data["category"][0]  # 只取第一個分類標籤
    content_list = data.get("article-content", [])
    content = " ".join(content_list).replace("\n", " ").strip()

    if not content:
        return None

    return f"__label__{label} {content}"

def convert_all_json(input_dir, output_file):
    with open(output_file, "w", encoding="utf-8") as out_f:
        for filename in os.listdir(input_dir):
            if filename.endswith(".json"):
                path = os.path.join(input_dir, filename)
                line = json_to_fasttext_line(path)
                if line:
                    out_f.write(line + "\n")
    print(f"✅ 轉換完成，結果儲存於：{output_file}")

if __name__ == "__main__":
    convert_all_json(INPUT_DIR, OUTPUT_FILE)
