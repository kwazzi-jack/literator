"""Utility objects for the Literator package."""

# Expose module
from literator.utils.errors import (
    Error,
    DateError,
    DatePatternError,
    DateEmptyError,
    StrError,
    StrEmptyError,
    ValidationError,
    PhraseError,
    PhraseEmptyError,
    PhrasesEmptyError,
    PhraseTypeError,
    PhrasesTypeError,
    FlagError,
    FlagsEmptyError,
    FlagTypeError,
)
from literator.utils.functions import get_timestamp, str_to_datetime, format_phrases
from literator.utils.logging import setup_logging, get_logger
from literator.utils.types import (
    Date,
    DateResult,
    Flag,
    FlagInput,
    FlagResult,
    Flags,
    Phrase,
    PhraseInput,
    PhraseResult,
    Phrases,
    ValidationResult,
)

__all__ = [
    # Errors
    "Error",
    "DateError",
    "DatePatternError",
    "DateEmptyError",
    "StrError",
    "StrEmptyError",
    "ValidationError",
    "PhraseError",
    "PhraseEmptyError",
    "PhrasesEmptyError",
    "PhraseTypeError",
    "PhrasesTypeError",
    "FlagError",
    "FlagsEmptyError",
    "FlagTypeError",
    # Functions
    "get_timestamp",
    "str_to_datetime",
    "format_phrases",
    "setup_logging",
    "get_logger",
    # Types
    "Date",
    "DateResult",
    "Flag",
    "FlagInput",
    "FlagResult",
    "Flags",
    "Phrase",
    "PhraseInput",
    "PhraseResult",
    "Phrases",
    "ValidationResult",
]
