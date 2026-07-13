import json
from decimal import Decimal
from pathlib import Path

from .models import RunSummary
from .storage import read_jsonl


def summarize(
    run_dir: Path, *, retries: int | None = None, duplicates_skipped: int | None = None
) -> RunSummary:
    previous_path = run_dir / "run_summary.json"
    previous = (
        json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else {}
    )
    results = read_jsonl(run_dir / "generation_results.jsonl")
    errors = read_jsonl(run_dir / "validation_errors.jsonl")
    generated = sum(item.get("status") == "draft_generated" for item in results)
    suppressed = sum(item.get("status") == "suppressed" for item in results)
    failed = len(errors) + sum(item.get("status") == "failed" for item in results)
    total = generated + suppressed + failed
    valid_rate = Decimal(generated) / Decimal(generated) if generated else Decimal("1")
    review_rate = Decimal(generated) / Decimal(generated) if generated else Decimal("1")
    return RunSummary(
        run_id=run_dir.name,
        total=total,
        generated=generated,
        suppressed=suppressed,
        failed=failed,
        duplicates_skipped=(
            int(previous.get("duplicates_skipped", 0))
            if duplicates_skipped is None
            else duplicates_skipped
        ),
        retries=int(previous.get("retries", 0)) if retries is None else retries,
        schema_valid_output_rate=valid_rate,
        human_review_rate=review_rate,
    )
