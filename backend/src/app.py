# Import FastAPI, which creates the backend web application
# Depends is used for dependency injection, which lets FastAPI automatically
# provide things like database sessions to route functions.
from fastapi import FastAPI, Depends

# BaseModel is used to define the shape of request and response data. 
# These are Pydantic models, which validate incoming JSON data.
from pydantic import BaseModel

# SQLAlchemy imports for connecting to a database and defining tables.
from sqlalchemy import create_engine, Column, Integer, String

# sessionmaker creates database sessions.
# declarative_base is used to create SQLAlchemy model classes.
# Sesssion is used for type hints.
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# HTTPException lets us return proper HTTP error responses,
# such as 404 Not Found.
from fastapi import HTTPException

# CORS middleware allows the frontend to make requests to this backend,
# even if the frontend is running on a different port or domain.
from fastapi.middleware.cors import CORSMiddleware

# This is the database connection URL.
# sqlite:/// means we are using SQLite.
# ./tara.db means the database file will be created in the current project folder.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'tara.db')}"

# Create the SQLAlchemy engine.
# The engine is the main connection point between Python and the database.
# 
# check_same_thread=False is needed for SQLite when using FastAPI,
# because requests may be handled across different threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a SessionLocal class.
# Each instance of SessionLocal will be an individual database session.
# A session is used to query, add, update, and delete database records. 
SessionLocal = sessionmaker(bind=engine)

# Create a Base class for SQLAlchemy models.
# Database table classes will inherit from this Base.
Base = declarative_base()

# This class defines the actual SQL database table for cats.
# It is not the same as a Pydantic model.
# This model controls how cat data is stored in tara.db.
class CatTable(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)

# Create all database tables defined by classes that inherit from Base.
# If the cats table does not already exist, this line creates it.
# If it already exists, SQLAlchemy leaves it alone.
Base.metadata.create_all(bind=engine)

# 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Cat(BaseModel):
    name: str
    status: str


class CatUpdate(BaseModel):
    name: str
    status: str


class CatResponse(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        from_attributes = True


@app.get("/")
def root():
    return {"message": "TARA backend is running"}


@app.get("/cats", response_model=list[CatResponse])
def get_cats(db: Session = Depends(get_db)):
    return db.query(CatTable).all()


@app.get("/cats/{cat_id}", response_model=CatResponse)
def get_cat(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(CatTable).filter(CatTable.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat


@app.post("/cats", response_model=CatResponse)
def add_cat(cat: Cat, db: Session = Depends(get_db)):
    new_cat = CatTable(
        name=cat.name,
        status=cat.status
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@app.put("/cats/{cat_id}", response_model=CatResponse)
def update_cat(cat_id: int, updated_cat: CatUpdate, db: Session = Depends(get_db)):
    cat = db.query(CatTable).filter(CatTable.id == cat_id).first()
    if cat:
        cat.name = updated_cat.name
        cat.status = updated_cat.status
        db.commit()
        db.refresh(cat)
        return cat
    return {"error": "Cat not found"}


@app.delete("/cats/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(CatTable).filter(CatTable.id == cat_id).first()
    if cat:
        db.delete(cat)
        db.commit()
        return {"message": "Cat deleted successfully"}
    return {"error": "Cat not found"}