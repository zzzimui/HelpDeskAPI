import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log(to_display: Any) -> None:
    logging.info(to_display)