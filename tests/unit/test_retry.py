import pytest

from charity_donor_outreach.errors import InputValidationError, TransientProviderError
from charity_donor_outreach.retry import with_retry


def test_transient_failure_retries_deterministically() -> None:
    attempts = 0
    delays: list[float] = []

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TransientProviderError("temporary")
        return "ok"

    result, retries = with_retry(
        operation, sleep=delays.append, random_value=lambda: 0.5, max_total_seconds=10
    )
    assert (result, retries, attempts) == ("ok", 2, 3)
    assert delays == [0.25, 0.5]


def test_policy_validation_failure_is_not_retried() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise InputValidationError("bad input")

    with pytest.raises(InputValidationError):
        with_retry(operation)
    assert attempts == 1
