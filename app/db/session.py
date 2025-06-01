from sqlmodel import create_engine, Session
from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URL), echo=True)

def get_db():
    with Session(engine) as session:
        yield session