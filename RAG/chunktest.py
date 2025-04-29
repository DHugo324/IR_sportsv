import os
import json
import time
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 設定資料夾
ARTICLE_DIR = "./articles"
MAX_TEST_DOCS = 300  # 只拿前 10 篇測試

def load_documents(folder_path, max_docs=MAX_TEST_DOCS):
    documents = []
    files = sorted(os.listdir(folder_path))[:max_docs]

    for filename in files:
        if filename.endswith(".json"):
            path = os.path.join(folder_path, filename)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            content = "\n".join(data.get("article-content", []))
            metadata = {"id": data.get("id")}
            documents.append(Document(page_content=content, metadata=metadata))
    return documents

def test_chunk_settings(documents, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    start = time.time()
    chunks = splitter.split_documents(documents)
    end = time.time()

    total_chunks = len(chunks)
    total_chars = sum(len(doc.page_content) for doc in chunks)
    avg_chars = total_chars / total_chunks if total_chunks else 0
    elapsed = end - start

    print(f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    print(f"產生段落數：{total_chunks} 段")
    print(f"平均每段字數：約 {avg_chars:.1f} 字")
    print(f"切分花費時間：約 {elapsed:.3f} 秒")
    print("-" * 40)

if __name__ == "__main__":
    docs = load_documents(ARTICLE_DIR)

    # 想要比較的參數組合
    settings = [
        (300, 50),
        (300, 100),
        (500, 50),
        (500, 100),
        (700, 100),
    ]

    for chunk_size, chunk_overlap in settings:
        test_chunk_settings(docs, chunk_size, chunk_overlap)
