from decimal import Decimal
from uuid import UUID
from generics import Asset 
from dataclasses import dataclass

@dataclass
class Agent:
    cash: Decimal
    portfolio: dict[UUID, Decimal]
    behavior: object | None = None
