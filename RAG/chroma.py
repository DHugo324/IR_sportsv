import os
import json
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

ARTICLE_DIR = "./articles/training_articles"      
PERSIST_DIR = "./chroma_store"   
MAX_ARTICLES = 99999             


def load_documents_from_folder(folder_path, max_articles=MAX_ARTICLES):
    documents = []
    # 取得排序後的檔名，限制數量
    for filename in sorted(os.listdir(folder_path))[:max_articles]: #sort可以改看要先抓那些
        if not filename.endswith(".json"):
            continue
        path = os.path.join(folder_path, filename)
        try:
            data = json.load(open(path, encoding="utf-8"))
            # 合併段落
            content = "\n".join(data.get("article-content", []))
            # 構建 metadata 字典 避免被向量化跟以後搜索
            metadata = {
                "id": data.get("id"),
                "title": data.get("title"),
                "date": data.get("date"),
                "topic": data.get("topic"),
                "author": data.get("author_name"),
                "tags": ", ".join(data.get("tags", [])),
                "category": ", ".join(data.get("category", []))
            }
            # 建立 Document 並加入列表
            documents.append(Document(page_content=content, metadata=metadata))
        except Exception as e:
            print(f"讀取 {filename} 失敗：{e}")
    print(f"讀入 {len(documents)} 篇文章")
    return documents


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """
    使用 RecursiveCharacterTextSplitter 將長文本切分為指定長度的段落。
    chunk_size: 每段最大字元數
    chunk_overlap: 段落之間重疊字元數 確保語句
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)


def create_or_update_chroma_vectorstore(documents, persist_dir=PERSIST_DIR):
    # 初始化嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5",
        #model_kwargs={"device": "cuda"},  # 用GPU跑
        encode_kwargs={"normalize_embeddings": True}
    )
    # 載入向量庫
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # 取得已存在的文章 ID 集合
    try:
        existing_ids = {m["id"] for m in vectorstore.get()["metadatas"] if "id" in m}
    except Exception:
        existing_ids = set()
    print(f"已存在 {len(existing_ids)} 篇文章向量")

    # 篩選尚未加入的文章
    fresh_docs = [doc for doc in documents if doc.metadata["id"] not in existing_ids]
    print(f"本次新增 {len(fresh_docs)} 篇文章")

    # 新文章切分並新增到向量庫
    if fresh_docs:
        split_docs = split_documents(fresh_docs)
        vectorstore.add_documents(split_docs)
        print("新文章已加入向量庫並保存")
    else:
        print("沒有新文章需要加入")


if __name__ == "__main__":
    docs_training = load_documents_from_folder(ARTICLE_DIR)
    docs_unlabeled = load_documents_from_folder("./articles/unlabeled_articles")
    docs = docs_training + docs_unlabeled
    create_or_update_chroma_vectorstore(docs)
