import typing
from enum import Enum
from typing import List, Tuple


def enum_to_choices(enum: Enum) -> List[Tuple[int, str]]:
    return [(i.value, i.name) for i in enum]
