from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .errors import PolicyError


@dataclass(frozen=True)
class Policies:
    segmentation: dict[str, Any]
    ask: dict[str, Any]
    claims: dict[str, Any]
    compliance: dict[str, Any]

    @property
    def version(self) -> str:
        versions = {
            str(p["version"]) for p in (self.segmentation, self.ask, self.claims, self.compliance)
        }
        if len(versions) != 1:
            raise PolicyError(f"policy versions must match, found {sorted(versions)}")
        return versions.pop()


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PolicyError(f"cannot load policy {path}: {exc}") from exc
    if not isinstance(value, dict) or "version" not in value:
        raise PolicyError(f"policy {path} must be a mapping with a version")
    return value


def load_policies(root: Path | None = None) -> Policies:
    base = root or Path(__file__).resolve().parents[2] / "policies"
    return Policies(
        segmentation=_load_yaml(base / "segmentation.yaml"),
        ask=_load_yaml(base / "ask_policy.yaml"),
        claims=_load_yaml(base / "campaign_claims.yaml"),
        compliance=_load_yaml(base / "compliance.yaml"),
    )
