import os
import json
import random
import tkinter as tk
from tkinter import messagebox
import move_file

ARTICLE_DIR = './articles/to_label'  # 已標記文章的資料夾
OUTPUT_DIR = './articles/training_articles'  # 新的標註完資料夾
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
    "球隊分析": "球隊表現預測、球隊近況、球隊未來展望、薪資空間",
    "球員焦點": "球員潛力預測、球員表現分析、個人評析",
    "交易與簽約": "自由市場球員簽約、球員選秀籤交易、交易傳聞",
    "教練與管理層": "教練/管理層變動，教練、管理層評析",
    "選秀觀察": "選秀分析、球隊選秀預測",
    "歷史與專題": "歷史回顧、人物專訪、經典賽事回顧、特殊專題"
}

class RelabelingApp:
    def __init__(self, master):
        self.master = master
        master.title("文章重標註工具")

        self.files = [f for f in os.listdir(ARTICLE_DIR) if f.endswith('.json')]
        random.shuffle(self.files)
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

        self.submit_button = tk.Button(self.button_frame, text="更新分類", command=self.submit)
        self.submit_button.grid(row=0, column=0, padx=10)

        self.skip_button = tk.Button(self.button_frame, text="略過", command=self.load_next_article)
        self.skip_button.grid(row=0, column=1, padx=10)

        self.load_next_article()

    def load_next_article(self):
        while self.files:
            filename = self.files.pop()
            path = os.path.join(ARTICLE_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "category" in data:
                self.current_file = filename
                self.article_data = data
                self.text.delete('1.0', tk.END)

                title = data.get("title", "（無標題）")
                article_id = data.get("id", "（無 ID）")
                current_cat = data.get("category", ["（無分類）"])[0]

                print(f"🔁 檢查文章 {article_id}《{title}》（目前分類：{current_cat}）")
                self.meta_label.config(text=f"ID：{article_id}\n標題：{title}\n原分類：{current_cat}")

                content = "\n\n".join(data.get('article-content', []))
                self.text.insert(tk.END, content)

                if data.get("category"):
                    self.selected_tag.set(data["category"][0])
                else:
                    self.selected_tag.set(None)
                return

        messagebox.showinfo("完成！", "所有文章都檢查完畢！")
        self.master.quit()

    def submit(self):
        selected_tag = self.selected_tag.get()
        if not selected_tag:
            messagebox.showwarning("請選擇分類", "請先選擇一個分類標籤！")
            return

        self.article_data["category"] = [selected_tag]

        path = os.path.join(ARTICLE_DIR, self.current_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.article_data, f, ensure_ascii=False, indent=2)

        # ✅ 將檔案移動到 reviewed_articles
        move_file.move_json_file(self.current_file, ARTICLE_DIR, OUTPUT_DIR)

        print(f"✅ {self.article_data.get('id', '未知ID')} 重標為：{selected_tag}")
        self.load_next_article()

if __name__ == "__main__":
    root = tk.Tk()
    app = RelabelingApp(root)
    root.mainloop()
