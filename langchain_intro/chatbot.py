#API_KEY

import dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema.runnable import RunnablePassthrough

from langchain.agents import (
    Tool,
    AgentType,
    initialize_agent
)
# from langchain.llms import google_palm
# from langchain import hub
from langchain_intro.tools import get_current_wait_time



REVIEW_CHROMA_PATH = "chroma_data/"

review_template_str = """Your job is to use patient
reviews to answer questions about their experience at
a hospital. Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.

{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=review_template_str
    )
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template=review_template_str
    )
)

messages = [review_system_prompt, review_human_prompt]

review_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages
)

output_parser = StrOutputParser()

chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key="<YOUR_API_KEY>") | output_parser

# review_chain = review_prompt_template | chat_model | output_parser

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

review_vector_db = Chroma(
    persist_directory=REVIEW_CHROMA_PATH,
    embedding_function=embeddings,
)
"""
as_retriever(): chuyển đổi 1 Vector Store thành 1 đối tượng Retriever
"""
reviews_retriever = review_vector_db.as_retriever(k=10)

"""
RunnablePassthrough(): Lớp đảm bảo rằng dữ liệu đầu vào không bị thay
                       đổi khi đi qua pipeline xử lý
"""
review_chain = (
    {"context": reviews_retriever, "question": RunnablePassthrough()}
    | review_prompt_template
    | chat_model
    | output_parser
)

tools = [
    Tool(
        name="Reviews",
        func=review_chain.invoke,
        description="""Useful when you need to answer questions
        about patient reviews or experiences at the hospital.
        Not useful for answering questions about specific visit
        details such as payer, billing, treatment, diagnosis,
        chief complaint, hospital, or physician information.
        Pass the entire question as input to the tool. For instance,
        if the question is "What do patients think about the triage system?",
        the input should be "What do patients think about the triage system?"
        """,
    ),
    Tool(
        name="Waits",
        func=get_current_wait_time,
        description="""Use when asked about current wait times
        at a specific hospital. This tool can only get the current
        wait time at a hospital and does not have any information about
        aggregate or historical wait times. This tool returns wait times in
        minutes. Do not pass the word "hospital" as input,
        only the hospital name itself. For instance, if the question is
        "What is the wait time at hospital A?", the input should be "A".
        """,
    ),
]

agent_chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key="<YOUR_API_KEY>") | output_parser
"""
- tools=tools: Danh sách các Tool mà agent có thể sử dụng để thực hiện các tác vụ, dựa vào description để quyết định
xem có sử dụng công cụ đó hay không.
- llm=agent_chat_model: Đóng vai trò "bộ não" của agent
- agent: Xác định chiến lược hoạt động của agent
- AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION: là 1 loại agent phổ biến trong lanchain, hoạt động theo cơ 
chế ReAct (Resoning(suy nghĩ từng bước) + Acting(ra quyết định)).
- return_intermediate_steps: Quyết định agent có trả về bước trung gian(tools call, kết quả từng bước,...)
"""
hospital_agent_executor = initialize_agent(
    tools=tools,
    llm=agent_chat_model,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True,
)

