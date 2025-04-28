import pytest
from app.services.auth import create_access_token
from app.database import crud
from app.database.schemas import UserCreate
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
import random
import string

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_user(db):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f"testuser_{suffix}"
    
    existing_user = crud.get_user_by_email(db, "test@example.com")
    if existing_user:
        crud.delete_user(db, existing_user.id)

    user_data = UserCreate(
        username=username,
        email="test@example.com",
        password="TestPassword123"
    )
    user = crud.create_user(db=db, user=user_data)
    return user


@pytest.fixture(scope="module")
def auth_headers(test_user):
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


def test_contacts_cache(auth_headers):
    """Тест для кешування контактів."""
    response = client.get("/contacts/", headers=auth_headers)

    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 200, f"Expected status 200, but got {response.status_code}: {response.json()}"
