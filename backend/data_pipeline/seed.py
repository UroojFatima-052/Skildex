"""Load cleaned CSVs into Supabase, skipping postings already stored."""

import sys

import pandas as pd

from database import SessionLocal
from data_pipeline.config import PROCESSED_DIR
from models import JobPosting

CHUNK_SIZE = 1000

COLUMNS = ["title", "company", "raw_description", "source", "dedup_key"]


def seed(source_name):
    path = PROCESSED_DIR / f"{source_name}.csv"
    if not path.exists():
        print(f"[{source_name}] no cleaned file at {path}")
        return

    df = pd.read_csv(path)
    df = df[COLUMNS].fillna("")
    print(f"[{source_name}] {len(df)} rows in file")

    db = SessionLocal()
    try:
        existing = {k for (k,) in db.query(JobPosting.dedup_key).all()}
        print(f"[{source_name}] {len(existing)} already in database")

        new_rows = df[~df["dedup_key"].isin(existing)]
        print(f"[{source_name}] {len(new_rows)} to insert")

        inserted = 0
        for start in range(0, len(new_rows), CHUNK_SIZE):
            chunk = new_rows.iloc[start:start + CHUNK_SIZE]
            db.bulk_insert_mappings(JobPosting, chunk.to_dict("records"))
            db.commit()
            inserted += len(chunk)
            print(f"[{source_name}] {inserted}/{len(new_rows)}")

        print(f"[{source_name}] done — {inserted} inserted")
    finally:
        db.close()


if __name__ == "__main__":
    names = sys.argv[1:] or ["djinni", "ats"]
    for name in names:
        seed(name)