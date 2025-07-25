from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from utils.app_config import SUPABASE_DB_URL

# Clauses RAG Agent
clauses_agent = Agent(
    name="Clauses Agent",
    role="Provide information about specific legal clauses and their implications", 
    model=OpenAIChat(id="gpt-4o"),
    storage=PostgresStorage(table_name="agent_clauses", db_url=SUPABASE_DB_URL),
    instructions=[
        "Provide information about specific legal clauses and their implications",
        "Explain clause meanings and implications",
        "Provide examples and precedents when available",
        "Use your knowledge of legal documents and contract law",
    ],
    markdown=True,
)