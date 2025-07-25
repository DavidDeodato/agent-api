"""
Modelo para representar um template de documento.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocTemplate(BaseModel):
    """
    Modelo para representar um template de documento.
    
    Corresponde à tabela doc_templates no banco de dados.
    """
    
    id: int
    agent_id: str
    name: str
    description: str
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
