from typing import (
    TypeAlias,
    Union,
    List,
    Callable,
    Any,
)


COMMAND: TypeAlias = Union[List[Any], str]
INPUT_VALIDATOR: TypeAlias = Callable[[str], bool]