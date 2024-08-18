from datetime import datetime
from typing import NamedTuple


class CveDTO(NamedTuple):
    """
    I chose NamedTuple because it faster than dict and dataclass.
    Also, it takes less memory.
    """

    cve_id: str
    title: str
    reserved_date: datetime | None
    published_date: datetime | None
    updated_date: datetime | None
    description: str
    problem_types: str
