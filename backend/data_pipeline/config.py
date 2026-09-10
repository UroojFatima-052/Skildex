from pathlib import Path

# Project root = two levels up from this file (data_pipeline -> backend -> skildex)
ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Make sure they exist
for d in (RAW_DIR, PROCESSED_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Dataset identifiers
DJINNI_HF_REPO = "lang-uk/recruitment-dataset-job-descriptions-english"
GREENHOUSE_COMPANIES_URL = "https://raw.githubusercontent.com/Feashliaa/job-board-aggregator/main/data/greenhouse_companies.json"
LEVER_COMPANIES_URL = "https://raw.githubusercontent.com/Feashliaa/job-board-aggregator/main/data/lever_companies.json"
