from typing import Any


class Error(Exception):
    """Base class for all exceptions raised by Literator."""


class ValidationErr(Error):
    """Base class for exceptions related to validation."""


class PhraseErr(ValidationErr):
    """Base class for exceptions related to phrase formatting."""


class PhraseEmptyError(PhraseErr):
    """Raised when the phrase value is problematic."""

    def __init__(self):
        super().__init__("Phrase input cannot be empty.")


class PhrasesEmptyError(PhraseErr):
    """Raised when the phrase value is problematic."""

    def __init__(self):
        super().__init__("Phrase sequence input cannot be empty.")


class PhraseTypeErr(PhraseErr):
    """Raised when the phrase input is of an invalid type."""

    def __init__(self, value: Any):
        super().__init__(
            f"Phrase input expects string or a sequence of strings. Got {type(value)} instead."
        )


class PhrasesTypeErr(PhraseErr):
    """Raised when the phrase input is of an invalid type."""

    def __init__(self, index: int, value: Any):
        super().__init__(
            f"Expected phrase input to be string at index {index}. Got {type(value)} instead."
        )


class FlagErr(ValidationErr):
    """Base class for exceptions related to flag formatting."""


class FlagsEmptyErr(FlagErr):
    """Raised when the flag input is empty."""

    def __init__(self):
        super().__init__("Flag sequence input cannot be empty.")


class FlagTypeError(FlagErr):
    """Raised when the flag input is of an invalid type."""

    def __init__(self, value: Any):
        super().__init__(
            f"Flag input expects boolean or a sequence of booleans. Got {type(value)} instead."
        )


class FlagsTypeErr(FlagErr):
    """Raised when the flag input is of an invalid type."""

    def __init__(self, index: int, value: Any):
        super().__init__(
            f"Expected flag input to be boolean at index {index}. Got {type(value)} instead."
        )


class LengthMismatchErr(PhraseErr, FlagErr):
    """Raised when the lengths of phrase and flag inputs do not match."""

    def __init__(self, phrases: Any, flags: Any):
        super().__init__(
            f"Phrases and flags must have the same length. Got {len(phrases)} and {len(flags)} instead."
        )
