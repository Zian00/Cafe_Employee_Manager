class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class ConflictError(Exception):
    """Raised when an operation would violate a uniqueness constraint."""


class ValidationError(Exception):
    """Raised when domain-level validation fails."""
