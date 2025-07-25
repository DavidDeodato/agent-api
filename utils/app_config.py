import os

# Wrapper de conexao com o supabase
# Capiturar do Env "postgresql+psycopg://[user]:[password]@[host]:[port]/[database]"
SUPABASE_DB_URL = os.getenv("DATABASE_URL")