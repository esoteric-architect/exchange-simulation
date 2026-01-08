from generics import Order, OrderStatus, TreeNode, Trade, OrderSide
from typing import Callable
from functools import wraps

def fill_order(side : OrderSide) : 
    def decorater(matching_function : Callable) :
        @wraps(matching_function)
        def wrapper(self, root : TreeNode | None, order : Order, trades : list[Trade]) : 
            if root is None or order.status == OrderStatus.FILLED : 
                return  
            
            first, second =  (root.left, root.right) if side == OrderSide.Buy else (root.right, root.left)

            wrapper(self, first, order, trades) 
            if order.status == OrderStatus.FILLED : 
                return 
            matching_function(self, root.value, order, trades) 
            if order.status == OrderStatus.FILLED : 
                return 
            wrapper(self, second, order, trades)

        return wrapper 
    return decorater  
