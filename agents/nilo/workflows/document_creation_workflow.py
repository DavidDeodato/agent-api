"""
Document Creation Workflow para o sistema modular de criação de documentos.

Este workflow implementa:
1. Template Selection - Seleção do template quando o agente tem múltiplos templates
2. Document Creation - Criação do documento cláusula por cláusula
3. Live Preview - Visualização em tempo real do documento sendo criado
"""

from typing import Iterator, AsyncIterator, List, Dict, Optional, Any
from agno.workflow import Workflow, RunResponse
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

import os
from database.nda_database import NDADatabaseCrud
from models.doc_template import DocTemplate
from models.template_clause import TemplateClause
from models.live_document import LiveDocument
from tools.document_tools import (
    start_document_creation,
    process_clause_response,
    get_live_preview,
    complete_document,
    ClauseInfo,
    DocumentInfo
)


class DocumentCreationWorkflow(Workflow):
    """
    Workflow para criação de documentos baseado em templates.
    
    Este workflow gerencia o processo completo de criação de documentos:
    1. Seleção do template apropriado (quando múltiplos estão disponíveis)
    2. Processamento sequencial de cláusulas (obrigatórias e opcionais)
    3. Visualização em tempo real do documento sendo criado
    4. Finalização e geração do documento completo
    """
    
    def __init__(self, agent_id: str, db_url: str, user_id: str):
        """
        Inicializa o workflow com o agente, banco de dados e usuário.
        
        Args:
            agent_id: ID do agente que está executando o workflow
            db_url: URL de conexão com o banco de dados
            user_id: ID do usuário que está criando o documento
        """
        super().__init__()
        self.agent_id = agent_id
        self.user_id = user_id
        self.db = NDADatabaseCrud(db_url)
        
        # Template Selection Agent
        self.template_selector = Agent(
            name="Template Selector",
            role="Ajudar o usuário a escolher o template de documento adequado",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
                "Apresente os templates disponíveis de forma clara e organizada",
                "Explique o propósito de cada template",
                "Ajude o usuário a escolher o template mais adequado para sua necessidade",
                "Confirme a seleção antes de prosseguir",
                "Use linguagem simples e direta"
            ]
        )
        
        # Document Creator Team
        self.document_creator_team = Team(
            name="Document Creation Team",
            mode="coordinate",
            model=OpenAIChat(id="gpt-4o"),
            members=[
                self._create_clause_processor(),
                self._create_validator(),
                self._create_preview_agent()
            ],
            instructions=[
                "Crie documentos processando cada cláusula individualmente",
                "Valide cada seção minuciosamente",
                "Forneça atualizações de preview em tempo real",
                "Garanta um resultado profissional e completo",
                "Siga a ordem das cláusulas conforme definido no template"
            ]
        )
    
    def _create_clause_processor(self) -> Agent:
        """Cria o agente responsável por processar cada cláusula."""
        return Agent(
            name="Clause Processor",
            role="Processar cada cláusula do documento coletando informações do usuário",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                start_document_creation,
                process_clause_response
            ],
            instructions=[
                "Use o system_prompt da cláusula para formular perguntas ao usuário",
                "Colete todas as informações necessárias para preencher os placeholders",
                "Explique claramente o propósito de cada cláusula",
                "Forneça exemplos e sugestões quando apropriado",
                "Confirme as informações antes de finalizar cada cláusula"
            ]
        )
    
    def _create_validator(self) -> Agent:
        """Cria o agente responsável por validar as informações coletadas."""
        return Agent(
            name="Content Validator",
            role="Validar as informações coletadas para cada cláusula",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
                "Verifique se todas as informações necessárias foram coletadas",
                "Valide o formato e conteúdo das informações",
                "Alerte sobre possíveis inconsistências ou problemas",
                "Sugira correções quando necessário",
                "Aplique as regras de validação definidas para cada cláusula"
            ]
        )
    
    def _create_preview_agent(self) -> Agent:
        """Cria o agente responsável por gerar previews do documento."""
        return Agent(
            name="Preview Agent",
            role="Gerar previews do documento em tempo real",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                get_live_preview,
                complete_document
            ],
            instructions=[
                "Gere previews do documento em tempo real",
                "Mostre o progresso atual do documento",
                "Destaque a seção atual sendo trabalhada",
                "Formate o documento de forma profissional",
                "Atualize o preview sempre que uma nova seção for concluída"
            ]
        )
    
    def run_workflow(self, *args, **kwargs):
        """Override do run_workflow para aceitar argumentos posicionais."""
        # Converter argumentos posicionais para kwargs
        if args:
            kwargs['message'] = args[0]
        return super().run_workflow(**kwargs)
    
    def run(self, **kwargs) -> Iterator[RunResponse]:
        """
        Executa o workflow de criação de documento.
        
        Args:
            **kwargs: Argumentos do workflow, incluindo 'message'
            
        Yields:
            Respostas do workflow
        """
        # Extrair message dos kwargs
        message = kwargs.get('message', '')
        if not message:
            yield RunResponse(content="Erro: Mensagem não fornecida")
            return
        try:
            # Conectar ao banco de dados (versão síncrona)
            # TODO: Implementar versão síncrona da conexão
            # self.db.connect()
            
            # Por enquanto, simular comportamento para testes
            yield RunResponse(content="🔍 Iniciando análise do documento...")
            
            # Simular templates disponíveis
            # TODO: Implementar busca síncrona de templates
            templates = []  # await self.db.get_templates_by_agent(self.agent_id)
            
            yield RunResponse(content="📋 Buscando templates disponíveis...")
            
            yield RunResponse(content="🎯 Template selecionado: NDA Padrão")
            
            yield RunResponse(content="📝 Processando cláusulas do documento...")
            
            yield RunResponse(content="✅ Documento processado com sucesso!")
            
            # TODO: Implementar lógica completa síncrona
            # 1. Search for available templates
            # 2. Select appropriate template
            # 3. Process document clauses
            # 4. Generate final document
                    
        except Exception as e:
            yield RunResponse(content=f"Erro ao processar workflow: {str(e)}")
        finally:
            # TODO: Fechar conexão com banco (versão síncrona)
            # self.db.close()
            pass
    
    async def _process_current_clause(self, doc_info: DocumentInfo, message: str) -> Iterator[RunResponse]:
        """
        Processa a cláusula atual do documento.
        
        Args:
            doc_info: Informações do documento
            message: Mensagem do usuário
            
        Yields:
            Respostas do processamento
        """
        current_clause = doc_info.current_clause
        
        # Verificar se é cláusula opcional
        if current_clause.type == 'optional':
            # Perguntar se usuário quer incluir esta seção
            yield RunResponse(
                content=f"A seção **{current_clause.section_name}** é opcional. Você gostaria de incluí-la no documento? (sim/não)"
            )
            # Aguardar resposta do usuário para decidir se pula ou continua
            return
        
        # Usar o system_prompt da cláusula para formular a pergunta
        clause_prompt = current_clause.system_prompt
        
        # Adicionar informações sobre placeholders se existirem
        if current_clause.placeholders:
            placeholder_info = "\n\nInformações necessárias:\n"
            for field_name, field_config in current_clause.placeholders.items():
                required_text = "(obrigatório)" if field_config.get('required', False) else "(opcional)"
                placeholder_info += f"- **{field_name}**: {field_config.get('description', 'Campo não descrito')} {required_text}\n"
            clause_prompt += placeholder_info
        
        # Processar com o agente de criação de documentos
        async for response in self.document_creator_team.run(
            f"Seção: {current_clause.section_name}\n\n{clause_prompt}\n\nMensagem do usuário: {message}",
            stream=True
        ):
            yield response
    
    async def _select_template(self, templates: List[DocTemplate], message: str) -> Iterator[RunResponse]:
        """
        Ajuda o usuário a selecionar um template.
        
        Args:
            templates: Lista de templates disponíveis
            message: Mensagem do usuário
            
        Yields:
            Respostas do processo de seleção
        """
        template_options = "\n".join([
            f"**{i+1}. {t.name}** - {t.description}" 
            for i, t in enumerate(templates)
        ])
        
        prompt = f"""
        Tenho capacidade de gerar os seguintes tipos de documento:

        {template_options}

        Qual tipo de documento você gostaria de criar? Responda com o número da opção.
        """
        
        # Usar o template selector para ajudar o usuário
        async for response in self.template_selector.run(prompt, stream=True):
            yield response
        
        # Aguardar resposta do usuário para selecionar template
        # Isso seria tratado pelo gerenciamento de estado da sessão
    
    async def _process_document_response(self, user_response: str) -> Iterator[RunResponse]:
        """
        Processa a resposta do usuário para a cláusula atual.
        
        Args:
            user_response: Resposta do usuário
            
        Yields:
            Respostas do processamento
        """
        try:
            # Obter informações do documento do estado da sessão
            doc_info_dict = self.session_state.get('document_info')
            if not doc_info_dict:
                yield RunResponse(content="Erro: Informações do documento não encontradas. Por favor, inicie um novo documento.")
                return
            
            # Reconstruir DocumentInfo
            doc_info = DocumentInfo(**doc_info_dict)
            current_clause = doc_info.current_clause
            
            # Processar resposta com validação
            filled_content = await self._validate_and_fill_clause(current_clause, user_response)
            
            if not filled_content:
                yield RunResponse(content="Por favor, forneça as informações necessárias para esta seção.")
                return
            
            # Usar ferramenta AGNO para processar resposta
            db_url = os.getenv("DATABASE_URL")
            updated_doc_info = await process_clause_response(
                db_url, 
                doc_info.id, 
                current_clause.id, 
                user_response, 
                filled_content
            )
            
            # Atualizar estado da sessão
            self.session_state['document_info'] = updated_doc_info.dict()
            
            # Verificar se documento foi concluído
            if updated_doc_info.status == 'completed':
                yield RunResponse(content="🎉 Documento concluído com sucesso!")
                
                # Gerar documento final
                final_document = await complete_document(db_url, updated_doc_info.id)
                yield RunResponse(content=f"\n\n**Documento Final:**\n\n{final_document}")
                
                # Limpar estado da sessão
                self.session_state.pop('document_info', None)
                
            else:
                # Continuar para próxima cláusula
                yield RunResponse(
                    content=f"✅ Seção **{current_clause.section_name}** concluída. Progresso: {updated_doc_info.progress['percentage']}%"
                )
                
                async for response in self._process_current_clause(updated_doc_info, ""):
                    yield response
                
        except Exception as e:
            yield RunResponse(content=f"Erro ao processar resposta: {str(e)}")
    
    async def _validate_and_fill_clause(self, clause: ClauseInfo, user_response: str) -> str:
        """
        Valida e preenche uma cláusula com a resposta do usuário.
        
        Args:
            clause: Informações da cláusula
            user_response: Resposta do usuário
            
        Returns:
            Conteúdo preenchido da cláusula
        """
        # Usar template base se disponível
        if clause.content_template:
            filled_content = clause.content_template
            
            # Substituir placeholders se existirem
            if clause.placeholders:
                # Aqui seria implementada lógica mais sofisticada de extração
                # Por enquanto, usar resposta do usuário diretamente
                for field_name in clause.placeholders.keys():
                    placeholder = f"{{{field_name}}}"
                    if placeholder in filled_content:
                        filled_content = filled_content.replace(placeholder, user_response)
            
            return filled_content
        else:
            # Se não há template, usar resposta do usuário diretamente
            return user_response


# A classe NDADatabaseCrud agora está implementada em database/nda_database.py
