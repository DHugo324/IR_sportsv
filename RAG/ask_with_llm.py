from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import os
#import google.generativeai as genai
#from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def load_retriever(persist_dir="chroma_store", model_name="BAAI/bge-small-zh-v1.5"):
    #初始化向量資料庫
    embedding_model = HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs={"normalize_embeddings": True}
        #model_kwargs={"device": "cuda"}   #如果有GPU
    )
    db = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    retriever = db.as_retriever(  #從db找向量
        search_type="mmr", #不只是找最相似的段落且彼此之間差異性比較大的段落
        search_kwargs={"k": 4, "fetch_k": 8,"score_threshold": 0.5} #從這8段裡，選出4段 濾掉分數太低
    )
    return retriever

def load_llm(model_name="qwen:7b", temperature=0.7):
    #初始化LLM
    return Ollama(model=model_name, temperature=temperature)

def load_gemini():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    return GoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        google_api_key = GOOGLE_API_KEY
    )

def load_prompt():
    template = """
    你是一位專業的籃球分析師，請根據以下文章內容回答使用者的問題。

    問題：{question}

    相關內容：
    {context}

    請用清楚的中文簡潔回答。
    """
    return PromptTemplate.from_template(template)

def main():
    retriever = load_retriever()
    llm = load_llm()
    prompt = load_prompt()
    qa_chain = LLMChain(llm=llm, prompt=prompt)

    print("籃球新聞 RAG 助手啟動，請輸入問題（輸入 exit 離開）")
    while True:
        query = input("\n請輸入問題：").strip()
        if query.lower() in ["exit", "quit"]:
            print("已離開問答助手")
            break

        docs = retriever.get_relevant_documents(query)
        if not docs:
            print("找不到相關內容")
            continue

        context = "\n\n".join(doc.page_content for doc in docs)
        response = qa_chain.run(question=query, context=context)

        print("\nAI 回答：")
        print(response)

        print("\n來源段落：")
        for doc in docs:
            print(f"{doc.metadata.get('title', '未知')}（{doc.metadata.get('date', '')}）")

if __name__ == "__main__":
    main()
