from typing import Any


class Error(Exception):
    """Base class for all exceptions raised by Literator."""


class ValidationError(Error):
    """Base class for exceptions related to validation."""


class PhraseError(ValidationError):
    """Base class for exceptions related to phrase formatting."""


class PhraseEmptyError(PhraseError):
    """Raised when the phrase value is problematic."""

    def __init__(self):
        super().__init__("Phrase input cannot be empty.")


class PhrasesEmptyError(PhraseError):
    """Raised when the phrase value is problematic."""

    def __init__(self):
        super().__init__("Phrase sequence input cannot be empty.")


class PhraseTypeError(PhraseError):
    """Raised when the phrase input is of an invalid type."""

    def __init__(self, value: Any):
        super().__init__(
            f"Phrase input expects string or a sequence of strings. Got {type(value)} instead."
        )


class PhrasesTypeError(PhraseError):
    """Raised when the phrase input is of an invalid type."""

    def __init__(self, index: int, value: Any):
        super().__init__(
            f"Expected phrase input to be string at index {index}. Got {type(value)} instead."
        )


class FlagError(ValidationError):
    """Base class for exceptions related to flag formatting."""


class FlagsEmptyError(FlagError):
    """Raised when the flag input is empty."""

    def __init__(self):
        super().__init__("Flag sequence input cannot be empty.")


class FlagTypeError(FlagError):
    """Raised when the flag input is of an invalid type."""

    def __init__(self, value: Any):
        super().__init__(
            f"Flag input expects boolean or a sequence of booleans. Got {type(value)} instead."
        )


class FlagsTypeError(FlagError):
    """Raised when the flag input is of an invalid type."""

    def __init__(self, index: int, value: Any):
        super().__init__(
            f"Expected flag input to be boolean at index {index}. Got {type(value)} instead."
        )


class LengthMismatchError(PhraseError, FlagError):
    """Raised when the lengths of phrase and flag inputs do not match."""

    def __init__(self, phrases: Any, flags: Any):
        super().__init__(
            f"Phrases and flags must have the same length. Got {len(phrases)} and {len(flags)} instead."
        )
