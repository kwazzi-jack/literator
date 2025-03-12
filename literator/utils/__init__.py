"""Utility objects for the Literator package."""

# Expose module
from literator.utils.errors import (
    Error,
    ValidationErr,
    PhraseErr,
    PhraseEmptyError,
    PhrasesEmptyError,
    PhraseTypeErr,
    PhrasesTypeErr,
    FlagErr,
    FlagsEmptyErr,
    FlagTypeError,
)
from literator.utils.functions import get_timestamp, str_to_datetime, format_phrases
from literator.utils.logging import setup_logging, get_logger
from literator.utils.types import (
    Date,
    Flag,
    FlagResult,
    Flags,
    Phrase,
    PhraseResult,
    Phrases,
)

__all__ = [
    "Error",
    "ValidationErr",
    "PhraseErr",
    "PhraseEmptyError",
    "PhrasesEmptyError",
    "PhraseTypeErr",
    "PhrasesTypeErr",
    "FlagErr",
    "FlagsEmptyErr",
    "FlagTypeError",
    "get_timestamp",
    "str_to_datetime",
    "format_phrases",
    "setup_logging",
    "get_logger",
    "Date",
    "Flag",
    "FlagResult",
    "Flags",
    "Phrase",
    "PhraseResult",
    "Phrases",
]
