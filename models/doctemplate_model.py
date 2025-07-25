from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import psycopg
from psycopg.rows import dict_row

@dataclass
class DocTemplateModel:
    id: Optional[int] = None
    name: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None