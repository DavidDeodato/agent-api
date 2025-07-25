from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import psycopg
from psycopg.rows import dict_row

class ClauseType(Enum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"

@dataclass
class ClauseModel:
    id: Optional[int] = None
    doc_template_id: int = 0
    order_num: int = 0
    section_name: str = ""
    type: ClauseType = ClauseType.MANDATORY
    type_alternatives: Dict[str, Any] = None
    alert_conditions: Dict[str, Any] = None
    suggestions: Dict[str, Any] = None
    system_prompt: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.type_alternatives is None:
            self.type_alternatives = {}
        if self.alert_conditions is None:
            self.alert_conditions = {}
        if self.suggestions is None:
            self.suggestions = {}