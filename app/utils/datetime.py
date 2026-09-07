from datetime import datetime, timezone

def get_utc() -> datetime:
    return datetime.now(timezone.utc)