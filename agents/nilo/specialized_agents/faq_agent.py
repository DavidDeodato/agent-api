from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from utils.app_config import SUPABASE_DB_URL

# FAQ RAG Agent
faq_agent = Agent(
    name="FAQ Agent", 
    role="Answer frequently asked questions about NDAs and legal processes",
    model=OpenAIChat(id="gpt-4o"),
    storage=PostgresStorage(table_name="agent_faqs", db_url=SUPABASE_DB_URL),
    instructions=[
        "Answer frequently asked questions about NDAs and legal processes",
        "Provide comprehensive answers to common questions",
        "Use your knowledge of legal documents and best practices",
        "Include references to relevant legal concepts",
    ],
    markdown=True,
)

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