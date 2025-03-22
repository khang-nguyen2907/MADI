from dataclasses import dataclass
from typing import (
    Callable,
    Any,
    Dict,
    get_type_hints,
    Optional,
    List
)

@dataclass
class Tool:
    name: str
    description: str
    func: Callable[..., str]
    parameters: Dict[str, Dict[str, str]]

    def __call__(self, *args: Any, **kwargs: Any) -> str:
        return self.func(*args, **kwargs)