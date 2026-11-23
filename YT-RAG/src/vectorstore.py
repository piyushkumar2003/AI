from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import SEARCH_K


def create_vector_store(chunks):
    """Generates free local embeddings using Hugging Face."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store


def get_retriever(vector_store, k=SEARCH_K):
    """Creates a similarity retriever from the vector store."""
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )