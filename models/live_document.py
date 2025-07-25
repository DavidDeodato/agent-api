"""
Modelo para representar um documento em processo de criação.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class LiveDocument(BaseModel):
    """
    Modelo para representar um documento em processo de criação.
    
    Corresponde à tabela live_documents no banco de dados.
    """
    
    id: int
    user_id: str
    doc_template_id: int
    content: Dict[str, Any] = Field(default_factory=dict)
    status: str = "in_progress"  # 'in_progress', 'completed', 'paused'
    current_clause_order: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
