import os
import dotenv
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load các biến môi trường
dotenv.load_dotenv()

REVIEWS_CSV_PATH = "data/reviews.csv" # Các dữ liệu đánh giá raw lưu trữ
REVIEWS_CHROMA_PATH = "chroma_data" # Nơi mà các vector cơ sở dữ liệu sẽ lưu dữ liệu

"""
Load dữ liệu từ file reviews.csv
source_column: chỉ định muốn lấy nội dung của cột review
"""
loader = CSVLoader(file_path=REVIEWS_CSV_PATH, source_column="review")
reviews = loader.load()

# Sử dụng mô hình Sentence Transformer của HuggingFace để tạo các embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Tạo cơ sở dữ liệu vector Chroma sử dụng mô hình embedding Sentence Transformer
reviews_vector_db = Chroma.from_documents(
    reviews, embeddings, persist_directory=REVIEWS_CHROMA_PATH
)

print("Database created successfully with Sentence Transformers embeddings!")


