from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .models import FactBundle, LetterDraft, NarrativeDraft

TEMPLATE_VERSION = "1.0.0"


class Renderer:
    def __init__(self, template_dir: Path | None = None) -> None:
        root = template_dir or Path(__file__).resolve().parents[2] / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(root),
            # Both HTML and plain-text outputs encode untrusted angle brackets.
            autoescape=True,
            undefined=StrictUndefined,
            enable_async=False,
        )

    def render(self, bundle: FactBundle, narrative: NarrativeDraft) -> LetterDraft:
        facts = {fact.key: fact.value for fact in bundle.facts}
        context = {
            "bundle": bundle,
            "narrative": narrative,
            "donation_url": facts["donation_url"],
            "charity_name": facts["charity_name"],
        }
        html = self.environment.get_template("donor-letter.html.j2").render(context)
        plain = self.environment.get_template("donor-letter.txt.j2").render(context)
        return LetterDraft(subject=narrative.subject, html=html, plain_text=plain)
