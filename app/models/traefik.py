from typing import List, Optional

from models.base import BaseSchema


class TLS(BaseSchema):
    options: str
    cert_resolver: str

class Router(BaseSchema):
    entry_points: List[str]
    service: str
    rule: str
    priority: Optional[int] = None
    tls: Optional[TLS] = None
    status: str
    using: List[str]
    name: str
    provider: str
    middlewares: Optional[List[str]] = None

