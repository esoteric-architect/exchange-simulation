from dataclasses import dataclass
from enum import Enum, auto
from .asset import Asset
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent import Agent

class OrderType(Enum) : 
    GoodTillCancel = auto() 
    Market = auto() 
    Limit = auto()

class OrderSide(Enum) : 
    Buy = auto() 
    Sell = auto() 

class OrderStatus(Enum)  :
    WAITING = auto() 
    FILLED = auto()
    CANCELED = auto() 

@dataclass 
class Order : 
    type : OrderType 
    side : OrderSide 
    offer : Decimal # offer to buy or sell 
    asset : Asset
    quantity : Decimal
    id : str
    agent : "Agent"
    status : OrderStatus = OrderStatus.WAITING

__all__ =  ["Order", "OrderSide", "OrderType", "OrderStatus"]
