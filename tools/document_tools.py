"""
Ferramentas para o workflow de criação de documentos.

Estas ferramentas são usadas pelos agentes AGNO para:
1. Iniciar a criação de um documento
2. Processar respostas para cláusulas
3. Obter preview ao vivo do documento
4. Finalizar o documento
"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from agno.tools import tool
from database.nda_database import NDADatabaseCrud
from models.template_clause import TemplateClause
from models.live_document import LiveDocument


class ClauseInfo(BaseModel):
    """Informações sobre uma cláusula de template."""
    
    id: int
    section_name: str
    order_num: int
    type: str
    system_prompt: str
    content_template: Optional[str] = None
    placeholders: Dict[str, Any] = Field(default_factory=dict)


class DocumentInfo(BaseModel):
    """Informações sobre um documento em andamento."""
    
    id: int
    template_id: int
    template_name: str
    current_clause: ClauseInfo
    content: Dict[str, Any] = Field(default_factory=dict)
    status: str
    progress: Dict[str, Any] = Field(default_factory=dict)


@tool("Inicia a criação de um documento baseado em template")
async def start_document_creation(
    db_url: str,
    user_id: str,
    template_id: int
) -> DocumentInfo:
    """
    Inicia a criação de um documento baseado em template.
    
    Args:
        db_url: URL de conexão com o banco de dados
        user_id: ID do usuário
        template_id: ID do template
        
    Returns:
        Informações sobre o documento iniciado
    """
    db = NDADatabaseCrud(db_url)
    
    # Obter template
    template = await db.get_template_by_id(template_id)
    if not template:
        raise ValueError(f"Template não encontrado: {template_id}")
    
    # Obter cláusulas
    clauses = await db.get_clauses_by_template(template_id)
    if not clauses:
        raise ValueError(f"Template sem cláusulas: {template_id}")
    
    # Criar documento
    live_doc = await db.create_live_document(user_id, template_id)
    
    # Preparar informações da primeira cláusula
    first_clause = clauses[0]
    clause_info = ClauseInfo(
        id=first_clause.id,
        section_name=first_clause.section_name,
        order_num=first_clause.order_num,
        type=first_clause.type,
        system_prompt=first_clause.system_prompt,
        content_template=first_clause.content_template,
        placeholders=first_clause.placeholders
    )
    
    # Calcular progresso
    total_clauses = len(clauses)
    mandatory_clauses = len([c for c in clauses if c.type == 'mandatory'])
    
    progress = {
        "current_clause": 1,
        "total_clauses": total_clauses,
        "mandatory_clauses": mandatory_clauses,
        "completed_clauses": 0,
        "percentage": 0
    }
    
    return DocumentInfo(
        id=live_doc.id,
        template_id=template.id,
        template_name=template.name,
        current_clause=clause_info,
        content={},
        status=live_doc.status,
        progress=progress
    )


@tool("Processa a resposta do usuário para uma cláusula")
async def process_clause_response(
    db_url: str,
    doc_id: int,
    clause_id: int,
    user_response: str,
    filled_content: str
) -> DocumentInfo:
    """
    Processa a resposta do usuário para uma cláusula.
    
    Args:
        db_url: URL de conexão com o banco de dados
        doc_id: ID do documento
        clause_id: ID da cláusula atual
        user_response: Resposta do usuário
        filled_content: Conteúdo preenchido da cláusula
        
    Returns:
        Informações atualizadas do documento
    """
    db = NDADatabaseCrud(db_url)
    
    # Obter documento
    live_doc = await db.get_live_document_by_id(doc_id)
    if not live_doc:
        raise ValueError(f"Documento não encontrado: {doc_id}")
    
    # Obter template
    template = await db.get_template_by_id(live_doc.doc_template_id)
    if not template:
        raise ValueError(f"Template não encontrado: {live_doc.doc_template_id}")
    
    # Obter cláusulas
    clauses = await db.get_clauses_by_template(template.id)
    if not clauses:
        raise ValueError(f"Template sem cláusulas: {template.id}")
    
    # Obter cláusula atual
    current_clause = next((c for c in clauses if c.id == clause_id), None)
    if not current_clause:
        raise ValueError(f"Cláusula não encontrada: {clause_id}")
    
    # Atualizar conteúdo do documento
    content = live_doc.content.copy() if live_doc.content else {}
    content[current_clause.section_name] = filled_content
    
    # Determinar próxima cláusula
    next_clause_order = current_clause.order_num + 1
    next_clause = next((c for c in clauses if c.order_num == next_clause_order), None)
    
    # Se não há próxima cláusula, documento está completo
    if not next_clause:
        await db.complete_document(doc_id)
        live_doc = await db.get_live_document_by_id(doc_id)
        
        # Calcular progresso final
        total_clauses = len(clauses)
        mandatory_clauses = len([c for c in clauses if c.type == 'mandatory'])
        completed_clauses = len(content.keys())
        
        progress = {
            "current_clause": total_clauses,
            "total_clauses": total_clauses,
            "mandatory_clauses": mandatory_clauses,
            "completed_clauses": completed_clauses,
            "percentage": 100
        }
        
        return DocumentInfo(
            id=live_doc.id,
            template_id=template.id,
            template_name=template.name,
            current_clause=ClauseInfo(
                id=current_clause.id,
                section_name=current_clause.section_name,
                order_num=current_clause.order_num,
                type=current_clause.type,
                system_prompt=current_clause.system_prompt,
                content_template=current_clause.content_template,
                placeholders=current_clause.placeholders
            ),
            content=content,
            status=live_doc.status,
            progress=progress
        )
    
    # Atualizar documento com próxima cláusula
    live_doc = await db.update_live_document_content(doc_id, content, next_clause.order_num)
    
    # Preparar informações da próxima cláusula
    next_clause_info = ClauseInfo(
        id=next_clause.id,
        section_name=next_clause.section_name,
        order_num=next_clause.order_num,
        type=next_clause.type,
        system_prompt=next_clause.system_prompt,
        content_template=next_clause.content_template,
        placeholders=next_clause.placeholders
    )
    
    # Calcular progresso
    total_clauses = len(clauses)
    mandatory_clauses = len([c for c in clauses if c.type == 'mandatory'])
    completed_clauses = len(content.keys())
    percentage = int((completed_clauses / total_clauses) * 100)
    
    progress = {
        "current_clause": next_clause.order_num,
        "total_clauses": total_clauses,
        "mandatory_clauses": mandatory_clauses,
        "completed_clauses": completed_clauses,
        "percentage": percentage
    }
    
    return DocumentInfo(
        id=live_doc.id,
        template_id=template.id,
        template_name=template.name,
        current_clause=next_clause_info,
        content=content,
        status=live_doc.status,
        progress=progress
    )


@tool("Obtém preview ao vivo do documento")
async def get_live_preview(
    db_url: str,
    doc_id: int
) -> str:
    """
    Obtém preview ao vivo do documento.
    
    Args:
        db_url: URL de conexão com o banco de dados
        doc_id: ID do documento
        
    Returns:
        Preview do documento em formato Markdown
    """
    db = NDADatabaseCrud(db_url)
    
    # Obter documento
    live_doc = await db.get_live_document_by_id(doc_id)
    if not live_doc:
        raise ValueError(f"Documento não encontrado: {doc_id}")
    
    # Obter template
    template = await db.get_template_by_id(live_doc.doc_template_id)
    if not template:
        raise ValueError(f"Template não encontrado: {live_doc.doc_template_id}")
    
    # Obter cláusulas
    clauses = await db.get_clauses_by_template(template.id)
    if not clauses:
        raise ValueError(f"Template sem cláusulas: {template.id}")
    
    # Gerar preview
    preview = f"# {template.name}\n\n"
    
    content = live_doc.content if live_doc.content else {}
    
    for clause in clauses:
        preview += f"## {clause.section_name}\n\n"
        
        if clause.section_name in content:
            # Seção já preenchida
            preview += f"{content[clause.section_name]}\n\n"
        elif clause.order_num == live_doc.current_clause_order:
            # Seção atual em preenchimento
            preview += "_Em preenchimento..._\n\n"
        else:
            # Seção ainda não preenchida
            preview += "_Aguardando preenchimento_\n\n"
    
    return preview


@tool("Finaliza o documento e gera versão final")
async def complete_document(
    db_url: str,
    doc_id: int
) -> str:
    """
    Finaliza o documento e gera versão final.
    
    Args:
        db_url: URL de conexão com o banco de dados
        doc_id: ID do documento
        
    Returns:
        Documento final em formato Markdown
    """
    db = NDADatabaseCrud(db_url)
    
    # Obter documento
    live_doc = await db.get_live_document_by_id(doc_id)
    if not live_doc:
        raise ValueError(f"Documento não encontrado: {doc_id}")
    
    # Obter template
    template = await db.get_template_by_id(live_doc.doc_template_id)
    if not template:
        raise ValueError(f"Template não encontrado: {live_doc.doc_template_id}")
    
    # Obter cláusulas
    clauses = await db.get_clauses_by_template(template.id)
    if not clauses:
        raise ValueError(f"Template sem cláusulas: {template.id}")
    
    # Verificar se todas as cláusulas obrigatórias foram preenchidas
    content = live_doc.content if live_doc.content else {}
    mandatory_clauses = [c for c in clauses if c.type == 'mandatory']
    
    for clause in mandatory_clauses:
        if clause.section_name not in content:
            raise ValueError(f"Cláusula obrigatória não preenchida: {clause.section_name}")
    
    # Marcar documento como completo
    await db.complete_document(doc_id)
    
    # Gerar documento final
    document = f"# {template.name}\n\n"
    
    for clause in clauses:
        if clause.section_name in content:
            document += f"## {clause.section_name}\n\n"
            document += f"{content[clause.section_name]}\n\n"
    
    return document
