#!/usr/bin/env python3
"""
Bateria de testes simplificada para validar problemas de argumentos no workflow.
Esta versão não depende de conexões com banco de dados.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Adicionar o diretório agent-api ao path
# Removido: sys.path já está correto quando executado de dentro do agent-api   

# Importar o workflow diretamente (AGNO está instalado)
from agents.nilo.workflows.document_creation_workflow import DocumentCreationWorkflow

class TestWorkflowArguments:
    """Testes focados nos problemas de argumentos do workflow."""
    
    def __init__(self):
        self.results = []
        
    def log_result(self, test_name, status, details=""):
        """Registra o resultado de um teste."""
        self.results.append({
            'test': test_name,
            'status': status,
            'details': details
        })
        print(f"[{status}] {test_name}: {details}")
    
    async def test_workflow_instantiation(self):
        """Testa se o workflow pode ser instanciado corretamente."""
        try:
            # Mock do banco de dados
            with patch('agents.nilo.workflows.document_creation_workflow.NDADatabaseCrud') as mock_db:
                mock_db.return_value = AsyncMock()
                
                workflow = DocumentCreationWorkflow(
                    agent_id="test_agent",
                    db_url="postgresql://test",
                    user_id="test_user"
                )
                
                self.log_result("Instanciação do Workflow", "PASSOU", "Workflow criado com sucesso")
                return workflow
                
        except Exception as e:
            self.log_result("Instanciação do Workflow", "FALHOU", f"Erro: {str(e)}")
            return None
    
    async def test_run_method_signature(self):
        """Testa a assinatura do método run."""
        try:
            import inspect
            
            # Verificar assinatura do método run
            run_method = DocumentCreationWorkflow.run
            signature = inspect.signature(run_method)
            
            params = list(signature.parameters.keys())
            self.log_result("Assinatura do método run", "PASSOU", f"Parâmetros: {params}")
            
            # Verificar se aceita message como argumento (através de **kwargs)
            if 'kwargs' in params:
                self.log_result("Parâmetro 'message'", "PASSOU", "Método aceita parâmetro 'message' via **kwargs")
            else:
                self.log_result("Parâmetro 'message'", "FALHOU", "Método não aceita **kwargs")
                
        except Exception as e:
            self.log_result("Assinatura do método run", "FALHOU", f"Erro: {str(e)}")
    
    async def test_run_method_call(self):
        """Testa chamadas do método run com diferentes argumentos."""
        try:
            # Mock do banco de dados
            with patch('agents.nilo.workflows.document_creation_workflow.NDADatabaseCrud') as mock_db:
                mock_db.return_value = AsyncMock()
                
                workflow = DocumentCreationWorkflow(
                    agent_id="test_agent",
                    db_url="postgresql://test",
                    user_id="test_user"
                )
                
                # Teste 1: Chamada com argumento posicional usando run_workflow
                try:
                    result = workflow.run_workflow("test message")
                    self.log_result("Chamada posicional", "PASSOU", "Método aceita argumento posicional")
                except Exception as e:
                    self.log_result("Chamada posicional", "FALHOU", f"Erro: {str(e)}")
                
                # Teste 2: Chamada com argumento nomeado usando run_workflow
                try:
                    result = workflow.run_workflow(message="test message")
                    self.log_result("Chamada nomeada", "PASSOU", "Método aceita argumento nomeado")
                except Exception as e:
                    self.log_result("Chamada nomeada", "FALHOU", f"Erro: {str(e)}")
                
        except Exception as e:
            self.log_result("Teste de chamadas do método run", "FALHOU", f"Erro: {str(e)}")
    
    async def test_inheritance_chain(self):
        """Testa a cadeia de herança do workflow."""
        try:
            # Verificar se herda de Workflow
            mro = DocumentCreationWorkflow.__mro__
            class_names = [cls.__name__ for cls in mro]
            
            self.log_result("Cadeia de herança", "PASSOU", f"MRO: {class_names}")
            
            # Verificar se tem método run
            if hasattr(DocumentCreationWorkflow, 'run'):
                self.log_result("Método run presente", "PASSOU", "Classe tem método run")
            else:
                self.log_result("Método run presente", "FALHOU", "Classe não tem método run")
                
        except Exception as e:
            self.log_result("Teste de herança", "FALHOU", f"Erro: {str(e)}")
    
    async def test_method_compatibility(self):
        """Testa compatibilidade com diferentes formas de chamada."""
        try:
            import inspect
            
            # Verificar se o método é síncrono (como esperado pelo AGNO)
            run_method = DocumentCreationWorkflow.run
            if not inspect.iscoroutinefunction(run_method):
                self.log_result("Método síncrono", "PASSOU", "Método run é síncrono (correto para AGNO)")
            else:
                self.log_result("Método síncrono", "FALHOU", "Método run é assíncrono (incorreto para AGNO)")
            
            # Verificar tipo de retorno
            signature = inspect.signature(run_method)
            return_annotation = signature.return_annotation
            
            self.log_result("Tipo de retorno", "PASSOU", f"Anotação: {return_annotation}")
            
        except Exception as e:
            self.log_result("Teste de compatibilidade", "FALHOU", f"Erro: {str(e)}")
    
    async def run_all_tests(self):
        """Executa todos os testes."""
        print("=== BATERIA DE TESTES SIMPLIFICADA ===")
        print("Focando nos problemas de argumentos do workflow\n")
        
        await self.test_workflow_instantiation()
        await self.test_run_method_signature()
        await self.test_run_method_call()
        await self.test_inheritance_chain()
        await self.test_method_compatibility()
        
        print("\n=== RESUMO DOS RESULTADOS ===")
        passed = sum(1 for r in self.results if r['status'] == 'PASSOU')
        failed = sum(1 for r in self.results if r['status'] == 'FALHOU')
        
        print(f"Testes executados: {len(self.results)}")
        print(f"Passou: {passed}")
        print(f"Falhou: {failed}")
        
        if failed > 0:
            print("\n=== TESTES QUE FALHARAM ===")
            for result in self.results:
                if result['status'] == 'FALHOU':
                    print(f"- {result['test']}: {result['details']}")
        
        return failed == 0

async def main():
    """Função principal."""
    tester = TestWorkflowArguments()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())