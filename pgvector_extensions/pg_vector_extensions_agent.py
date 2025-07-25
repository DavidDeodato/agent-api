# Database configuration for Supabase
SUPABASE_DB_URL = "postgresql+psycopg://[user]:[password]@[host]:[port]/[database]"

from agno.vectordb.pgvector import PgVector, SearchType
from agno.embedder.openai import OpenAIEmbedder

# Configure vector database for different document types
nda_vector_db = PgVector(
    table_name="nda_documents",
    db_url=SUPABASE_DB_URL,
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)

faq_vector_db = PgVector(
    table_name="faq_documents", 
    db_url=SUPABASE_DB_URL,
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)

clauses_vector_db = PgVector(
    table_name="clauses_documents",
    db_url=SUPABASE_DB_URL, 
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)

jurisprudences_vector_db = PgVector(
    table_name="jurisprudences_documents",
    db_url=SUPABASE_DB_URL,
    search_type=SearchType.hybrid, 
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)