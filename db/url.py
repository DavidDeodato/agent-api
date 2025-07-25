import os
import sys
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente do arquivo .env
try:
    # Obter o caminho absoluto para o arquivo .env
    env_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / '.env'
    print(f"Carregando variáveis de ambiente de: {env_path}", file=sys.stderr)
    # Carregar o arquivo .env
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("AVISO: python-dotenv não está instalado. As variáveis de ambiente devem ser definidas manualmente.", file=sys.stderr)


def get_supabase_client() -> Client:
    """Cria e retorna um cliente Supabase configurado"""
    supabase_url = getenv("SUPABASE_URL", "")
    supabase_key = getenv("SUPABASE_ACCESS_TOKEN", "")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_ACCESS_TOKEN devem estar definidos no arquivo .env")
    
    print(f"Conectando ao Supabase: {supabase_url}", file=sys.stderr)
    return create_client(supabase_url, supabase_key)


def get_db_url() -> str:
    """Retorna a URL de conexão PostgreSQL para o Supabase"""
    # Primeiro, verificar se DATABASE_URL já está definida
    database_url = getenv("DATABASE_URL", "")
    if database_url:
        print(f"Usando DATABASE_URL: {database_url.replace(':LMLsbLWB3ItCRKLp', ':***')}", file=sys.stderr)
        return database_url
    
    # Obter a URL do Supabase
    supabase_url = getenv("SUPABASE_URL", "")
    if not supabase_url:
        print("ERRO: SUPABASE_URL não está definida no arquivo .env", file=sys.stderr)
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # Extrair o ID do projeto do Supabase da URL
    # Exemplo: https://fjrqrgjydsgkixmuowub.supabase.co -> fjrqrgjydsgkixmuowub
    project_id = None
    if "//" in supabase_url:
        parts = supabase_url.split("//")[1].split(".")[0]
        project_id = parts
    else:
        parts = supabase_url.split(".")[0]
        project_id = parts
    
    if not project_id:
        print(f"ERRO: Não foi possível extrair o ID do projeto da URL do Supabase: {supabase_url}", file=sys.stderr)
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # Obter a senha do PostgreSQL do Supabase
    db_pass = getenv("SUPABASE_DB_PASSWORD", "")
    if not db_pass:
        print("ERRO: SUPABASE_DB_PASSWORD não está definido no arquivo .env", file=sys.stderr)
        print("DICA: Encontre a senha em Settings > Database > Connection string no painel do Supabase", file=sys.stderr)
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # Configuração para Supabase PostgreSQL
    db_driver = "postgresql+psycopg"
    db_user = "postgres"
    db_port = 5432
    db_database = "postgres"
    
    # Construir o host do banco de dados
    # O formato correto é: db.[project-id].supabase.co
    db_host = f"db.{project_id}.supabase.co"
    
    # Construir a URL para o Supabase
    db_url = f"{db_driver}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_database}"
    
    # Imprimir informações de debug (sem a senha)
    debug_url = f"{db_driver}://{db_user}:***@{db_host}:{db_port}/{db_database}"
    print(f"Conectando ao banco de dados PostgreSQL: {debug_url}", file=sys.stderr)
    print(f"URL de conexão final: {db_url}", file=sys.stderr)
    
    return db_url

