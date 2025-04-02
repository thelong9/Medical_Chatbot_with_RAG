from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.runnables import RunnableSequence
from Model.model import compressor


def create_prompt_template():
    # Cấu hình prompt
    classification_prompt_template = """Bạn là một trợ lý y tế thông minh.
    Hãy phân loại truy vấn sau đây vào một trong bốn nhóm (chỉ trả lời "thuoc", "benh", "nhieu" hoặc "unknown"):
    1. "thuoc" nếu nó liên quan đến thông tin thuốc (thành phần, công dụng, liều lượng, tác dụng phụ, bảo quản, cách dùng).
    2. "benh" nếu nó liên quan đến bệnh lý (triệu chứng, nguyên nhân, chẩn đoán, điều trị, phòng ngừa).
    3. "nhieu" nếu nó có thể liên quan đến cả hai nhóm.
    4. "unknown" nếu không có thông tin nào liên quan đến thuốc hoặc bệnh.

    Truy vấn: {query}
    Phân loại:"""


    answer_prompt_template = """Bạn là: BotTech, một trợ lý y tế thông minh giúp giải đáp thắc mắc của bệnh nhân.
    Sử dụng thông tin sau để trả lời câu hỏi một cách chính xác, chỉ đưa ra câu trả lời trực tiếp từ thông tin cung cấp.
    Hãy trả lời một cách thân thiện với người dùng.
    Nếu thông tin không đầy đủ, trả lời: "Xin lỗi, tôi chưa thể giải đáp thắc mắc của bạn, xin vui lòng đặt câu hỏi chi tiết hơn".
    Nếu câu hỏi không thuộc lĩnh vực y tế, trả lời: "Xin lỗi, tôi chỉ có thể cung cấp các thông tin về y tế", trừ trường hợp hỏi về thông tin cá nhân của bạn thì hãy giới thiệu bản thân.
    Nếu không biết câu trả lời, trả lời: "Xin lỗi câu hỏi của bạn nằm ngoài tầm hiểu biết của tôi.".


    {context}

    Câu hỏi: {question}
    Trả lời:"""

    ANSWER_PROMPT = PromptTemplate(template=answer_prompt_template, input_variables=["context", "question"])
    CLASSIFICATION_PROMPT = PromptTemplate(template=classification_prompt_template, input_variables=["query"])

    return ANSWER_PROMPT, CLASSIFICATION_PROMPT

def create_conversational_chain(llm, retriever, memory, answer_prompt):
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": answer_prompt}
    )
    return chain



# Hàm xác định loại truy vấn bằng Gemini
def detect_data_type(question, classification_prompt, llm):
    classification_chain = RunnableSequence(classification_prompt | llm)  
    data_type = classification_chain.invoke({"query": question}) 
    return data_type


# Reranking các retriver
def reranking(db_thuoc, db_benh, data_type, k=20):

    if data_type == "nhieu":
        retriever_thuoc = db_thuoc.as_retriever(search_type="mmr", search_kwargs={"k": k})
        retriever_benh = db_benh.as_retriever(search_type="mmr", search_kwargs={"k": k})
        ensemble_retriever = EnsembleRetriever(retrievers=[retriever_thuoc, retriever_benh])
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=ensemble_retriever
        )
    else:
        db = db_thuoc if data_type == "thuoc" else db_benh
        retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": k})
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=retriever
        )
    return compression_retriever

