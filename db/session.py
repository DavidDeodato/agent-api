from typing import Generator

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.url import get_db_url

# Função para obter a URL do banco de dados dinamicamente
def get_engine() -> Engine:
    # Obter a URL do banco de dados no momento da chamada
    db_url: str = get_db_url()
    # Criar e retornar o engine com configurações otimizadas para Supabase
    return create_engine(
        db_url, 
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
        echo=False
    )

# Engine será criado dinamicamente quando necessário
# Removido db_url global para evitar cache de valor antigo

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.

    Yields:
        Session: An SQLAlchemy database session.
    """
    # Criar engine dinamicamente para cada sessão
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
