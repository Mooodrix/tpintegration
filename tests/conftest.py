import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base

# Fixture SQLite en mémoire (partagée par tous les tests)
@pytest.fixture(scope="session")
def db_session():
    # BDD isolée, ultra-rapide en RAM
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    yield session  # Fourni au test
    session.close() # Nettoyage automatique après