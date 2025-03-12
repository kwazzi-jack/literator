from datetime import datetime
from typing import List, Optional, Sequence, TypeAlias, Union


Date: TypeAlias = Optional[datetime]
Phrases: TypeAlias = List[str]
PhraseInput: TypeAlias = Union[str, Sequence[str]]
ExactFlag: TypeAlias = Union[bool, Sequence[bool]]
