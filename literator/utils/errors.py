from typing import Any


class Error(Exception):
    """Base class for all exceptions raised by Literator."""


class PhraseEmptyError(Error):
    """Raised when the phrase input is empty."""

    def __init__(self):
        super().__init__("Phrase input cannot be empty.")


class PhraseTypeError(Error):
    """Raised when the phrase input is of an invalid type."""

    def __init__(self, value: Any):
        super().__init__(
            f"Phrase input expects string or a sequence of strings. Got {type(value)} instead."
        )


class FlagEmptyError(Error):
    """Raised when the flag input is empty."""

    def __init__(self):
        super().__init__("Flag input cannot be empty.")


class FlagTypeError(Error):
    """Raised when the flag input is of an invalid type."""

    def __init__(self, value: Any):
        super().__init__(
            f"Flag input expects boolean or a sequence of booleans. Got {type(value)} instead."
        )


class PhraseAndFlagLengthError(Error):
    """Raised when the lengths of phrase and flag inputs do not match."""

    def __init__(self, phrase: Any, flag: Any):
        super().__init__(
            f"Phrase and flag inputs must have the same length. Got {len(phrase)} and {len(flag)} instead."
        )
