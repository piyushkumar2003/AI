from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.config import LLM_MODEL, LLM_TEMPERATURE, GROQ_API_KEY


def format_docs(retrieved_docs):
    """Helper to join content from retrieved Document objects."""
    return "\n\n".join(doc.page_content for doc in retrieved_docs)


def build_rag_chain(retriever):
    """Constructs the full LCEL RAG chain using Groq LLM."""
    
    # Initialize Groq LLM
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=GROQ_API_KEY
    )

    # Prompt
    prompt = PromptTemplate(
        template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}

      Question: {question}
    """,
        input_variables=["context", "question"]
    )

    # Parallel retriever chain
    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })

    # Main pipeline execution chain
    parser = StrOutputParser()
    main_chain = parallel_chain | prompt | llm | parser

    return main_chain