from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

prompt1 = PromptTemplate(
    template = "Give me Summary about the {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template = "Give me 3 pointer summary from the following text {text}",
    input_variables=['text']
)

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=1.5
)

parser = StrOutputParser()

chain = prompt1 | model | parser | prompt2 | model | parser 

print(chain.invoke({'topic' : 'cricket'}))

chain.get_graph().print_ascii()