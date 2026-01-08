from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .orders import Order
from .asset import Asset
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent import Agent

@dataclass 
class LinkedListNode : 
    value : Order 
    next  : LinkedListNode | None = None 
    prev : LinkedListNode | None = None

@dataclass 
class PriceLevel : 
    price : Decimal 
    levels : LinkedListNode | None = None 
    tail : LinkedListNode | None = None

    def __post_init__(self)  :
        if self.tail is None and self.levels is not None : 
            runner = self.levels 
            while runner.next :
                runner = runner.next
            self.tail = runner  

    def insert_order(self, order : Order) : 
        to_add = LinkedListNode(value=order)
        if self.tail : # levels could be uninitialized 
            to_add.prev = self.tail 
            self.tail.next = to_add
        else : 
            self.levels = to_add

        self.tail = to_add

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, PriceLevel) : 
            return NotImplemented
        return self.price == other.price 

    def __lt__(self, other : object, /) -> bool : 
        if not isinstance(other, PriceLevel) : 
            return NotImplemented 
        return self.price < other.price

    def __le__(self, other : object, /) -> bool : 
        if not isinstance(other, PriceLevel) : 
            return NotImplemented 
        return self.price <= other.price

@dataclass 
class TreeNode : 
    value : PriceLevel
    left : TreeNode | None = None
    right : TreeNode | None = None  
    height : int = 0

@dataclass 
class Trade : 
    buyer : "Agent" 
    seller : "Agent"
    trade_id :  str
    trade_asset : Asset
    quantity : Decimal 
    amount_exchanged : Decimal 



__all__ = ['TreeNode', 'LinkedListNode', 'PriceLevel', "Trade"]
