from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .batch import BatchProcessor
from .config import load_policies
from .llm import FakeDraftingModel, OpenAIAdapter
from .storage import atomic_write_json
from .summary import summarize as build_summary
from .validation import load_campaign, load_donors_csv

app = typer.Typer(no_args_is_help=True, help="Generate policy-governed donor outreach drafts.")


@app.command()
def validate(
    donors: Annotated[Path, typer.Option(exists=True)],
    campaign: Annotated[Path, typer.Option(exists=True)],
) -> None:
    loaded_donors = load_donors_csv(donors)
    loaded_campaign = load_campaign(campaign)
    typer.echo(
        json.dumps(
            {
                "donors": len(loaded_donors),
                "campaign_id": loaded_campaign.campaign_id,
                "valid": True,
            }
        )
    )


@app.command()
def generate(
    donors: Annotated[Path, typer.Option(exists=True)],
    campaign: Annotated[Path, typer.Option(exists=True)],
    output: Annotated[Path, typer.Option()],
    provider: Annotated[str, typer.Option()] = "fake",
    max_workers: Annotated[int, typer.Option(min=1, max=32)] = 4,
) -> None:
    _generate(donors, campaign, output, provider, max_workers)


def _generate(donors: Path, campaign: Path, output: Path, provider: str, max_workers: int) -> None:
    model = FakeDraftingModel() if provider == "fake" else OpenAIAdapter()
    output.mkdir(parents=True, exist_ok=True)
    atomic_write_json(
        output / "input_sources.json",
        {
            "donors": str(donors.resolve()),
            "campaign": str(campaign.resolve()),
            "provider": provider,
        },
    )
    manifest = BatchProcessor(load_policies(), model).run(
        load_donors_csv(donors), load_campaign(campaign), output, max_workers=max_workers
    )
    typer.echo(manifest.model_dump_json())
    if manifest.status == "failed":
        raise typer.Exit(1)


@app.command()
def resume(run: Annotated[Path, typer.Option(exists=True)]) -> None:
    metadata_path = run / "input_sources.json"
    if not metadata_path.exists():
        raise typer.BadParameter(
            "run does not contain input_sources.json; use generate again with the same output"
        )
    sources = json.loads(metadata_path.read_text(encoding="utf-8"))
    _generate(
        Path(sources["donors"]), Path(sources["campaign"]), run, sources.get("provider", "fake"), 4
    )


@app.command()
def summarize(run: Annotated[Path, typer.Option(exists=True)]) -> None:
    summary = build_summary(run)
    atomic_write_json(run / "run_summary.json", summary.model_dump(mode="json"))
    typer.echo(summary.model_dump_json())


if __name__ == "__main__":
    app()
