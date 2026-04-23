from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///./tara.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class CatTable(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)


Base.metadata.create_all(bind=engine)


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