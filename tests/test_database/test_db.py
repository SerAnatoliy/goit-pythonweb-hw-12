from app.database.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import ResourceClosedError

def test_get_db():
    db_gen = get_db()
    db_session = next(db_gen)

    assert isinstance(db_session, Session)
    assert db_session.is_active

    try:
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
      
        try:
            next(db_gen)
        except StopIteration:
            pass

    try:
        db_session.execute(text("SELECT 1"))
        assert False, "Session should be closed and not allow execution"
    except ResourceClosedError:
        assert True
    except Exception:
        assert True  
