"""Shared cleaning applied to every source."""

import re

import pandas as pd

from data_pipeline.config import PROCESSED_DIR
from data_pipeline.dedup import make_dedup_key

MIN_DESCRIPTION_LENGTH = 200


def _tidy(text):
    """Collapse whitespace and line-break noise into single spaces."""
    if pd.isna(text):
        return ""
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


def clean(df, source_name):
    """Apply shared rules, add dedup_key, save to processed/."""
    before = len(df)

    df = df.copy()
    df["title"] = df["title"].apply(_tidy)
    df["company"] = df["company"].apply(_tidy)
    df["raw_description"] = df["raw_description"].apply(_tidy)

    # Must have a title and a description
    df = df[df["title"] != ""]
    df = df[df["raw_description"] != ""]

    # Too short to be a real posting
    df = df[df["raw_description"].str.len() >= MIN_DESCRIPTION_LENGTH]

    df["dedup_key"] = df.apply(
        lambda row: make_dedup_key(
            row["title"], row["company"], row["raw_description"]
        ),
        axis=1,
    )

    # Same posting appearing twice inside this batch
    df = df.drop_duplicates(subset="dedup_key")

    out_path = PROCESSED_DIR / f"{source_name}.csv"
    df.to_csv(out_path, index=False)

    print(f"[{source_name}] {before} -> {len(df)} rows kept, saved to {out_path}")
    return df