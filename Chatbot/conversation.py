from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def create_conversational_chain(llm, retriever, memory, answer_prompt):
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": answer_prompt}
    )
    return chain

def create_response(question, chain):
    response = chain.invoke({"question": question})  
    return response["answer"]
