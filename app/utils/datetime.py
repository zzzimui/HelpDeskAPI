from datetime import datetime, timezone

def get_utc() -> datetime:
    return datetime.now(timezone.utc)

def get_naive_utc() -> datetime:
    """
    Sets tzinfo to null — as PostgreSQL expects it to be
    """
    return datetime.now()