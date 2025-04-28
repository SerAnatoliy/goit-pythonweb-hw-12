from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database.models import Contact

def search_contacts(db: Session, name: str = None, email: str = None, user_id: int = None):
    query = db.query(Contact)

    if user_id is not None:
        query = query.filter(Contact.user_id == user_id)

    if name:
        query = query.filter(
            (Contact.first_name.ilike(f"%{name}%")) | (Contact.last_name.ilike(f"%{name}%"))
        )

    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    return query.all()

def get_upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    next_week = today + timedelta(days=7)

    print(f"Today: {today}")
    print(f"Looking for birthdays from: {today.day}-{today.month} to {next_week.day}-{next_week.month} (year is ignored)")

    contacts = db.query(Contact).filter(
        Contact.user_id == user_id,  
        ((func.extract('month', Contact.birthday) == today.month) & (func.extract('day', Contact.birthday) >= today.day)) |
        ((func.extract('month', Contact.birthday) == next_week.month) & (func.extract('day', Contact.birthday) <= next_week.day))
    ).all()

    print(f"Contacts found: {len(contacts)}")
    
    return contacts
