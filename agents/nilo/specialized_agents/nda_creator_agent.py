from typing import Dict, List, Optional, Any
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from agno.tools import tool
from pepperlaw_intelligent_agents.src.crud.da_database_crud import NDADatabaseCrud
from pepperlaw_intelligent_agents.src.tools.nda_creator_agent_tools import (
    start_nda_creation,
    process_clause_response,
    skip_optional_clause,
    get_document_preview,
    validate_clause_content,
    complete_nda_document
)

class NDACreatorAgent:
    def __init__(self, db_url: str, doc_template_ids: List[int]):
        self.db = NDADatabaseCrud(db_url)
        self.doc_template_ids = doc_template_ids
        self.current_document_id: Optional[int] = None
        self.current_template_id: Optional[int] = None
        self.current_clauses: List[ClauseModel] = []
        self.current_clause_index: int = 0
        
        # Create the agent with database tools
        self.agent = Agent(
            name="NDA Creator Agent",
            role="Create NDA documents by guiding users through clause-by-clause completion",
            model=OpenAIChat(id="gpt-4o"), #TODO: TROCAR PARA O MODELO PEPPERLAW
            tools=[
                start_nda_creation,
                process_clause_response,
                skip_optional_clause,
                get_document_preview,
                validate_clause_content,
                complete_nda_document
            ],
            storage=PostgresStorage(table_name="nda_creator_sessions", db_url=db_url),
            instructions=[
                #TODO: TROCAR PARA CARREGAR DO BANCO DE DADOS
                "You are an expert NDA creation assistant.",
                "Guide users through creating NDAs step by step.",
                "Always validate user responses against alert conditions.",
                "Provide helpful suggestions when needed.",
                "Confirm completion of each clause before proceeding.",
                "Be professional and clear in your communication."
            ],
            show_tool_calls=True,
            markdown=True,
        )
    
    
   
        