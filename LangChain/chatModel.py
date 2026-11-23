from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=1.5
)

chat_history = [
    SystemMessage(content = "You are a Helpful AI Assitant")
]

while True:
    user_input = input("User:  ")
    chat_history.append(HumanMessage(content=user_input))
    if user_input == "exit":
        break
    else:
        result = model.invoke(chat_history)
        chat_history.append(AIMessage(content=result.content))
        print("AI:  ", result.content)

print(chat_history)