import fasttext

# 訓練模型
model = fasttext.train_supervised(
    input="fasttext_train.txt",   # 之前轉出的資料檔
    epoch=35,                     # 訓練輪數
    lr=1.0,                       # 學習率
    wordNgrams=2,                 # 使用n-gram提升表達能力
    verbose=2,
    minCount=1,                   # 低頻詞的最小出現次數
    loss="softmax"                # 多分類任務常用的 loss
)

# 儲存模型
model.save_model("./classification/category_classifier.bin")
print("✅ 模型已儲存為 category_classifier.bin")
