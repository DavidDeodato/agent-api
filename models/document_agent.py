from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import psycopg
from psycopg.rows import dict_row

@dataclass
class DocumentAgentModel:
    id: Optional[int] = None
    doc_template_id: int = 0
    content: Dict[str, str] = None
    status: str = "in_progress"
    current_clause_order: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.content is None:
            self.content = {}