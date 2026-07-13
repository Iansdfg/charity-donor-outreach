from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from .ask_calculator import calculate_ask
from .claims import approved_claims
from .config import Policies
from .eligibility import evaluate_eligibility
from .fact_bundle import build_fact_bundle
from .llm import DraftingModel
from .models import Campaign, DonorInput, GenerationResult, RunManifest
from .normalization import normalize_donor
from .output_validation import validate_output
from .prompting import build_prompt
from .reconciliation import reconcile
from .renderer import TEMPLATE_VERSION, Renderer
from .retry import with_retry
from .segmentation import segment
from .storage import atomic_write_json, atomic_write_jsonl, read_jsonl, upsert_jsonl
from .summary import summarize


def idempotency_key(
    run_id: str, donor_id: str, campaign_id: str, policy_version: str, template_version: str
) -> str:
    value = "\x1f".join((run_id, donor_id, campaign_id, policy_version, template_version))
    return hashlib.sha256(value.encode()).hexdigest()


class BatchProcessor:
    def __init__(
        self, policies: Policies, model: DraftingModel, renderer: Renderer | None = None
    ) -> None:
        self.policies = policies
        self.model = model
        self.renderer = renderer or Renderer()
        self.retries = 0
        self.duplicates_skipped = 0

    def _process(
        self, donor_input: DonorInput, campaign: Campaign, run_id: str
    ) -> GenerationResult:
        normalized = normalize_donor(donor_input)
        segmentation = segment(normalized, campaign.as_of_date, self.policies.segmentation)
        normalized = reconcile(donor_input, normalized, segmentation)
        eligibility = evaluate_eligibility(normalized, self.policies.compliance)
        key = idempotency_key(
            run_id,
            donor_input.donor_id,
            campaign.campaign_id,
            self.policies.version,
            TEMPLATE_VERSION,
        )
        if not eligibility.eligible:
            return GenerationResult(
                donor_id=donor_input.donor_id,
                campaign_id=campaign.campaign_id,
                status="suppressed",
                financial_tier=segmentation.financial_tier,
                engagement_status=segmentation.engagement_status,
                warnings=normalized.warnings,
                policy_version=self.policies.version,
                template_version=TEMPLATE_VERSION,
                model_identifier=self.model.identifier,
                idempotency_key=key,
                suppression_reasons=eligibility.reason_codes,
            )
        ask = calculate_ask(normalized, campaign, segmentation, self.policies.ask)
        claims = approved_claims(campaign, self.policies.claims)
        bundle = build_fact_bundle(normalized, campaign, segmentation, ask, claims)
        narrative, retries = with_retry(
            lambda: self.model.draft(bundle, build_prompt(bundle), timeout_seconds=20.0)
        )
        self.retries += retries
        letter = self.renderer.render(bundle, narrative)
        validate_output(
            letter,
            ask=ask.amount,
            donation_url=str(campaign.donation_url),
            claims=claims,
            claim_policy=self.policies.claims,
        )
        return GenerationResult(
            donor_id=donor_input.donor_id,
            campaign_id=campaign.campaign_id,
            status="draft_generated",
            financial_tier=segmentation.financial_tier,
            engagement_status=segmentation.engagement_status,
            recommended_ask=ask,
            personalization_facts_used=[fact.key for fact in bundle.facts],
            campaign_claims_used=[claim.claim_id for claim in claims],
            warnings=normalized.warnings,
            letter=letter,
            policy_version=self.policies.version,
            template_version=TEMPLATE_VERSION,
            model_identifier=self.model.identifier,
            idempotency_key=key,
        )

    def run(
        self, donors: list[DonorInput], campaign: Campaign, run_dir: Path, *, max_workers: int = 4
    ) -> RunManifest:
        run_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        manifest_path = run_dir / "manifest.json"
        manifest = RunManifest(
            run_id=run_dir.name,
            campaign_id=campaign.campaign_id,
            policy_version=self.policies.version,
            template_version=TEMPLATE_VERSION,
            provider=self.model.identifier,
            status="running",
            created_at=now,
            updated_at=now,
        )
        if manifest_path.exists():
            prior = RunManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
            manifest = prior.model_copy(update={"status": "running", "updated_at": now})
        atomic_write_json(manifest_path, manifest.model_dump(mode="json"))
        normalized_records = [
            normalize_donor(donor).model_dump(mode="json")
            for donor in sorted(donors, key=lambda item: item.donor_id)
        ]
        atomic_write_jsonl(run_dir / "normalized_donors.jsonl", normalized_records)
        completed = {
            item["idempotency_key"] for item in read_jsonl(run_dir / "generation_results.jsonl")
        }
        pending = [
            donor
            for donor in sorted(donors, key=lambda item: item.donor_id)
            if idempotency_key(
                run_dir.name,
                donor.donor_id,
                campaign.campaign_id,
                self.policies.version,
                TEMPLATE_VERSION,
            )
            not in completed
        ]
        self.duplicates_skipped += len(donors) - len(pending)
        with ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
            futures = [
                (donor, executor.submit(self._process, donor, campaign, run_dir.name))
                for donor in pending
            ]
            for donor, future in futures:
                try:
                    result = future.result()
                    upsert_jsonl(
                        run_dir / "generation_results.jsonl",
                        result.model_dump(mode="json"),
                        key="idempotency_key",
                    )
                    eligibility = {
                        "donor_id": donor.donor_id,
                        "eligible": result.status != "suppressed",
                        "reason_codes": result.suppression_reasons,
                    }
                    upsert_jsonl(run_dir / "eligibility_results.jsonl", eligibility, key="donor_id")
                    if result.status == "draft_generated":
                        upsert_jsonl(
                            run_dir / "review_queue.jsonl",
                            result.model_dump(mode="json"),
                            key="idempotency_key",
                        )
                except Exception as exc:
                    error = {
                        "donor_id": donor.donor_id,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                    upsert_jsonl(run_dir / "validation_errors.jsonl", error, key="donor_id")
        run_summary = summarize(
            run_dir, retries=self.retries, duplicates_skipped=self.duplicates_skipped
        )
        atomic_write_json(run_dir / "run_summary.json", run_summary.model_dump(mode="json"))
        status = "completed_with_errors" if run_summary.failed else "completed"
        manifest = manifest.model_copy(update={"status": status, "updated_at": datetime.now(UTC)})
        atomic_write_json(manifest_path, manifest.model_dump(mode="json"))
        return manifest
