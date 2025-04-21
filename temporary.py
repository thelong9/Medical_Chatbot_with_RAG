# from langchain_intro.chatbot import review_chain
# # from langchain.schema import HumanMessage, SystemMessage

# # messages = [
# #     SystemMessage(content="You're an assistant knowledgeable about healthcare. Only answer healthcare-related questions."),
# #     HumanMessage(content="How do i change tire")
# # ]

# # response = chat_model.invoke(messages)
# # print(response)

# # context = "I'm having a problem with my head"
# # question = "Can you suggest me some medicines to relieve my headache"
# question = """Has anyone complained about
#             communication with the hospital staff?"""
# answer = review_chain.invoke(question)
# print(answer)


# from langchain_intro.chatbot import hospital_agent_executor
# response_wait = hospital_agent_executor.invoke({"input": "What is the current wait time at hospital C?"})
# print(response_wait)
# response_review = hospital_agent_executor.invoke(
#     {"input": "What have patients said about their comfort at the hospital?"}
# )
# print(response_review)


# from chatbot_api.src.chains.hospital_review_chain import reviews_vector_chain
# query = """What have patients said about hospital efficiency?
#          Mention details from specific reviews."""
# response = reviews_vector_chain.invoke(query)
# print(response)


# from chatbot_api.src.chains.hospital_cypher_chain import hospital_cypher_chain
# question = """What is the average visit duration for
#             emergency visits in North Carolina?"""
# response = hospital_cypher_chain.invoke(question)
# print(response)


# from chatbot_api.src.tools.wait_times import (
#     get_current_wait_times,
#     get_most_available_hospital,
# )
# print(get_current_wait_times("Wallace-Hamilton"))
# print(get_most_available_hospital(None))


from chatbot_api.src.agents.hospital_rag_agent import hospital_rag_agent_executor
response = hospital_rag_agent_executor.invoke(
    {"input": "What is the wait time at Wallace-Hamilton?"}
)
print(response)

