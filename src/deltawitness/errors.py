"""Project-specific exceptions."""


class DeltaWitnessError(Exception):
    """Base class for expected DeltaWitness failures."""


class ConfigurationError(DeltaWitnessError):
    """Raised when the witness specification is invalid."""


class GitError(DeltaWitnessError):
    """Raised when Git operations fail or the repository is unsuitable."""


class UnsupportedClaimError(DeltaWitnessError):
    """Raised when complete observations show the declared claim is unsupported."""


class VerificationError(DeltaWitnessError):
    """Raised when the verification harness cannot complete safely."""


class ReportError(DeltaWitnessError):
    """Raised when a report is malformed or fails an integrity check."""


class ReceiptError(DeltaWitnessError):
    """Raised when a machine-readable outcome receipt is missing or invalid."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)
