import hashlib


def make_dedup_key(title, company, description):
    """Same posting always produces the same key."""
    text = f"{title}|{company}|{description}".lower().strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()