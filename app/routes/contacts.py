from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import crud, schemas
from app.config import SessionLocal
from app.services.utils import search_contacts, get_upcoming_birthdays
from app.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["Contacts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    return crud.create_contact(db, contact, current_user.id)

@router.get("/", response_model=list[schemas.ContactResponse])
def get_contacts(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    return crud.get_contacts(db, current_user.id)

@router.get("/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    db_contact = crud.get_contact_by_id(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    db_contact = crud.update_contact(db, contact_id, contact, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.delete("/{contact_id}", response_model=schemas.ContactResponse)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    db_contact = crud.delete_contact(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/search/", response_model=list[schemas.ContactResponse])
def search_contacts_api(
    name: str = Query(None, description="Search by first or last name"),
    email: str = Query(None, description="Search by email"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    contacts = search_contacts(db, name, email, current_user.id)
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")
    return contacts

@router.get("/upcoming_birthdays/", response_model=list[schemas.ContactResponse])
def get_birthdays_api(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    contacts = get_upcoming_birthdays(db, current_user.id)
    if not contacts:
        raise HTTPException(status_code=404, detail="No upcoming birthdays found")
    return contacts