import pandas as pd
import json
import os

# 設定 JSON 檔案所在的資料夾
json_folder = "articles\predicted_articles"

# 創建一個空的列表來存儲篩選後的 JSON 數據
data_list = []

# 讀取所有 JSON 檔案
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        with open(os.path.join(json_folder, filename), "r", encoding="utf-8") as file:
            data = json.load(file)
            filtered_data = {
                "id": data["id"],
                "title": data["title"],
                "predicted_category": data["predicted_category"],
                "confidence": data["confidence"]
            }
            data_list.append(filtered_data)

# 轉換為 DataFrame
df = pd.DataFrame(data_list)

# 將 DataFrame 儲存為 CSV 檔案
df.to_csv("./classification/predict_summary.csv", index=False, encoding="utf-8-sig")

print("CSV 檔案已成功儲存！")
