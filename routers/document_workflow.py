"""
Endpoints FastAPI para o workflow de criação de documentos.

Este módulo implementa os endpoints para:
1. Iniciar o workflow de criação de documentos
2. Continuar o workflow com mensagens do usuário
3. Obter preview ao vivo do documento
"""

import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from agents.nilo.workflows.document_creation_workflow import DocumentCreationWorkflow
from agents.nilo.nda_team_agent import creator_nda_team
from database.nda_database import NDADatabaseCrud


# Configuração do router
router = APIRouter(
    prefix="/workflows/document-creation",
    tags=["document-creation"],
    responses={404: {"description": "Not found"}},
)


# Modelos de dados para os endpoints
class WorkflowRequest(BaseModel):
    """Modelo para requisição de workflow."""
    
    agent_id: str
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    analyze_intent_only: Optional[bool] = False


class TemplateSelectionRequest(BaseModel):
    """Modelo para requisição de seleção de template."""
    
    agent_id: str
    user_id: str
    template_id: int
    conversation_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    """
    Modelo para resposta de workflow.
    """
    
    content: str
    document_info: Optional[Dict[str, Any]] = None
    buttons: Optional[List[Dict[str, Any]]] = None
    response_type: Optional[str] = "message"  # "message", "selection", "confirmation"


# Endpoints
@router.post("/run")
async def run_document_workflow(request: WorkflowRequest) -> WorkflowResponse:
    """
    🧠 ROTEAMENTO INTELIGENTE CENTRALIZADO NO BACKEND AGNO
    
    Este endpoint é o ÚNICO ponto de entrada para todas as requisições.
    O backend AGNO decide automaticamente se é:
    - Consulta/FAQ → Resposta direta do orquestrador
    - Criação de documento → Workflow de documentos
    
    O FRONTEND NÃO TEM RESPONSABILIDADE DE DECISÃO!
    
    Args:
        request: Dados da requisição
        
    Returns:
        Resposta do workflow (consulta ou documento)
    """
    # Obter URL do banco de dados da variável de ambiente
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL não configurada")
    
    print(f"🚀 [AGNO] Processando mensagem: {request.message[:100]}...")
    print(f"🚀 [AGNO] Agent ID: {request.agent_id}")
    print(f"🚀 [AGNO] User ID: {request.user_id}")
    
    try:
        # 🧠 ETAPA 1: ANÁLISE DE INTENÇÃO COM ORQUESTRADOR
        print(f"🧠 [INTENT] Analisando intenção com creator_nda_team...")
        
        # Usar o orquestrador para análise inicial
        orchestrator_response = creator_nda_team.run(request.message)
        
        print(f"🧠 [INTENT] Resposta do orquestrador: {orchestrator_response.content[:200]}...")
        
        # 🔍 ETAPA 2: DETECÇÃO INTELIGENTE DE INTENÇÃO
        message_lower = request.message.lower()
        response_lower = orchestrator_response.content.lower()
        
        # Palavras-chave para criação de documentos
        document_keywords = [
            'criar documento', 'gerar documento', 'novo documento',
            'criar nda', 'gerar nda', 'novo nda',
            'criar contrato', 'gerar contrato', 'novo contrato',
            'documento de', 'preciso de um documento',
            'quero criar', 'vou criar', 'vamos criar'
        ]
        
        # Verificar se é intenção de criação de documento
        is_document_creation = any(
            keyword in message_lower for keyword in document_keywords
        ) or any(
            keyword in response_lower for keyword in document_keywords
        )
        
        # Verificar se o agente suporta criação de documentos
        db = NDADatabaseCrud(db_url)
        
        # Tratar casos especiais (orquestrador)
        if request.agent_id == 'creator_nda_team':
            # Para o orquestrador, sempre assumir que suporta documentos
            supports_documents = True
            agent = {'name': 'Creator NDA Team', 'doc_template_ids': []}
        else:
            # Para agentes normais, buscar no banco
            agent = await db.get_agent_by_id(request.agent_id)
            supports_documents = (
                agent and 
                agent.get('doc_template_ids') and 
                len(agent.get('doc_template_ids', [])) > 0
            )
        
        print(f"🔍 [DECISION] Intenção de documento: {is_document_creation}")
        print(f"🔍 [DECISION] Agente suporta documentos: {supports_documents}")
        
        # 🎯 ETAPA 3: ROTEAMENTO INTELIGENTE
        if is_document_creation and supports_documents:
            print(f"📄 [ROUTE] → WORKFLOW DE CRIAÇÃO DE DOCUMENTOS")
            
            # Verificar se agente tem múltiplos templates
            doc_template_ids = agent.get('doc_template_ids', [])
            
            if len(doc_template_ids) > 1:
                print(f"🔘 [TEMPLATES] Múltiplos templates encontrados: {len(doc_template_ids)}")
                
                # Buscar informações dos templates
                templates = await db.get_templates_by_ids(doc_template_ids)
                
                if templates:
                    # Criar botões modulares para seleção de template
                    buttons = []
                    for template in templates:
                        buttons.append({
                            "id": f"template_{template.id}",
                            "text": template.name,
                            "description": template.description,
                            "action": "select_template",
                            "params": {"template_id": template.id}
                        })
                    
                    return WorkflowResponse(
                        content=f"Legal, entendi! Posso gerar alguns tipos de documentos:",
                        buttons=buttons,
                        response_type="selection",
                        document_info={
                            'intent': 'template_selection',
                            'workflow': 'document_creation',
                            'agent_id': request.agent_id,
                            'supports_documents': True,
                            'available_templates': [t.id for t in templates]
                        }
                    )
            
            # Se apenas 1 template ou seleção já feita, prosseguir com workflow
            # Criar instância do workflow
            workflow = DocumentCreationWorkflow(
                agent_id=request.agent_id,
                db_url=db_url,
                user_id=request.user_id
            )
            
            # Executar workflow
            responses = []
            for response in workflow.run(request.message):
                responses.append(response.content)
            
            # Combinar respostas
            combined_response = "\n\n".join(responses)
            
            return WorkflowResponse(
                content=combined_response,
                document_info={
                    'intent': 'create_document',
                    'workflow': 'document_creation',
                    'agent_id': request.agent_id,
                    'supports_documents': True
                }
            )
            
        else:
            print(f"💬 [ROUTE] → CONSULTA/FAQ COM ORQUESTRADOR")
            
            # Retornar resposta do orquestrador para consultas
            return WorkflowResponse(
                content=orchestrator_response.content,
                document_info={
                    'intent': 'consultation',
                    'workflow': 'orchestrator_response',
                    'agent_id': request.agent_id,
                    'supports_documents': supports_documents
                }
            )
            
    except Exception as e:
        print(f"❌ [ERROR] Erro no roteamento inteligente: {str(e)}")
        
        # Fallback: resposta de erro amigável
        return WorkflowResponse(
            content=f"Desculpe, houve um problema temporário. Tente novamente em alguns instantes.\n\nSe o problema persistir, entre em contato com o suporte.",
            document_info={
                'intent': 'error',
                'workflow': 'fallback',
                'error': str(e)
            }
        )


