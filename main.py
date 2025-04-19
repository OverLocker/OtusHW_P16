from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session  # Импортируем declarative_base из sqlalchemy.orm
import uvicorn  # Импортируем uvicorn

# Создаем базу данных SQLite
DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Теперь используем правильный импорт


# Определяем модель контакта
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI
app = FastAPI()


# Модель для входящих данных
class ContactCreate(BaseModel):
    name: str
    email: str


class ContactResponse(ContactCreate):
    id: int


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/contacts/", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(name=contact.name, email=contact.email)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"detail": "Contact deleted"}


@app.get("/contacts/", response_model=list[ContactResponse])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  # Запускаем приложение на локальном хосте и порту 8000