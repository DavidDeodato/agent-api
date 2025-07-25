#!/usr/bin/env python3
"""
Teste final para verificar se o workflow está funcionando corretamente.
"""

import asyncio
from unittest.mock import patch, AsyncMock
from agents.nilo.workflows.document_creation_workflow import DocumentCreationWorkflow

async def test_workflow():
    print("🧪 Testando workflow real...")
    
    # Mock do banco de dados
    with patch('agents.nilo.workflows.document_creation_workflow.NDADatabaseCrud') as mock_db:
        mock_db.return_value = AsyncMock()
        
        # Criar workflow
        workflow = DocumentCreationWorkflow(
            agent_id="test_agent",
            db_url="postgresql://test",
            user_id="test_user"
        )
        
        print("✅ Workflow criado com sucesso")
        
        # Testar chamada posicional
        try:
            result = workflow.run_workflow("Olá, preciso criar um documento")
            print("✅ Chamada posicional funcionou")
            print(f"📊 Tipo do resultado: {type(result)}")
        except Exception as e:
            print(f"❌ Erro na chamada posicional: {e}")
        
        # Testar chamada nomeada
        try:
            result = workflow.run_workflow(message="Olá, preciso criar um documento")
            print("✅ Chamada nomeada funcionou")
            print(f"📊 Tipo do resultado: {type(result)}")
        except Exception as e:
            print(f"❌ Erro na chamada nomeada: {e}")
        
        print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_workflow())