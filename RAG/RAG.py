import gradio as gr
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 載入 retriever
def load_retriever(persist_dir="chroma_store", model_name="BAAI/bge-small-zh-v1.5"):
    embedding_model = HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs={"normalize_embeddings": True}
    )
    db = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 8, "score_threshold": 0.5}
    )
    return retriever

# 載入 LLM
def load_llm(model_name="llama3", temperature=0.7):
    return Ollama(model=model_name, temperature=temperature)

# 載入 prompt 模板
def load_prompt():
    template = """
    你是一位專業的籃球分析師，請根據以下文章內容回答使用者的問題。

    問題：{question}

    相關內容：
    {context}

    請用清楚的中文簡潔回答。
    """
    return PromptTemplate.from_template(template)

# 問答邏輯
retriever = load_retriever()
llm = load_llm()
prompt = load_prompt()
qa_chain = LLMChain(llm=llm, prompt=prompt)

def rag_qa_interface(query):
    docs = retriever.get_relevant_documents(query)
    if not docs:
        return "❌ 找不到相關內容", ""

    context = "\n\n".join(doc.page_content for doc in docs)
    response = qa_chain.run(question=query, context=context)

    sources = "\n".join([f"- {doc.metadata.get('title', '未知')}（{doc.metadata.get('date', '')}）" for doc in docs])
    return response, sources

# 啟動 Gradio 介面
iface = gr.Interface(
    fn=rag_qa_interface,
    inputs=gr.Textbox(label="請輸入籃球問題"),
    outputs=[
        gr.Textbox(label="AI 回答"),
        gr.Textbox(label="來源段落")
    ],
    title="🏀 籃球新聞 RAG 問答助手",
    description="請輸入一個問題，我會根據爬下來的文章內容來回答。"
)

if __name__ == "__main__":
    iface.launch()
