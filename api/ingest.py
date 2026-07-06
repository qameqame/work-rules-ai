from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from config import settings


def ingest():
    print("PDFを読み込み中...")
    loader = PyPDFDirectoryLoader("/app/docs")
    documents = loader.load()

    if not documents:
        print("docs/ にPDFが見つかりません。")
        return

    print(f"{len(documents)} ページを読み込みました。")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n第", "\n（", "\n　", "\n", "。", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"{len(chunks)} チャンクに分割しました。")

    embeddings = HuggingFaceEmbeddings(model_name=settings.embed_model)

    client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_internal_port,
    )

    Chroma.from_documents(
        chunks,
        embeddings,
        collection_name="work_rules",
        client=client,
    )
    print("ChromaDBへの登録が完了しました。")


if __name__ == "__main__":
    ingest()