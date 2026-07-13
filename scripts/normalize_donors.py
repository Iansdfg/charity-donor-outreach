import json
import sys
from pathlib import Path

from charity_donor_outreach.normalization import normalize_donor
from charity_donor_outreach.validation import load_donors_csv

for donor in load_donors_csv(Path(sys.argv[1])):
    print(json.dumps(normalize_donor(donor).model_dump(mode="json"), sort_keys=True))
