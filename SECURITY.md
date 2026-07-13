# Security Policy

Report vulnerabilities privately to the repository maintainers; do not include donor data in reports. Supported releases receive security fixes on the latest minor line.

Treat all uploaded fields and provider output as hostile. Never commit production donor data, secrets, run artifacts, or API keys. Immediately stop affected runs, preserve minimal donor-ID audit evidence, revoke exposed credentials, quarantine outputs, correct policy/templates, and rerun from trusted inputs after review. See `docs/SECURITY_AND_PRIVACY.md`.

