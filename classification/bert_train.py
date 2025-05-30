from transformers import BertTokenizerFast, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, ClassLabel
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
import torch

# 1. 載入資料集
data_path = "./articles/training_data.csv" # 你的 CSV 檔
dataset = load_dataset('csv', data_files=data_path)

# 2. 標準化欄位名稱
dataset = dataset['train'].train_test_split(test_size=0.2, seed=42) # 切 80/20
label_names = ["賽事戰報", "球隊分析", "球員焦點", "交易與簽約", "教練與管理層", "選秀觀察", "歷史與專題"]

# 3. Tokenizer + encode
model_name = "bert-base-chinese"
tokenizer = BertTokenizerFast.from_pretrained(model_name)

def tokenize(example):
    return tokenizer(example['text'], padding="max_length", truncation=True, max_length=512)

encoded = dataset.map(tokenize, batched=True)
encoded = encoded.rename_column("label", "labels")
encoded.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# 4. 建立模型
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=7)

# 5. 訓練參數設定
args = TrainingArguments(
output_dir="./bert_output",
evaluation_strategy="epoch",
save_strategy="epoch",
logging_strategy="epoch",
learning_rate=2e-5,
per_device_train_batch_size=8,
per_device_eval_batch_size=8,
num_train_epochs=4,
weight_decay=0.01,
load_best_model_at_end=True,
metric_for_best_model="eval_loss",
)

# 6. 評估函式
def compute_metrics(eval_pred):
    preds, labels = eval_pred
    preds = np.argmax(preds, axis=1)
    report = classification_report(labels, preds, target_names=label_names, digits=4, output_dict=True)
    return {
    "accuracy": report["accuracy"],
    "f1_macro": report["macro avg"]["f1-score"],
    "precision_macro": report["macro avg"]["precision"],
    "recall_macro": report["macro avg"]["recall"],
    }

# 7. Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=encoded['train'],
    eval_dataset=encoded['test'],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# 8. 開始訓練
trainer.train()

# 9. 儲存模型
trainer.save_model("./bert_output/basketball-bert")
tokenizer.save_pretrained("./bert_output/basketball-bert")