from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from Chatbot.config import LLM_MODEL,EMBEDDING_MODEL,PERSIST_DIRECTORY,RERANKER_MODEL, GOOGLE_API_KEY


llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,  
    google_api_key=GOOGLE_API_KEY
)

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

persist_directory = PERSIST_DIRECTORY

# Mô hình Reranking (Cross-Encoder)
reranker = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)
compressor = CrossEncoderReranker(model=reranker, top_n=10)