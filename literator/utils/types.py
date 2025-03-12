from datetime import datetime
from typing import List, Tuple, TypeAlias, Union

from result import Result

from literator.utils.errors import (
    DateError,
    FlagError,
    PhraseError,
    StrError,
    ValidationError,
)

# Generic Types
Phrase: TypeAlias = str
Flag: TypeAlias = bool
Date: TypeAlias = datetime

# Collection Types
Phrases: TypeAlias = Union[List[Phrase], Tuple[Phrase]]
Flags: TypeAlias = Union[List[Flag], Tuple[Flag]]

# Input Types
DateInput: TypeAlias = Union[str, Date]
PhraseInput: TypeAlias = Union[Phrase, Phrases]
FlagInput: TypeAlias = Union[Flag, Flags]

# Output Types
PhraseOutput: TypeAlias = Union[Phrase, Phrases]
FlagOutput: TypeAlias = Union[Flag, Flags]

# Result types
DateResult: TypeAlias = Result[DateInput, DateError]
StrResult: TypeAlias = Result[str, StrError]
ValidationResult: TypeAlias = Result[None, ValidationError]
PhraseResult: TypeAlias = Result[PhraseOutput, PhraseError]
FlagResult: TypeAlias = Result[FlagOutput, FlagError]
