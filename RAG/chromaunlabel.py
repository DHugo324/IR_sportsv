import os
import json
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

ARTICLE_DIR = "./articles/unlabeled_articles"
PERSIST_DIR = "./chroma_store"
MAX_ARTICLES = 99999


def load_documents_from_folder(folder_path, max_articles=MAX_ARTICLES):
    documents = []
    for filename in sorted(os.listdir(folder_path))[:max_articles]:
        if not filename.endswith(".json"):
            continue
        path = os.path.join(folder_path, filename)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            content = "\n".join(data.get("article-content", []))
            metadata = {
                "id": data.get("id"),
                "title": data.get("title"),
                "date": data.get("date"),
                "topic": data.get("topic"),
                "author": data.get("author_name"),
                "tags": ", ".join(data.get("tags", [])),
                "category": ", ".join(data.get("category", []))
            }
            documents.append(Document(page_content=content, metadata=metadata))
        except Exception as e:
            print(f"讀取 {filename} 失敗：{e}")
    print(f"讀入 {len(documents)} 篇文章")
    return documents


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)


def batched_add_documents(vectorstore, documents, batch_size=5000):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        vectorstore.add_documents(batch)


def create_or_update_chroma_vectorstore(documents, persist_dir=PERSIST_DIR):
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    try:
        existing_ids = {m["id"] for m in vectorstore.get()["metadatas"] if "id" in m}
    except Exception:
        existing_ids = set()
    print(f"已存在 {len(existing_ids)} 篇文章向量")

    fresh_docs = [doc for doc in documents if doc.metadata["id"] not in existing_ids]
    print(f"本次新增 {len(fresh_docs)} 篇文章")

    if fresh_docs:
        split_docs = split_documents(fresh_docs)
        batched_add_documents(vectorstore, split_docs)
        print("新文章已加入向量庫並保存")
    else:
        print("沒有新文章需要加入")


if __name__ == "__main__":
    docs_unlabeled = load_documents_from_folder(ARTICLE_DIR)
    docs_training = load_documents_from_folder("./articles/training_articles")
    docs = docs_training + docs_unlabeled
    create_or_update_chroma_vectorstore(docs)
