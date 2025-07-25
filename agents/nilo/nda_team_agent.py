from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from utils.app_config import SUPABASE_DB_URL
from agents.nilo.specialized_agents.nda_analyser_agent import nda_analyzer
from agents.nilo.specialized_agents.faq_agent import faq_agent, clauses_agent, jurisprudences_agent


# The Main Creator NDA Agent Team
creator_nda_team = Team(
    name="Creator NDA Team",
    mode="coordinate",  # Team leader coordinates between agents
    model=OpenAIChat(id="gpt-4o"),
    members=[nda_analyzer, faq_agent, clauses_agent, jurisprudences_agent],
    storage=PostgresStorage(table_name="creator_nda_team_sessions", db_url=SUPABASE_DB_URL),
    instructions=[
        "You are a comprehensive NDA analysis system for creators",
        "Coordinate between specialized agents to provide complete analysis",
        "For document analysis, delegate to the NDA Document Analyzer",
        "For general questions, use the FAQ Agent",
        "For specific clause information, use the Clauses Agent", 
        "For legal precedents, use the Jurisprudences Agent",
        "Synthesize responses from multiple agents when needed",
        "Always provide actionable insights for creators",
    ],
    show_tool_calls=True,
    show_members_responses=True,
    markdown=True,
    enable_agentic_context=True,  # Enable shared context between agents,
    add_datetime_to_instructions=True,
)