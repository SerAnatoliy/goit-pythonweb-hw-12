import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.db import SessionLocal
from app.database.models import User
from app.services.security import hash_password


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


def create_user_in_db(email: str, password: str, role: str = "user") -> None:

    db: Session = SessionLocal()
    try:
        user = User(
            username=email.split("@")[0],  
            email=email,
            password_hash=hash_password(password),
            is_verified=True,
            role=role,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()


def get_auth_header(email: str, password: str) -> dict:
    with TestClient(app) as client:
        response = client.post(
            "/users/login",
            data={"username": email, "password": password},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
