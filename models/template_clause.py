"""
Modelo para representar uma cláusula de template de documento.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TemplateClause(BaseModel):
    """
    Modelo para representar uma cláusula de template de documento.
    
    Corresponde à tabela template_clauses no banco de dados.
    """
    
    id: int
    doc_template_id: int
    section_name: str
    order_num: int
    type: str  # 'mandatory' ou 'optional'
    system_prompt: str
    content_template: Optional[str] = None
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    placeholders: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
