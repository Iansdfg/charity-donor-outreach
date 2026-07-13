import json

from charity_donor_outreach.batch import BatchProcessor
from charity_donor_outreach.llm import FakeDraftingModel
from charity_donor_outreach.models import NarrativeDraft
from tests.conftest import make_donor


def test_resume_idempotency_and_deterministic_order(tmp_path, policies, campaign):
    donors = [make_donor(donor_id="D-2"), make_donor(donor_id="D-1")]
    run = tmp_path / "demo"
    processor = BatchProcessor(policies, FakeDraftingModel())
    processor.run(donors, campaign, run, max_workers=2)
    first = (run / "generation_results.jsonl").read_text()
    processor.run(donors, campaign, run, max_workers=2)
    assert (run / "generation_results.jsonl").read_text() == first
    records = [json.loads(line) for line in first.splitlines()]
    assert [record["donor_id"] for record in records] == ["D-1", "D-2"]
    assert processor.duplicates_skipped == 2
    assert all(record["approval_status"] == "requires_review" for record in records)


class OneBadModel(FakeDraftingModel):
    def draft(self, bundle, prompt, *, timeout_seconds):
        if bundle.donor_id == "D-bad":
            return NarrativeDraft(
                subject="bad", opening="x", campaign_paragraph="x", ask_paragraph="wrong"
            )
        return super().draft(bundle, prompt, timeout_seconds=timeout_seconds)


def test_partial_failure_isolated(tmp_path, policies, campaign):
    run = tmp_path / "partial"
    BatchProcessor(policies, OneBadModel()).run(
        [make_donor(donor_id="D-good"), make_donor(donor_id="D-bad")], campaign, run
    )
    assert "D-good" in (run / "generation_results.jsonl").read_text()
    assert "D-bad" in (run / "validation_errors.jsonl").read_text()


def test_atomic_files_are_complete_json_lines(tmp_path, policies, campaign):
    run = tmp_path / "atomic"
    BatchProcessor(policies, FakeDraftingModel()).run([make_donor()], campaign, run)
    for path in run.glob("*.jsonl"):
        for line in path.read_text().splitlines():
            json.loads(line)
