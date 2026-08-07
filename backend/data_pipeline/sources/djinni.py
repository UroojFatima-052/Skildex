"""Djinni job descriptions — downloaded from Hugging Face."""

import shutil
import pandas as pd
from huggingface_hub import list_repo_files, hf_hub_download

from data_pipeline.config import RAW_DIR, DJINNI_HF_REPO

SOURCE_NAME = "djinni"
RAW_FILE = RAW_DIR / "djinni.parquet"


def download():
    """Fetch the raw parquet, unless we already have it."""
    if RAW_FILE.exists():
        print(f"[{SOURCE_NAME}] already downloaded, skipping")
        return RAW_FILE

    files = list_repo_files(DJINNI_HF_REPO, repo_type="dataset")
    parquet_files = [f for f in files if f.endswith(".parquet")]

    if not parquet_files:
        raise FileNotFoundError(f"No parquet found in {DJINNI_HF_REPO}")

    print(f"[{SOURCE_NAME}] downloading {parquet_files[0]} ...")
    cached_path = hf_hub_download(
        repo_id=DJINNI_HF_REPO,
        filename=parquet_files[0],
        repo_type="dataset",
    )
    shutil.copy(cached_path, RAW_FILE)
    print(f"[{SOURCE_NAME}] saved to {RAW_FILE}")
    return RAW_FILE

def _cyrillic_ratio(text):
    text = str(text)
    if not text:
        return 0
    cyrillic = sum(1 for c in text if "\u0400" <= c <= "\u04FF")
    return cyrillic / len(text)

def load():
    """Return this source's postings in our standard columns."""
    download()
    df = pd.read_parquet(RAW_FILE)

    df = df[df["Long Description"].apply(_cyrillic_ratio) < 0.1]
    
    return pd.DataFrame({
        "title": df["Position"],
        "company": df["Company Name"],
        "raw_description": df["Long Description"],
        "source": SOURCE_NAME,
    })


if __name__ == "__main__":
    result = load()
    print(result.shape)
    print(result.head())