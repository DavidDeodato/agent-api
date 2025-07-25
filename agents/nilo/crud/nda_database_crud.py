from models.doc_template_model import DocTemplate
from models.clause_model import Clause
from models.document_agent import DocumentAgent
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import psycopg
from psycopg.rows import dict_row


class NDADatabaseCrud:
    def __init__(self, db_url: str):
        self.db_url = db_url
    
    def get_connection(self):
        return psycopg.connect(self.db_url, row_factory=dict_row)
    
    # Doc Templates CRUD
    def create_doc_template(self, name: str) -> DocTemplate:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO doc_templates (name) VALUES (%s) RETURNING *",
                    (name,)
                )
                result = cur.fetchone()
                return DocTemplate(**result)
    
    def get_doc_template(self, template_id: int) -> Optional[DocTemplate]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM doc_templates WHERE id = %s", (template_id,))
                result = cur.fetchone()
                return DocTemplate(**result) if result else None
    
    def list_doc_templates(self) -> List[DocTemplate]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM doc_templates ORDER BY name")
                results = cur.fetchall()
                return [DocTemplate(**row) for row in results]
    
    # Clauses CRUD
    def create_clause(self, clause: Clause) -> Clause:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO clauses 
                    (doc_template_id, order_num, section_name, type, type_alternatives, 
                     alert_conditions, suggestions, system_prompt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    clause.doc_template_id, clause.order_num, clause.section_name,
                    clause.type.value, json.dumps(clause.type_alternatives),
                    json.dumps(clause.alert_conditions), json.dumps(clause.suggestions),
                    clause.system_prompt
                ))
                result = cur.fetchone()
                result['type'] = ClauseType(result['type'])
                result['type_alternatives'] = json.loads(result['type_alternatives'])
                result['alert_conditions'] = json.loads(result['alert_conditions'])
                result['suggestions'] = json.loads(result['suggestions'])
                return Clause(**result)
    
    def get_clauses_by_template(self, template_id: int) -> List[Clause]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM clauses 
                    WHERE doc_template_id = %s 
                    ORDER BY order_num
                """, (template_id,))
                results = cur.fetchall()
                clauses = []
                for row in results:
                    row['type'] = ClauseType(row['type'])
                    row['type_alternatives'] = json.loads(row['type_alternatives'])
                    row['alert_conditions'] = json.loads(row['alert_conditions'])
                    row['suggestions'] = json.loads(row['suggestions'])
                    clauses.append(Clause(**row))
                return clauses
    
    # Documents Agents CRUD
    def create_document_agent(self, doc_template_id: int) -> DocumentAgent:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO documents_agents (doc_template_id, content)
                    VALUES (%s, %s)
                    RETURNING *
                """, (doc_template_id, json.dumps({})))
                result = cur.fetchone()
                result['content'] = json.loads(result['content'])
                return DocumentAgent(**result)
    
    def update_document_agent_content(self, doc_id: int, section_name: str, content: str, current_clause_order: int) -> DocumentAgent:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Get current content
                cur.execute("SELECT content FROM documents_agents WHERE id = %s", (doc_id,))
                current_content = json.loads(cur.fetchone()['content'])
                
                # Update content
                current_content[section_name] = content
                
                cur.execute("""
                    UPDATE documents_agents 
                    SET content = %s, current_clause_order = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *
                """, (json.dumps(current_content), current_clause_order, doc_id))
                result = cur.fetchone()
                result['content'] = json.loads(result['content'])
                return DocumentAgent(**result)
    
    def get_document_agent(self, doc_id: int) -> Optional[DocumentAgent]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM documents_agents WHERE id = %s", (doc_id,))
                result = cur.fetchone()
                if result:
                    result['content'] = json.loads(result['content'])
                    return DocumentAgent(**result)
                return None
    
    def complete_document_agent(self, doc_id: int) -> DocumentAgent:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE documents_agents 
                    SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *
                """, (doc_id,))
                result = cur.fetchone()
                result['content'] = json.loads(result['content'])
                return DocumentAgent(**result)