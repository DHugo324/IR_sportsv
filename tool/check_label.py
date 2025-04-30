import os
import json
import tkinter as tk
from tkinter import messagebox

ARTICLE_DIR = './articles/training_articles'
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

class ReviewApp:
    def __init__(self, master):
        self.master = master
        master.title("標註文章檢查與修改工具")

        self.files = [
            f for f in os.listdir(ARTICLE_DIR)
            if f.endswith('.json') and self._has_category(f)
        ]
        self.index = 0
        self.current_file = None
        self.article_data = None

        self.meta_label = tk.Label(master, text="", font=("Arial", 12, "bold"), anchor='w', justify='left')
        self.meta_label.pack(padx=10, pady=(10, 0), anchor='w')

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

        self.save_button = tk.Button(self.button_frame, text="儲存修改", command=self.save_changes)
        self.save_button.grid(row=0, column=0, padx=10)

        self.next_button = tk.Button(self.button_frame, text="下一篇", command=self.load_next)
        self.next_button.grid(row=0, column=1, padx=10)

        self.load_next()

    def _has_category(self, filename):
        path = os.path.join(ARTICLE_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return bool(data.get("category"))
        except:
            return False

    def load_next(self):
        if self.index >= len(self.files):
            messagebox.showinfo("完成", "已檢查完所有已標註文章。")
            self.master.quit()
            return

        filename = self.files[self.index]
        self.index += 1
        self.current_file = filename

        path = os.path.join(ARTICLE_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            self.article_data = json.load(f)

        title = self.article_data.get("title", "（無標題）")
        article_id = self.article_data.get("id", "（無 ID）")
        current_tags = ", ".join(self.article_data.get("category", []))
        self.meta_label.config(text=f"ID：{article_id}\n標題：{title}\n目前標籤：{current_tags}")

        content = "\n\n".join(self.article_data.get("article-content", []))
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, content)

        current = self.article_data.get("category", [])
        self.selected_tag.set(current[0] if current else "")

    def save_changes(self):
        selected_tag = self.selected_tag.get()
        if not selected_tag:
            messagebox.showwarning("未選擇標籤", "請選擇一個標籤後再儲存。")
            return

        self.article_data["category"] = [selected_tag]
        path = os.path.join(ARTICLE_DIR, self.current_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.article_data, f, ensure_ascii=False, indent=2)

        self.load_next()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReviewApp(root)
    root.mainloop()
