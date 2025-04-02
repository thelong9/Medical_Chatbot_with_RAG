import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Cấu hình model
PERSIST_DIRECTORY = "D:\Chatbot RAG\Data\Chroma"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = "gemini-2.0-pro-exp-02-05"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

__all__ = ["GOOGLE_API_KEY", "PERSIST_DIRECTORY", "EMBEDDING_MODEL", "LLM_MODEL", "RERANKER_MODEL"]
