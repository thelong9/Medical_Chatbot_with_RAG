from langchain_chroma import Chroma
from Model.model import embedding_model, persist_directory

def query_db(query, data_type="thuoc", top_k=5):

    chroma_db = Chroma(
        collection_name=data_type,
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )

    retriver_test = chroma_db.as_retriever(search_kwargs={"k": top_k})

    results = chroma_db.similarity_search(query, k=top_k)

    # In kết quả truy vấn
    print(f"Top {top_k} kết quả cho truy vấn: '{query}'")
    for i, res in enumerate(results):
        print(f"\nKết quả {i+1}:")
        print(f"{res.page_content}")
        print(f"{res.metadata}")
        print(retriver_test.invoke(query))


query_db("Beprosone Cream có tác dụng gì ? Tôi bị viêm da cơ địa, có dùng được không?", data_type="thuoc")
query_db("Suy tim trái là bệnh gì ?", data_type="benh")