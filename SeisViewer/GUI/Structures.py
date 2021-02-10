from typing import NamedTuple
from datetime import datetime


class FileInfo(NamedTuple):
    path: str
    name: str
    format_type: str
    frequency: int
    time_start: datetime
    time_stop: datetime
    duration: str
    longitude: float
    latitude: float
