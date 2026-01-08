from agent import Agent
from generics import TreeNode, Order, OrderType, OrderSide, Asset, LinkedListNode, PriceLevel, OrderStatus, Trade
from decimal import Decimal
from uuid import uuid4
from datastructures import AVLTree
from order_book_decoraters import fill_order

class OrderBook :

    def __init__(self, asset_type : str) -> None:
        self.asset_type = asset_type
        self.buy_side_tree = AVLTree() 
        self.sell_side_tree = AVLTree()
        self.order_map : dict[str, LinkedListNode] = {} 
        self.dispatcher = self._init_dispatcher()

    def _init_dispatcher(self) : 
        # TODO make this dynamic 
        return {
                (OrderType.Market, OrderSide.Buy) : lambda root, order : self._fill_market_order(root, order), 
                (OrderType.Market, OrderSide.Sell) : lambda root, order : self._fill_market_order(root, order),  
                (OrderType.Limit, OrderSide.Buy) : lambda root, order : self._fill_limit_order(root, order),
                (OrderType.Limit, OrderSide.Sell) : lambda root, order : self._fill_limit_order(root, order)}

    def _insert_to_tree(self, order : Order, tree : AVLTree) -> None: 
        if price_level := tree.search(order.offer) : 
            price_level.insert_order(order)
            if price_level.tail : 
                self.order_map[order.id] = price_level.tail 
        else : 
            new_price_level = PriceLevel(price=order.offer) 
            new_price_level.insert_order(order)
            tree.insert(TreeNode(value=new_price_level))

            if new_price_level.tail : 
                self.order_map[order.id] = new_price_level.tail

    def insert(self, order : Order) :
        
        if order.asset.type == self.asset_type  : 

            if order.side == OrderSide.Buy : 
                self._insert_to_tree(order, self.buy_side_tree)

            elif order.side == OrderSide.Sell : 
                self._insert_to_tree(order, self.sell_side_tree)

            else : 
                raise NotImplementedError(f"Order Side {order.side} is not implemented for OrderBook")

        else : 
            raise TypeError(f"Wrong Asset")

    def cancel(self, order_id : str) -> bool :
        pointer = self.order_map.get(order_id)
        if pointer is None:
            return False

        side = pointer.value.side
        price = pointer.value.offer

        if side == OrderSide.Buy:
            price_level = self.buy_side_tree.search(price)
        else:
            price_level = self.sell_side_tree.search(price)
        
        if price_level:  

            if pointer.prev:
                pointer.prev.next = pointer.next
            else:
                price_level.levels = pointer.next 

            if pointer.next:
                pointer.next.prev = pointer.prev
            else:
                price_level.tail = pointer.prev  

            del self.order_map[order_id]

            # If the price level is empty, remove from AVL tree
            if price_level and price_level.levels is  None :
                # TODO Stop using dummy nodes instead just use price to compare -> less memory  
                if side == OrderSide.Buy:
                    self.buy_side_tree.delete(TreeNode(value=PriceLevel(price=price))) 
                else:
                    self.sell_side_tree.delete(TreeNode(value=PriceLevel(price=price)))
            
            return True 

         
        raise RuntimeError(f"Order exists but its price level doesn't")


    def get_best_bid(self) -> PriceLevel | None : 
        if self.buy_side_tree.root is not None : 
            node = self._get_best_bid(self.buy_side_tree.root) 
            price_level = node.value 
            return price_level
        return None 

    def get_best_ask(self) -> PriceLevel | None: 
        if self.sell_side_tree.root is not None: 
            node = self._get_best_ask(self.sell_side_tree.root)
            price_level = node.value
            return price_level
        return None

    def _get_best_bid(self, node : TreeNode) -> TreeNode: 

        while node.right : 
            node = node.right 

        return node

    def _get_best_ask(self, node : TreeNode) -> TreeNode:

        while node.left : 
            node = node.left 

        return node 
        
    def get_order(self, order_id : str) -> Order | None: 
        pointer = self.order_map.get(order_id, None)
        return pointer.value if pointer else None
    

    def _create_default_trade(self, buyer : Agent, seller : Agent, asset : Asset) -> Trade :

        return Trade(buyer, seller, str(uuid4()), asset, quantity=Decimal(0), amount_exchanged=Decimal(0))
 
    
    def _fill_market_at_price_level(self, price_level : PriceLevel, order : Order) -> list[Trade]  :
        
        trades = [ ]
        order_slot = price_level.levels

        while order_slot and order.quantity > 0: 
            current_order = order_slot.value 
            order_quantity_difference = current_order.quantity - order.quantity 
            
            if order.side == OrderSide.Buy : 
                trade = self._create_default_trade(buyer = order.agent, seller = current_order.agent, asset = order.asset)
            else : 
                trade = self._create_default_trade(buyer = current_order.agent, seller = order.agent, asset = order.asset)

            if order_quantity_difference >= 0 : 
                # fill  
                amount_exchanged = order.quantity * current_order.offer # could be either 
                trade.quantity = order.quantity 
                trade.amount_exchanged = amount_exchanged 
                trades.append(trade) 
                
                current_order.quantity -= order.quantity 
                order.quantity = Decimal(0) 
                order.status = OrderStatus.FILLED
                
                if current_order.quantity == 0 : 
                    current_order.status = OrderStatus.FILLED 
                    self._delete_order_from_price_level(price_level, order_slot)

                return trades 

            else : 
                #take                
                amount_exchanged = current_order.offer * current_order.quantity # this quantity is less than 
                trade.quantity = current_order.quantity 
                trade.amount_exchanged = amount_exchanged
                trades.append(trade)

                order.quantity -= current_order.quantity
                current_order.quantity = Decimal(0) 
                current_order.status = OrderStatus.FILLED 
                self._delete_order_from_price_level(price_level, order_slot)

            order_slot = order_slot.next 

        return trades 
    
    def _delete_order_from_price_level(self, price_level : PriceLevel, node : LinkedListNode) -> None: 

        if node.prev : 
            node.prev.next = node.next 
        else : 
            price_level.levels = node.next 

        if node.next : 
            node.next.prev = node.prev 
        else : 
            price_level.tail = node.prev 
             
 
    def market_order_matching_function(self, price_level : PriceLevel, order : Order, trades : list[Trade]) : 
        trades.extend(self._fill_market_at_price_level(price_level, order))

    def _fill_market_order(self, tree : AVLTree, order : Order) :
        trades = [] 
        root = tree.root
        if tree.root is None :
            order.status = OrderStatus.CANCELED
            return trades 

        side = OrderSide.Buy if order.side == OrderSide.Sell else OrderSide.Sell
        fill_order(side)(matching_function=OrderBook.market_order_matching_function)(self, root, order, trades)
        return trades 

    def _fill_limit_order(self, tree : AVLTree, order : Order) : 
        price_level = tree.search(order.offer) 
        trades =  []
        if price_level : 
            self.market_order_matching_function(price_level, order, trades) 
        return trades    
 
    def match(self, order : Order) : 
        if order.asset.type != self.asset_type : 
            raise TypeError(f"Order asset type {order.asset} is not the same as the Orderbook asset type {self.asset_type}")
        
        tree = self.sell_side_tree if order.side == OrderSide.Buy else self.buy_side_tree 
        fill = self.dispatcher[(order.type, order.side)]
        trades = fill(tree, order) 
        if order.status != OrderStatus.FILLED : 
            self.insert(order)
        return trades 
    
    def get_top_bids(self, n: int) -> list[tuple[Decimal, Decimal]]:
        results: list[tuple[Decimal, Decimal]] = []
        def traverse(node):
            if not node or len(results) >= n:
                return
            
            traverse(node.right)

            if len(results) < n:
                price_level: PriceLevel = node.value
                total_qty = Decimal(0)
                current = price_level.levels
                while current:
                    total_qty += current.value.quantity
                    current = current.next
                if total_qty > 0:
                    results.append((price_level.price, total_qty))

            traverse(node.left)

        traverse(self.buy_side_tree.root)
        return results

    def get_top_asks(self, n: int) -> list[tuple[Decimal, Decimal]]:
        results: list[tuple[Decimal, Decimal]] = []
        def traverse(node):
            if not node or len(results) >= n:
                return
            
            traverse(node.left)

            if len(results) < n:
                price_level: PriceLevel = node.value
                total_qty = Decimal(0)
                current = price_level.levels
                while current:
                    total_qty += current.value.quantity
                    current = current.next
                if total_qty > 0:
                    results.append((price_level.price, total_qty))

            traverse(node.right)

        traverse(self.sell_side_tree.root)
        return results
