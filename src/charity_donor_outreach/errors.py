class OutreachError(Exception):
    """Base class for actionable domain failures."""


class InputValidationError(OutreachError):
    """Input failed schema or safety validation."""


class PolicyError(OutreachError):
    """Versioned policy is invalid or cannot authorize an operation."""


class OutputValidationError(OutreachError):
    """Draft output is unsafe, ungrounded, or structurally invalid."""


class TransientProviderError(OutreachError):
    """Provider failure that can be retried within configured bounds."""
