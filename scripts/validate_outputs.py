import json
import sys
from pathlib import Path

from charity_donor_outreach.models import GenerationResult

for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    if line.strip():
        GenerationResult.model_validate(json.loads(line))
print("valid")
