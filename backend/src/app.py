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
    # Name of the table inside the SQLite database.
    __tablename__ = "cats"

    # Primary key columnn.
    # Each cat gets a unqiue integer ID.
    # inndex=True makes lookups by ID faster.
    id = Column(Integer, primary_key=True, index=True)

    # Cat name column.
    # Stored as text/strinng.
    # index=True makes searchinng by name faster.
    name = Column(String, index=True)

    # Cat status column.
    # Example statuses could be "available", "adopted", "medical hold", etc.
    status = Column(String)

# Create all database tables defined by classes that inherit from Base.
# If the cats table does not already exist, this line creates it.
# If it already exists, SQLAlchemy leaves it alone.
Base.metadata.create_all(bind=engine)

# This function provides a database session to each API route that needs one.
# FastAPI will call this function whenever a route has db: Session = Depends(get_db).
def get_db():

    # Open a new database session.
    db = SessionLocal()

    try:
        # yield gives the database session to the route function.
        yield db

    finally:
        # After the request is finished, close the session.
        # This prevents database connections from staying open unnecessarily.
        db.close()

# Create the FastAPI app instance.
# This is the main backend application.
app = FastAPI()

# Add CORS middleware so a frontend can communicate with this backend.
# This is especially useful when your frontend runs on something like:
# http://localhost:5500 or http://127.0.0.1:5500
# while the backend runs on:
# http://127.0.0.1:8000
app.add_middleware(
    CORSMiddleware,

    # "*" allows requests from any frontend origin.
    # This is fine for local development, but in a real deployed app,
    # you woould usually restrict this to your actual frontend URL.
    allow_origins=["*"],

    # Allows cookies/auth headers to be included in cross-origin requests.
    allow_credentials=True,

    # Allows all HTTP methods, such as GET, POST, PUT, and DELETE.
    allow_methods=["*"],

    # Allows all request headers.
    allow_headers=["*"],
)

# This Pydantic model defines the data required when creating a new cat.
# It describes the JSON body expected by the POST /cats route.
class Cat(BaseModel):
    name: str
    status: str

# This Pydantic model defines the data required when updating a cat.
# Right now, updating requires both name and status.
class CatUpdate(BaseModel):
    name: str
    status: str

# This Pydantic model defines the data returned by the API.
# It includes the database-generated id, plus the cat's name and status.
class CatResponse(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        # Allows Pydantic to convert SQLAlchemy objects into response models.
        # Without this, returning CatTable objects directly may not serialize correctly.
        from_attributes = True

# Root route.
# This is mainly used to quickly check whether the backend is running.
@app.get("/")
def root():
    return {"message": "TARA backend is running"}

# GET /cats
# Returns a list of all cats currently stored in the database.
@app.get("/cats", response_model=list[CatResponse])
def get_cats(db: Session = Depends(get_db)):
    # Query the cats table and return every row.
    return db.query(CatTable).all()

# GET /cats/{cat_id}
# Returns one specific cat by its ID.
@app.get("/cats/{cat_id}", response_model=CatResponse)
def get_cat(cat_id: int, db: Session = Depends(get_db)):
    # Search for the first cat whose ID matches the cat_id from the URL.
    cat = db.query(CatTable).filter(CatTable.id == cat_id).first()

    # If no cat was found, return a proper 404 error.
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    # If found, return the cat.
    return cat

# POST /cats
# Creates a new cat record in the database.
@app.post("/cats", response_model=CatResponse)
def add_cat(cat: Cat, db: Session = Depends(get_db)):
    # Create a new SQLAlchemy CatTable object using the validated request data.
    new_cat = CatTable(
        name=cat.name,
        status=cat.status
    )

    # Add the new cat object to the current database session.
    db.add(new_cat)

    # Commit saves the new cat permanently to the database.
    db.commit()

    # Refresh updates new_cat with database-generated values,
    # especially the new ID.
    db.refresh(new_cat)

    # Return the newly created cat.
    return new_cat

# PUT /cats/{cat_id}
# Updates an existing cat by replacing its name and status.
@app.put("/cats/{cat_id}", response_model=CatResponse)
def update_cat(cat_id: int, updated_cat: CatUpdate, db: Session = Depends(get_db)):
    # Look for the cat with the matching ID.
    cat = db.query(CatTable).filter(CatTable.id == cat_id).first()

    # If the cat exists, update its fields.
    if cat:
        cat.name = updated_cat.name
        cat.status = updated_cat.status

        # Save the changes to the database.
        db.commit()

        # Refresh the object so it reflects the latest database state.
        db.refresh(cat)

        # Return the updated cat.
        return cat
    
    # If the cat was not found, return an error message.
    # Note: because this route uses response_model=CatResponse,
    # this should ideally be changed to raise HTTPException instead.
    return {"error": "Cat not found"}

# DELETE /cats/{cat_id}
# Deletes a cat from the database by ID.
@app.delete("/cats/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(get_db)):
    # Look for the cat with the matching ID.
    cat = db.query(CatTable).filter(CatTable.id == cat_id).first()

    # If the cat exists, delete it.
    if cat:
        # Mark the cat for deletion.
        db.delete(cat)

        # Commit saves the deletion permanently.
        db.commit()

        # Return a success message.
        return {"message": "Cat deleted successfully"}
    
    # If the cat was not found, return an error message.
    # This could also be improved by raising HTTPException with a 404 status.
    return {"error": "Cat not found"}