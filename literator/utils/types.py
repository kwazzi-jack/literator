from datetime import datetime
from typing import Optional, Sequence, TypeAlias, Union

# Input types
StrInput: TypeAlias = Union[str, Sequence[str]]
BoolInput: TypeAlias = Union[bool, Sequence[bool]]

# Output types
StrOutput: TypeAlias = Optional[Union[str, Sequence[str]]]
BoolOutput: TypeAlias = Optional[Union[bool, Sequence[bool]]]

# Other types
Date: TypeAlias = Optional[datetime]
