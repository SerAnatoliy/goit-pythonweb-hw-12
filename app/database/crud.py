from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import Contact, User
from app.database.schemas import (
    ContactCreate, ContactUpdate,
    UserCreate, UserResponse
)
from app.services.security import hash_password, verify_password as verify_password_service


def create_user(db: Session, user: UserCreate) -> UserResponse:
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_verified=db_user.is_verified,
        avatar_url=db_user.avatar_url,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
        role=db_user.role  
    )


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_avatar(db: Session, user: User, avatar_path: str):
    user.avatar_url = avatar_path
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, email: str, new_password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    db_contact = Contact(
        **contact.model_dump(),
        user_id=user_id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int):
    return db.query(Contact).filter(Contact.user_id == user_id).all()

def get_contact_by_id(db: Session, contact_id: int, user_id: int):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        for key, value in contact.model_dump(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return verify_password_service(plain_password, hashed_password)
