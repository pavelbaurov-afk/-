from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    title: str
    start: datetime
    end: Optional[datetime]
    address: str
    url: str
    source: str
    description: str = ""
    category: str = ""
    age: str = ""
    registration_required: Optional[bool] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    distance_km: Optional[float] = None
    score: float = field(default=0.0)
