import os
import json
import random
import tkinter as tk
from tkinter import messagebox

ARTICLE_DIR = './articles'
TAGS = [
    "預測分析",
    "賽事戰報",
    "球隊分析",
    "人事異動",
    "歷史回顧",
    "未來展望"
]

class LabelingApp:
    def __init__(self, master):
        self.master = master
        master.title("文章標註工具")

        self.all_files = [f for f in os.listdir(ARTICLE_DIR) if f.endswith('.json')]
        self.files = self.all_files.copy()
        random.shuffle(self.files)
        self.current_file = None
        self.article_data = None

        # ➤ 顯示文章標題與 ID
        self.meta_label = tk.Label(master, text="", font=("Arial", 12, "bold"), anchor='w', justify='left')
        self.meta_label.pack(padx=10, pady=(10, 0), anchor='w')

        # ➤ 顯示已標記/總數狀態
        self.status_label = tk.Label(master, text="", font=("Arial", 10), anchor='w', justify='left')
        self.status_label.pack(padx=10, pady=(0, 10), anchor='w')

        self.text = tk.Text(master, wrap=tk.WORD, height=25, width=80)
        self.text.pack(padx=10, pady=(5, 10))

        self.check_vars = [tk.BooleanVar() for _ in TAGS]
        TAG_DESCRIPTIONS = {
            "預測分析": "賽事預測、交易預測",
            "賽事戰報": "季前賽、例行賽、附加賽、季後賽",
            "球隊分析": "球隊未來可能交易、薪資空間",
            "人事異動": "球員選秀籤交易、教練/管理層",
            "歷史回顧": "球員回顧、歷史故事",
            "未來展望": "球員潛在買家、球隊未來"
        }

        for i, tag in enumerate(TAGS):
            description = TAG_DESCRIPTIONS.get(tag, "")
            cb_text = f"{tag}（{description}）"
            cb = tk.Checkbutton(master, text=cb_text, variable=self.check_vars[i], wraplength=600, justify='left')
            cb.pack(anchor='w', padx=20)


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
                self.meta_label.config(text=f"ID：{article_id}\n標題：{title}")

                content = "\n\n".join(data.get('article-content', []))
                self.text.insert(tk.END, content)

                for var in self.check_vars:
                    var.set(False)
                return

        messagebox.showinfo("完成！", "所有文章都已標註完畢！")
        self.master.quit()

    def submit(self):
        selected_tags = [TAGS[i] for i, var in enumerate(self.check_vars) if var.get()]
        if not selected_tags:
            # ➤ 沒有標籤就略過，不儲存，直接跳下一篇
            self.load_next_article()
            return

        self.article_data.setdefault("category", []).extend(selected_tags)
        self.article_data["category"] = list(set(self.article_data["category"]))

        path = os.path.join(ARTICLE_DIR, self.current_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.article_data, f, ensure_ascii=False, indent=2)

        self.load_next_article()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()
