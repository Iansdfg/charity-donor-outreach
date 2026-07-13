from __future__ import annotations

import os
from typing import Protocol

from .models import FactBundle, NarrativeDraft


class DraftingModel(Protocol):
    identifier: str

    def draft(
        self, bundle: FactBundle, prompt: str, *, timeout_seconds: float
    ) -> NarrativeDraft: ...


class FakeDraftingModel:
    identifier = "fake-deterministic-v1"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def draft(self, bundle: FactBundle, prompt: str, *, timeout_seconds: float) -> NarrativeDraft:
        del prompt, timeout_seconds
        self.calls.append(bundle.donor_id)
        claim_text = " ".join(claim.text for claim in bundle.claims)
        campaign = next(fact.value for fact in bundle.facts if fact.key == "campaign_name")
        return NarrativeDraft(
            subject=f"An invitation to support {campaign}",
            opening="Thank you for your generosity and connection to our community.",
            campaign_paragraph=claim_text
            or f"Your support for {campaign} helps sustain this work.",
            ask_paragraph=(
                f"Please consider a gift of {bundle.ask.amount:.2f} {bundle.ask.currency}."
            ),
        )


class OpenAIAdapter:
    """Optional adapter; importing this module never requires the SDK or an API key."""

    identifier = "openai-configured-model"

    def draft(self, bundle: FactBundle, prompt: str, *, timeout_seconds: float) -> NarrativeDraft:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for the optional OpenAI provider")
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("install the 'openai' extra to use this provider") from exc
        client = OpenAI(timeout=timeout_seconds)
        response = client.responses.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            input=[
                {"role": "system", "content": "Return schema-valid narrative fields only."},
                {"role": "user", "content": prompt},
            ],
            text_format=NarrativeDraft,
        )
        parsed = response.output_parsed
        if not isinstance(parsed, NarrativeDraft):
            raise RuntimeError("provider returned no schema-valid parsed output")
        return parsed
