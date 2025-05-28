import os
import json
import random
import tkinter as tk
from tkinter import messagebox
import move_file

ARTICLE_DIR = './articles/unlabeled_articles'  # 未標記的 JSON 檔資料夾
OUTPUT_DIR = './articles/training_articles'  # 標記後輸出的資料夾
TAGS = [
    "賽事戰報",
    "球隊分析",
    "球員焦點",
    "交易與簽約",
    "教練與管理層",
    "選秀觀察",
    "歷史與專題"
]

TAG_DESCRIPTIONS = {
    "賽事戰報": "各類賽事及時賽後報導、賽前分析",
    "球隊分析": "球隊表現預測、球隊近況、球隊未來展望、薪資空間", # 若文章以球隊為主角、討論補強方向與名單
    "球員焦點": "球員潛力預測、球員表現分析、個人評析", # 若文章以球員為主角、分析其潛在買家
    "交易與簽約": "自由市場球員簽約、球員選秀籤交易", # 已完成的交易與簽約
    "教練與管理層": "教練/管理層變動，教練評析",
    "選秀觀察": "選秀分析、球隊選秀預測",
    "歷史與專題": "歷史回顧、人物專訪、經典賽事回顧、特殊專題"
}
for i in TAG_DESCRIPTIONS:
    print(f"{i}：{TAG_DESCRIPTIONS[i]}")
class LabelingApp:
    def __init__(self, master):
        self.master = master
        master.title("文章標註工具")

        self.all_files = [f for f in os.listdir(ARTICLE_DIR) if f.endswith('.json')]
        self.files = self.all_files.copy()
        random.shuffle(self.files)
        self.current_file = None
        self.article_data = None

        # 顯示文章標題與 ID
        self.meta_label = tk.Label(master, text="", font=("Arial", 12, "bold"), anchor='w', justify='left')
        self.meta_label.pack(padx=10, pady=(10, 0), anchor='w')

        # 顯示已標記/總數狀態
        self.status_label = tk.Label(master, text="", font=("Arial", 10), anchor='w', justify='left')
        self.status_label.pack(padx=10, pady=(0, 10), anchor='w')

        self.text = tk.Text(master, wrap=tk.WORD, height=25, width=80)
        self.text.pack(padx=10, pady=(5, 10))

        self.selected_tag = tk.StringVar(value="")

        for tag in TAGS:
            description = TAG_DESCRIPTIONS.get(tag, "")
            rb_text = f"{tag}（{description}）"
            rb = tk.Radiobutton(master, text=rb_text, variable=self.selected_tag, value=tag,
                                wraplength=600, justify='left')
            rb.pack(anchor='w', padx=20)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.submit_button = tk.Button(self.button_frame, text="送出", command=self.submit)
        self.submit_button.grid(row=0, column=0, padx=10)

        self.skip_button = tk.Button(self.button_frame, text="略過", command=self.load_next_article)
        self.skip_button.grid(row=0, column=1, padx=10)
        self.print_label_statistics()  # 印出統計

        self.load_next_article()

    def update_status_label(self):
        labeled_count = 0
        total_count = len(self.all_files)  # 原始總數（未標記文章）

        # **計算已標記的文章數量**
        for f in os.listdir(OUTPUT_DIR):  # 改為遍歷 `training_articles`
            path = os.path.join(OUTPUT_DIR, f)
            if os.path.isfile(path) and f.endswith('.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        if data.get("category"):  # 確保有標記
                            labeled_count += 1
                except json.JSONDecodeError:
                    print(f"警告：無法解析 {f}，跳過！")

        # **更新 UI**
        self.status_label.config(text=f"已標記 {labeled_count} / {total_count} 篇")


    def load_next_article(self):
        self.update_status_label()
        while self.files:
            filename = self.files.pop()
            path = os.path.join(ARTICLE_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not data.get("category"):
                self.current_file = filename
                self.article_data = data
                self.text.delete('1.0', tk.END)

                title = data.get("title", "（無標題）")
                article_id = data.get("id", "（無 ID）")
                print(f"正在標記🔍 {article_id}《{title}》")
                self.meta_label.config(text=f"ID：{article_id}\n標題：{title}")

                content = "\n\n".join(data.get('article-content', []))
                self.text.insert(tk.END, content)

                self.selected_tag.set(None)  # 清空選擇
                return

        messagebox.showinfo("完成！", "所有文章都已標註完畢！")
        self.master.quit()

    def submit(self):
        selected_tag = self.selected_tag.get()
        if not selected_tag:
            self.load_next_article()
            return

        self.article_data.setdefault("category", []).append(selected_tag)
        self.article_data["category"] = list(set(self.article_data["category"]))

        path = os.path.join(ARTICLE_DIR, self.current_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.article_data, f, ensure_ascii=False, indent=2)
        print(f"已標記為 {selected_tag}", end="")
        move_file.move_json_file(self.current_file, ARTICLE_DIR, OUTPUT_DIR)  # 移動檔案到 training_articles 資料夾
        self.load_next_article()
    
    def print_label_statistics(self):
        tag_counts = {tag: 0 for tag in TAGS}
        others = 0

        print("\n📊 目前各分類數量：")

        # **遍歷 training_articles 資料夾**
        for f in os.listdir(OUTPUT_DIR):
            path = os.path.join(OUTPUT_DIR, f)
            
            if os.path.isfile(path) and f.endswith('.json'):  # 確保是 JSON 檔案
                try:
                    with open(path, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        categories = data.get("category", [])
                        
                        for cat in categories:
                            if cat in tag_counts:
                                tag_counts[cat] += 1
                            else:
                                others += 1
                except Exception as e:
                    print(f"⚠️ 讀取 {f} 時發生錯誤：{e}")

        # **印出各分類統計**
        for tag, count in tag_counts.items():
            print(f"{tag}：{count} 篇")
        
        if others:
            print(f"（其他未定義標籤：{others} 篇）")

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()
