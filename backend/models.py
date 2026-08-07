from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    raw_description = Column(Text, nullable=False)
    dedup_key = Column(String, unique=True, index=True)
    source = Column(String, nullable=True)  # e.g. "manual", "greenhouse", "scraped"
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())