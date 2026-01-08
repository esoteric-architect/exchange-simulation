from dataclasses import dataclass 
from decimal import Decimal
from uuid import UUID

@dataclass 
class Asset :
   # __slots__ = ['type', 'id', 'price', 'owner']
    type : str 
    id : UUID
    price : Decimal
    quantity : Decimal # how many units there are 
    owner : UUID | None = None
    # Don't access by __setattr__()
    def update_price(self, new_price : Decimal) : 
        self.price = new_price 
    

