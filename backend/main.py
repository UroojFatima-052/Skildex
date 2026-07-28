from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import schemas

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Skildex backend is alive"}

@app.post("/job-postings", response_model=schemas.JobPostingResponse)
def create_job_posting(posting: schemas.JobPostingCreate, db: Session = Depends(get_db)):
    db_posting = models.JobPosting(**posting.model_dump())
    db.add(db_posting)
    db.commit()
    db.refresh(db_posting)
    return db_posting

@app.get("/job-postings", response_model=list[schemas.JobPostingResponse])
def list_job_postings(db: Session = Depends(get_db)):
    return db.query(models.JobPosting).all()