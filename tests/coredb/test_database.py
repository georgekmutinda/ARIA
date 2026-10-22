from sqlalchemy import text
from core.database import engine

def test_database_engine():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar()==1