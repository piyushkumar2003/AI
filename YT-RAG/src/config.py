import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Default Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "text-embedding-3-small"

# Updated Groq Model Name
LLM_MODEL = "openai/gpt-oss-20b"  # Alternatively use "llama3-8b-8192" or "mixtral-8x7b-32768"
LLM_TEMPERATURE = 0.2
SEARCH_K = 4