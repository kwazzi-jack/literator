from datetime import datetime
from typing import List, Tuple, TypeAlias, Union

from result import Result

from literator.utils.errors import FlagErr, PhraseErr

# Generic Types
Phrase: TypeAlias = str
Flag: TypeAlias = bool
Date: TypeAlias = datetime

# Collection Types
Phrases: TypeAlias = Union[List[Phrase], Tuple[Phrase]]
Flags: TypeAlias = Union[List[Flag], Tuple[Flag]]

# Result types
PhraseResult: TypeAlias = Result[Union[Phrase, Phrases], PhraseErr]
FlagResult: TypeAlias = Result[Union[Flag, Flags], FlagErr]
