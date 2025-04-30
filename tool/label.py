import os
import json
import random
import tkinter as tk
from tkinter import messagebox

ARTICLE_DIR = './articles/unlabeled_articles'  # 未標記的 JSON 檔資料夾
OUTPUT_DIR = './articles/training_articles'  # 標記後輸出的資料夾
TAGS = [
    "賽事戰報",
    "球隊分析",
    "球員焦點",
    "人事異動",
    "歷史回顧"
]

TAG_DESCRIPTIONS = {
    "賽事戰報": "各類賽事及時賽後報導、分析",
    "球隊分析": "球隊表現預測、球隊近況、球隊未來展望、薪資空間",
    "球員焦點": "球員潛在買家、球員表現分析",
    "人事異動": "球員選秀籤交易、教練/管理層",
    "歷史回顧": "球員回顧、歷史故事、經典賽事回顧"
}

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

        self.load_next_article()

    def update_status_label(self):
        labeled_count = 0
        for f in self.all_files:
            path = os.path.join(ARTICLE_DIR, f)
            with open(path, 'r', encoding='utf-8') as fp:
                try:
                    data = json.load(fp)
                    if data.get("category"):
                        labeled_count += 1
                except json.JSONDecodeError:
                    continue
        total = len(self.all_files)
        self.status_label.config(text=f"已標記 {labeled_count} / {total} 篇")

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

        self.load_next_article()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()
