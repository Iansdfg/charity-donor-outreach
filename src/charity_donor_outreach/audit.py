import json
import logging
from typing import Any


def audit_event(logger: logging.Logger, event: str, donor_id: str, **context: Any) -> None:
    logger.info(
        json.dumps({"event": event, "donor_id": donor_id, **context}, sort_keys=True, default=str)
    )
