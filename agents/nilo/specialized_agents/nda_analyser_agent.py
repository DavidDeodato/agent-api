from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from utils.app_config import SUPABASE_DB_URL

# NDA Document Analyzer Agent
nda_analyzer = Agent(
    name="NDA Document Analyzer",
    role="Analyze NDA documents for key terms, clauses, and legal implications",
    model=OpenAIChat(id="gpt-4o"),
    storage=PostgresStorage(table_name="nda_analyzer_sessions", db_url=SUPABASE_DB_URL),
    instructions=[
        "Analyze NDA documents for key legal terms and clauses",
        "Identify potential risks and obligations",
        "Provide clear explanations of legal implications",
        "Always cite specific sections from the documents",
        "Use your knowledge of legal documents and NDA best practices",
    ],
    markdown=True,
)