@router.post("/select-template")
async def select_template_and_start_document(request: TemplateSelectionRequest) -> WorkflowResponse:
    """
    🔘 ENDPOINT PARA SELEÇÃO DE TEMPLATE VIA BOTÃO MODULAR
    
    Este endpoint é chamado quando o usuário clica em um botão de seleção de template.
    Inicia imediatamente o preenchimento "ao vivo" do documento.
    
    Args:
        request: Dados da seleção de template
        
    Returns:
        Resposta com início do preenchimento do documento
    """
    # Obter URL do banco de dados da variável de ambiente
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL não configurada")
    
    print(f"🔘 [TEMPLATE_SELECTION] Template selecionado: {request.template_id}")
    print(f"🔘 [TEMPLATE_SELECTION] Agent ID: {request.agent_id}")
    print(f"🔘 [TEMPLATE_SELECTION] User ID: {request.user_id}")
    
    try:
        # Verificar se template existe e pertence ao agente
        db = NDADatabaseCrud(db_url)
        template = await db.get_template_by_id(request.template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        # Verificar se agente tem acesso ao template
        agent = await db.get_agent_by_id(request.agent_id)
        if not agent or request.template_id not in agent.get('doc_template_ids', []):
            raise HTTPException(status_code=403, detail="Agente não tem acesso a este template")
        
        print(f"🔘 [TEMPLATE_SELECTION] Template validado: {template.name}")
        
        # Criar instância do workflow com template específico
        workflow = DocumentCreationWorkflow(
            agent_id=request.agent_id,
            db_url=db_url,
            user_id=request.user_id
        )
        
        # Iniciar documento com template selecionado
        message = f"Iniciar criação de documento usando template: {template.name}"
        
        # Executar workflow
        responses = []
        for response in workflow.run(message):
            responses.append(response.content)
        
        # Combinar respostas
        combined_response = "\n\n".join(responses)
        
        return WorkflowResponse(
            content=f"✅ **{template.name}** selecionado!\n\n{combined_response}",
            document_info={
                'intent': 'document_creation_started',
                'workflow': 'document_creation',
                'agent_id': request.agent_id,
                'template_id': request.template_id,
                'template_name': template.name,
                'status': 'in_progress'
            }
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ [ERROR] Erro na seleção de template: {str(e)}")
        
        return WorkflowResponse(
            content=f"Desculpe, houve um problema ao iniciar o documento. Tente novamente.",
            document_info={
                'intent': 'error',
                'workflow': 'template_selection',
                'error': str(e)
            }
        )


@router.post("/run/stream")
async def run_document_workflow_stream(request: WorkflowRequest):
    """
    Executa o workflow de criação de documentos com streaming.
    
    Args:
        request: Dados da requisição
        
    Returns:
        Stream de respostas do workflow
    """
    # Obter URL do banco de dados da variável de ambiente
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL não configurada")
    
    # Criar instância do workflow
    workflow = DocumentCreationWorkflow(
        agent_id=request.agent_id,
        db_url=db_url,
        user_id=request.user_id
    )
    
    # Função geradora para streaming
    async def response_generator():
        for response in workflow.run(request.message):
            # Formatar resposta como evento SSE (Server-Sent Events)
            yield f"data: {response.content}\n\n"
    
    # Retornar resposta de streaming
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )


@router.get("/templates/{agent_id}")
async def get_agent_templates(agent_id: str):
    """
    Obtém os templates disponíveis para um agente específico.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[TEMPLATES] Iniciando busca de templates para agent_id: {agent_id}")
    
    try:
        # Inicializar conexão com o banco
        db_url = os.getenv("DATABASE_URL")
        logger.info(f"[TEMPLATES] DATABASE_URL obtida: {db_url[:50]}..." if db_url else "[TEMPLATES] DATABASE_URL não encontrada")
        
        if not db_url:
            logger.error("[TEMPLATES] DATABASE_URL não configurada")
            raise HTTPException(status_code=500, detail="Database URL not configured")
        
        logger.info("[TEMPLATES] Criando instância do NDADatabaseCrud")
        db = NDADatabaseCrud(db_url)
        
        # Obter dados do agente
        logger.info(f"[TEMPLATES] Buscando dados do agente: {agent_id}")
        agent = await db.get_agent_by_id(agent_id)
        logger.info(f"[TEMPLATES] Resultado da busca do agente: {agent}")
        
        if not agent:
            logger.error(f"[TEMPLATES] Agente não encontrado: {agent_id}")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Obter templates pelos doc_template_ids
        doc_template_ids = agent.get('doc_template_ids', [])
        logger.info(f"[TEMPLATES] doc_template_ids encontrados: {doc_template_ids}")
        
        if not doc_template_ids:
            logger.warning(f"[TEMPLATES] Nenhum doc_template_ids encontrado para o agente {agent_id}")
            return {"templates": [], "agent_name": agent.get('name', 'Unknown')}
        
        logger.info(f"[TEMPLATES] Buscando templates pelos IDs: {doc_template_ids}")
        templates = await db.get_templates_by_ids(doc_template_ids)
        logger.info(f"[TEMPLATES] Templates encontrados: {len(templates)} templates")
        
        for template in templates:
            logger.info(f"[TEMPLATES] Template: ID={template.id}, Name={template.name}, Active={template.active}")
        
        result = {
            "templates": [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "active": template.active
                }
                for template in templates
            ],
            "agent_name": agent.get('name', 'Unknown')
        }
        
        logger.info(f"[TEMPLATES] Retornando resultado: {result}")
        return result
        
    except HTTPException as he:
        logger.error(f"[TEMPLATES] HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"[TEMPLATES] Erro inesperado: {str(e)}")
        logger.exception("[TEMPLATES] Stack trace completo:")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/preview")
async def get_document_preview(request: WorkflowRequest) -> Dict[str, Any]:
    """
    Obtém preview do documento em andamento.
    
    Args:
        request: Dados da requisição
        
    Returns:
        Preview do documento
    """
    # Obter URL do banco de dados da variável de ambiente
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL não configurada")
    
    # Criar instância do workflow apenas para acessar o banco
    workflow = DocumentCreationWorkflow(
        agent_id=request.agent_id,
        db_url=db_url,
        user_id=request.user_id
    )
    
    # Obter documento em andamento
    live_doc = await workflow.db.get_in_progress_document(request.user_id)
    if not live_doc:
        raise HTTPException(status_code=404, detail="Documento em andamento não encontrado")
    
    # Obter template
    template = await workflow.db.get_template_by_id(live_doc.doc_template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    # Obter cláusulas
    clauses = await workflow.db.get_clauses_by_template(template.id)
    
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
    
    # Calcular progresso
    total_clauses = len(clauses)
    mandatory_clauses = len([c for c in clauses if c.type == 'mandatory'])
    completed_clauses = len(content.keys())
    percentage = int((completed_clauses / total_clauses) * 100) if total_clauses > 0 else 0
    
    return {
        "preview": preview,
        "progress": {
            "current_clause": live_doc.current_clause_order,
            "total_clauses": total_clauses,
            "mandatory_clauses": mandatory_clauses,
            "completed_clauses": completed_clauses,
            "percentage": percentage
        },
        "status": live_doc.status
    }
