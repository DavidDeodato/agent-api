"""
Módulo para operações CRUD no banco de dados relacionadas a NDAs.

Este módulo implementa operações para:
1. Templates de documentos
2. Cláusulas de templates
3. Documentos em andamento
"""

import json
from typing import List, Optional, Dict, Any
import asyncpg
from asyncpg.pool import Pool

from models.doc_template import DocTemplate
from models.template_clause import TemplateClause
from models.live_document import LiveDocument


class NDADatabaseCrud:
    """
    Classe para operações CRUD no banco de dados relacionadas a NDAs.
    
    Implementa operações para templates, cláusulas e documentos em andamento.
    """
    
    def __init__(self, db_url: str):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            db_url: URL de conexão com o banco de dados
        """
        # Corrigir URL do banco para asyncpg (remover +psycopg se presente)
        if 'postgresql+psycopg' in db_url:
            self.db_url = db_url.replace('postgresql+psycopg', 'postgresql')
        else:
            self.db_url = db_url
        self.pool: Optional[Pool] = None
    
    async def connect(self):
        """
        Estabelece conexão com o banco de dados.
        """
        if not self.pool:
            # Configurar para compatibilidade com pgbouncer
            self.pool = await asyncpg.create_pool(
                self.db_url,
                statement_cache_size=0  # Desabilitar cache de prepared statements
            )
    
    async def close(self) -> None:
        """
        Fecha a conexão com o banco de dados.
        """
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def get_templates_by_agent(self, agent_id: str) -> List[DocTemplate]:
        """
        Obtém os templates disponíveis para um agente.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Lista de templates
        """
        await self.connect()
        
        query = """
        SELECT id, agent_id, name, description, active, created_at, updated_at
        FROM public.doc_templates
        WHERE agent_id = $1 AND active = true
        ORDER BY name
        """
        
        rows = await self.pool.fetch(query, agent_id)
        
        return [
            DocTemplate(
                id=row['id'],
                agent_id=str(row['agent_id']),  # Converter UUID para string
                name=row['name'],
                description=row['description'],
                active=row['active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]
    
    async def get_templates_by_ids(self, template_ids: List[int]) -> List[DocTemplate]:
        """
        Obtém templates pelos IDs específicos.
        
        Args:
            template_ids: Lista de IDs dos templates
            
        Returns:
            Lista de templates
        """
        await self.connect()
        
        if not template_ids:
            return []
        
        query = """
        SELECT id, agent_id, name, description, active, created_at, updated_at
        FROM public.doc_templates
        WHERE id = ANY($1) AND active = true
        ORDER BY name
        """
        
        rows = await self.pool.fetch(query, template_ids)
        
        return [
            DocTemplate(
                id=row['id'],
                agent_id=str(row['agent_id']),  # Converter UUID para string
                name=row['name'],
                description=row['description'],
                active=row['active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um agente pelo ID.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Dados do agente ou None se não encontrado
        """
        # Tratar casos especiais (orquestradores)
        if agent_id == 'creator_nda_team':
            return {
                'id': 'creator_nda_team',
                'name': 'Creator NDA Team',
                'doc_template_ids': []
            }
        
        await self.connect()
        
        query = """
        SELECT id, name, doc_template_ids
        FROM public.agents
        WHERE id = $1
        """
        
        row = await self.pool.fetchrow(query, agent_id)
        
        if not row:
            return None
        
        # Parse do doc_template_ids se for string JSON
        doc_template_ids = row['doc_template_ids']
        if isinstance(doc_template_ids, str):
            try:
                import json
                doc_template_ids = json.loads(doc_template_ids)
            except (json.JSONDecodeError, TypeError):
                doc_template_ids = []
        elif doc_template_ids is None:
            doc_template_ids = []
        
        return {
            'id': row['id'],
            'name': row['name'],
            'doc_template_ids': doc_template_ids
        }
    
    async def get_template_by_id(self, template_id: int) -> Optional[DocTemplate]:
        """
        Obtém um template pelo ID.
        
        Args:
            template_id: ID do template
            
        Returns:
            Template ou None se não encontrado
        """
        await self.connect()
        
        query = """
        SELECT id, agent_id, name, description, active, created_at, updated_at
        FROM public.doc_templates
        WHERE id = $1
        """
        
        row = await self.pool.fetchrow(query, template_id)
        
        if not row:
            return None
        
        return DocTemplate(
            id=row['id'],
            agent_id=row['agent_id'],
            name=row['name'],
            description=row['description'],
            active=row['active'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def get_clauses_by_template(self, template_id: int, order_by: str = 'order_num') -> List[TemplateClause]:
        """
        Obtém as cláusulas de um template.
        
        Args:
            template_id: ID do template
            order_by: Campo para ordenação
            
        Returns:
            Lista de cláusulas
        """
        await self.connect()
        
        query = f"""
        SELECT id, doc_template_id, section_name, order_num, type, system_prompt, 
               content_template, validation_rules, placeholders, created_at, updated_at
        FROM public.template_clauses
        WHERE doc_template_id = $1
        ORDER BY {order_by}
        """
        
        rows = await self.pool.fetch(query, template_id)
        
        return [
            TemplateClause(
                id=row['id'],
                doc_template_id=row['doc_template_id'],
                section_name=row['section_name'],
                order_num=row['order_num'],
                type=row['type'],
                system_prompt=row['system_prompt'],
                content_template=row['content_template'],
                validation_rules=row['validation_rules'],
                placeholders=row['placeholders'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]
    
    async def get_in_progress_document(self, user_id: str) -> Optional[LiveDocument]:
        """
        Obtém um documento em andamento para um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Documento em andamento ou None
        """
        await self.connect()
        
        query = """
        SELECT id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        FROM public.live_documents
        WHERE user_id = $1 AND status = 'in_progress'
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        row = await self.pool.fetchrow(query, user_id)
        
        if not row:
            return None
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    async def get_live_document_by_id(self, doc_id: int) -> Optional[LiveDocument]:
        """
        Obtém um documento pelo ID.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Documento ou None se não encontrado
        """
        await self.connect()
        
        query = """
        SELECT id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        FROM public.live_documents
        WHERE id = $1
        """
        
        row = await self.pool.fetchrow(query, doc_id)
        
        if not row:
            return None
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def create_live_document(self, user_id: str, template_id: int) -> LiveDocument:
        """
        Cria um novo documento em andamento.
        
        Args:
            user_id: ID do usuário
            template_id: ID do template
            
        Returns:
            Documento criado
        """
        await self.connect()
        
        query = """
        INSERT INTO public.live_documents (user_id, doc_template_id, content, status, current_clause_order)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        """
        
        row = await self.pool.fetchrow(
            query, 
            user_id, 
            template_id, 
            json.dumps({}), 
            'in_progress', 
            1
        )
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def update_live_document_content(self, doc_id: int, content: Dict[str, Any], current_clause_order: int) -> LiveDocument:
        """
        Atualiza o conteúdo de um documento em andamento.
        
        Args:
            doc_id: ID do documento
            content: Novo conteúdo
            current_clause_order: Ordem da cláusula atual
            
        Returns:
            Documento atualizado
        """
        await self.connect()
        
        query = """
        UPDATE public.live_documents
        SET content = $1, current_clause_order = $2, updated_at = NOW()
        WHERE id = $3
        RETURNING id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        """
        
        row = await self.pool.fetchrow(
            query, 
            json.dumps(content), 
            current_clause_order, 
            doc_id
        )
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def complete_document(self, doc_id: int) -> LiveDocument:
        """
        Marca um documento como concluído.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Documento atualizado
        """
        await self.connect()
        
        query = """
        UPDATE public.live_documents
        SET status = 'completed', updated_at = NOW()
        WHERE id = $1
        RETURNING id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        """
        
        row = await self.pool.fetchrow(query, doc_id)
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def pause_document(self, doc_id: int) -> LiveDocument:
        """
        Pausa um documento em andamento.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Documento atualizado
        """
        await self.connect()
        
        query = """
        UPDATE public.live_documents
        SET status = 'paused', updated_at = NOW()
        WHERE id = $1
        RETURNING id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        """
        
        row = await self.pool.fetchrow(query, doc_id)
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def resume_document(self, doc_id: int) -> LiveDocument:
        """
        Retoma um documento pausado.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Documento atualizado
        """
        await self.connect()
        
        query = """
        UPDATE public.live_documents
        SET status = 'in_progress', updated_at = NOW()
        WHERE id = $1
        RETURNING id, user_id, doc_template_id, content, status, current_clause_order, created_at, updated_at
        """
        
        row = await self.pool.fetchrow(query, doc_id)
        
        return LiveDocument(
            id=row['id'],
            user_id=row['user_id'],
            doc_template_id=row['doc_template_id'],
            content=row['content'],
            status=row['status'],
            current_clause_order=row['current_clause_order'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
