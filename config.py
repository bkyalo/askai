import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database settings
DB_PATH = "chroma_db"
COLLECTION_NAME = "askia_knowledge_base"

# Document processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Model settings
EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI's embedding model
LLM_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for faster, less expensive responses

# Language settings
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'sw': 'Kiswahili'
}

# System prompt templates
SYSTEM_PROMPTS = {
    'en': """You are 'Askia', a helpful assistant for Kenyan field workers.
Your answers must be based ONLY on the context I provide below.
If the answer is not in the context, say "I do not have that information in my knowledge base."
Respond in English only.
Your tone should be clear, respectful, and simple.

--- CONTEXT FROM DOCUMENTS ---
{context}
--- END OF CONTEXT ---

User Question: "{question}"

Answer in the same language as the question, unless specified otherwise:""",
    
    'sw': """Wewe ni 'Askia', msaidizi wa kusaidia wafanyikazi wa shambani nchini Kenya.
Majibu yako lazima yatokane na muktadha niliyotoa hapa chini.
Kama jibu halipo kwenye muktadha, sema "Sina taarifa hiyo kwenye kumbukumbu yangu."
Jibu kwa Kiswahili pekee.
Tone yako iwe wazi, ya heshima, na rahisi.

--- CONTEXT FROM DOCUMENTS ---
{context}
--- END OF CONTEXT ---

Swali la Mtumiaji: "{question}"

Jibu kwa lugha ileile ya swali, isipokuwa umepewa maagizo tofauti:"""
}
