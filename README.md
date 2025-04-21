# Chatbot RAG y tế với LangChain

## Giới Thiệu

Dự án này là một chatbot RAG (Retrieval-Augmented Generation) chuyên về lĩnh vực y tế, sử dụng **LangChain** và **Google Gemini API** để giải đáp thông tin về bệnh và thuốc.

Chatbot có khả năng:
- Tìm kiếm và trích xuất thông tin thuốc và bệnh từ kho dữ liệu.
- Sử dụng **Neo4j** để lưu trữ vector embeddings.
- Tự động phân loại truy vấn và chọn nguồn dữ liệu phù hợp.
- Sử dụng **Google Gemini** để sinh ra câu trả lời có ngữ cảnh.

## Mô hình
- Embedding Model: all-MiniLM-L6-v2
- LLM: gemini-1.5-pro

### 1. Cài Đặt Môi Trường


```bash
pip install -r requirements.txt
```

### 2. Thêm Google API Key
Tạo file .env như sau:

```bash
GOOGLE_API_KEY = "YOUR API KEY"  # Thay bằng API key của bạn
```

### 3. Đóng Docker và truy cập local web
Chạy các lệnh sau để tạo vector database từ dữ liệu thuốc và bệnh:

```python
docker-compose up --build
```




