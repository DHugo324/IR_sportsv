import pandas as pd

# 讀取 CSV 檔案
df = pd.read_csv("classification/bert/predict_summary.csv")

# 定義固定的類別順序（可依需求調整）
category_order = ["球員焦點", "賽事戰報", "球隊分析", "交易與簽約", "歷史與專題", "選秀觀察", "教練與管理層"]

# 計算每個類別的文章數量並按照順序排序
category_counts = df["predicted_category"].value_counts().reindex(category_order, fill_value=0)

# 印出所有類別的文章數量
print("各類別文章數量：")
for category, count in category_counts.items():
    print(f"{category} {count}篇")

print("-" * 30)  # 分隔線

# 定義級距
bins = [0, 0.4, 0.5, 0.6, 0.7, 0.8,  1]
labels = ["<0.4", "0.4-0.5", "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-1"]

# 依照 `confidence` 欄位分組
df["confidence_range"] = pd.cut(df["confidence"], bins=bins, labels=labels, right=False)

# 依級距與 `predicted_category` 分組，計算各類別文章數
category_counts_by_range = df.groupby(["confidence_range", "predicted_category"]).size().reset_index(name="count")

# 依照級距輸出各類別文章數量，並按照固定的類別順序排列
for range_label in labels:
    print(range_label)
    subset = category_counts_by_range[category_counts_by_range["confidence_range"] == range_label]
    
    # 根據類別順序輸出結果
    for category in category_order:
        row = subset[subset["predicted_category"] == category]
        count = row["count"].values[0] if not row.empty else 0
        print(f"{category} {count}篇")
    
    print("-" * 30)  # 分隔線
