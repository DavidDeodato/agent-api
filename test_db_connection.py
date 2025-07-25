#!/usr/bin/env python3
"""
Script de teste para verificar a conectividade com o banco de dados Supabase.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from db.url import get_db_url
from db.session import get_engine
from sqlalchemy import text

def test_database_connection():
    """Testa a conexão com o banco de dados."""
    print("=== Teste de Conexão com o Banco de Dados ===")
    
    try:
        # Obter a URL do banco de dados
        print("\n1. Obtendo URL do banco de dados...")
        db_url = get_db_url()
        print(f"URL obtida com sucesso!")
        
        # Criar engine
        print("\n2. Criando engine SQLAlchemy...")
        engine = get_engine()
        print("Engine criado com sucesso!")
        
        # Testar conexão
        print("\n3. Testando conexão...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexão bem-sucedida!")
            print(f"Versão do PostgreSQL: {version}")
            
        # Testar uma consulta simples
        print("\n4. Testando consulta simples...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"✅ Banco de dados: {db_info[0]}")
            print(f"✅ Usuário: {db_info[1]}")
            
        print("\n🎉 Todos os testes passaram! A conexão está funcionando.")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na conexão: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        
        # Informações adicionais para debug
        print("\n=== Informações de Debug ===")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        
        # Verificar variáveis de ambiente
        env_vars = ['SUPABASE_URL', 'SUPABASE_DB_PASSWORD', 'DATABASE_URL']
        for var in env_vars:
            value = os.getenv(var, 'NÃO DEFINIDA')
            if 'PASSWORD' in var or 'TOKEN' in var:
                value = '***' if value != 'NÃO DEFINIDA' else 'NÃO DEFINIDA'
            print(f"{var}: {value}")
            
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)