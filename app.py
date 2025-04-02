from Chatbot.chain import detect_data_type, create_prompt_template,reranking
from Chatbot.conversation import create_conversational_chain, create_response, memory
from VectorDB.load_db import load_db
from Model.model import llm

def initialize_chatbot():

    db_thuoc = load_db("thuoc")
    db_benh = load_db("benh")
    answer_prompt, classification_prompt = create_prompt_template()
    return db_thuoc, db_benh, answer_prompt, classification_prompt

def process_chat(question, db_thuoc, db_benh, answer_prompt, classification_prompt):
    
    data_type = detect_data_type(question, classification_prompt, llm)

    retriever = reranking(db_thuoc, db_benh, data_type)

    chain = create_conversational_chain(llm, retriever, memory, answer_prompt)

    response = create_response(question, chain)
    return response

def main():
    db_thuoc, db_benh, answer_prompt, classification_prompt = initialize_chatbot()
    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit", "thoát"]:
            print("ChatBot: Cảm ơn vì được hỗ trợ bạn! Tạm biệt! Hẹn gặp lại sau.")
            break
        
        response = process_chat(user_input, db_thuoc, db_benh, answer_prompt, classification_prompt)
        print("ChatBot:", response, "\n")

if __name__ == "__main__":
    main()