from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from Chatbot.config import PERSIST_DIRECTORY
from Model.model import embedding_model


# Định nghĩa thư mục lưu trữ vector database
persist_directory = PERSIST_DIRECTORY

def create_db(df, data_type="thuoc"):


    # Xử lý dữ liệu tùy theo loại
    if data_type == "thuoc":
        df = df[["Tên thuốc", "URL", "Thành phần", "Công dụng", "Cách dùng", "Tác dụng phụ", "Lưu ý", "Bảo quản", "Loại thuốc"]].copy()

        # Ghép thông tin thành một nội dung thống nhất
        df["Nội dung"] = df.apply(lambda row: ' '.join([
        str(row["Tên thuốc"]).strip(),
        str(row["Thành phần"]).strip(),
        str(row["Công dụng"]).strip(),
        str(row["Cách dùng"]).strip(),
        str(row["Tác dụng phụ"]).strip(),
        str(row["Lưu ý"]).strip(),
        str(row["Bảo quản"]).strip(),
        str(row["Loại thuốc"]).strip()
        ]), axis=1)


    # Cấu hình chunking (chia nhỏ văn bản)
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=0,
    )

    documents = []
    metadata = []

    for _, row in df.iterrows():
        chunks = text_splitter.split_text(row["Nội dung"])

        for chunk in chunks:
            documents.append(chunk)
            metadata.append({
              "Tên bệnh" if data_type == "benh" else "Tên thuốc": row["Tên bệnh"] if data_type == "benh" else row["Tên thuốc"],
              **({"Loại thuốc": row["Loại thuốc"]} if data_type == "thuoc" else {}),
              "URL": row["URL"]
            })


    print(f"Tổng số đoạn (chunks) được tạo: {len(documents)}")

    chroma_db = Chroma(
        collection_name=data_type,
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )

    chroma_db.add_texts(texts=documents, metadatas=metadata)

    chroma_db.persist()
    print(f"Dữ liệu {data_type} đã được lưu vào ChromaDB.")

create_db("data/medicine_data.csv", data_type="thuoc")
create_db("data/disease_data.csv", data_type="benh")