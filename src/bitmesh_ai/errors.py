"""Exceptions raised by ``BitmeshClient``."""


class BitmeshError(RuntimeError):
    """Raised for transport failures, HTTP errors, validation errors, or invalid JSON."""
