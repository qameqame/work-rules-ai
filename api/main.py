from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
import ollama as ollama_client
from config import settings

app = FastAPI(title="就業規則AI API")

embeddings = HuggingFaceEmbeddings(model_name=settings.embed_model)

chroma_client = chromadb.HttpClient(
    host=settings.chroma_host,
    port=settings.chroma_internal_port,
)

vectorstore = Chroma(
    collection_name="work_rules",
    embedding_function=embeddings,
    client=chroma_client,
)

ollama = ollama_client.Client(host=settings.ollama_base_url)


class Query(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str
    sources: list[dict]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=Answer)
def ask(query: Query):
    try:
        docs = vectorstore.similarity_search(query.question, k=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {e}")

    if not docs:
        return Answer(answer="該当する条文が見つかりませんでした。", sources=[])

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""以下は就業規則の抜粋です。この情報だけをもとに質問に答えてください。
抜粋に答えが含まれない場合は「就業規則に記載が見当たりません」と答えてください。

【就業規則抜粋】
{context}

【質問】
{query.question}

【回答】"""

    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLMエラー: {e}")

    sources = [
        {
            "page": d.metadata.get("page", "不明"),
            "source": d.metadata.get("source", "不明"),
        }
        for d in docs
    ]

    return Answer(answer=response["message"]["content"], sources=sources)