"""Provider-specific exception classes."""


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, provider: str | None = None, status_code: int | None = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int | None = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""

    pass


class ValidationError(ProviderError):
    """Raised when provider input validation fails."""

    pass


class TimeoutError(ProviderError):
    """Raised when provider request times out."""

    pass
