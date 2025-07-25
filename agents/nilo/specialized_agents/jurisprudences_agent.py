from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from utils.app_config import SUPABASE_DB_URL

# Jurisprudences RAG Agent  
jurisprudences_agent = Agent(
    name="Jurisprudences Agent",
    role="Provide legal precedents and case law information",
    model=OpenAIChat(id="gpt-4o"), 
    storage=PostgresStorage(table_name="agent_jurisprudences", db_url=SUPABASE_DB_URL),
    instructions=[
        "Provide legal precedents and case law information",
        "Provide legal precedents and court decisions", 
        "Explain how precedents apply to current situations",
        "Use your knowledge of legal jurisprudence and case law",
    ],
    markdown=True,
)