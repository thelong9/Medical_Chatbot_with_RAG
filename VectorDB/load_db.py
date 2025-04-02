from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from Chatbot.config import PERSIST_DIRECTORY, EMBEDDING_MODEL

# Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def load_db(data_type, persist_directory=PERSIST_DIRECTORY):
    chroma_db = Chroma(
        collection_name=data_type,
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )
    return chroma_db
