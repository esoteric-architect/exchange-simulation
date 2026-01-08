from decimal import Decimal 
from uuid import uuid4 
from generics import LinkedListNode, Order,Asset,  OrderSide, OrderType, TreeNode, PriceLevel 
from datastructures import AVLTree 
from agent import Agent
import random


agent1 = Agent(id=uuid4(), cash=Decimal(500), portfilio=[])
agent2 = Agent(id=uuid4(), cash=Decimal(1500), portfilio=[])
agent3 = Agent(id=uuid4(), cash=Decimal(5000), portfilio=[])

assets = (Asset("cool stock", id=uuid4(), price=Decimal(102), owner=uuid4()),
           Asset("youtube", id=uuid4(), price=Decimal(1000), owner=uuid4()),
           Asset("11labs", id=uuid4(), price=Decimal(50), owner=uuid4()),
           Asset("jane street", id=uuid4(), price=Decimal(20), owner=uuid4())
           )

o1 = Order(
        type=OrderType.GoodTillCancel,
        side=OrderSide.Buy,
        offer=Decimal(200),
        asset=random.choice(assets),
        quantity=Decimal(10), 
        id=str(uuid4()), 
        agent = agent1
        ) 

o2 = Order(
        type=OrderType.Limit,
        side=OrderSide.Sell,
        offer=Decimal(100),
        asset=random.choice(assets),
        quantity=Decimal(20), 
        id=str(uuid4()), 
        agent = agent2
        ) 

o3 = Order(
        type=OrderType.Market,
        side=OrderSide.Buy,
        offer=Decimal(140),
        asset=random.choice(assets),
        quantity=Decimal(40),
        id=str(uuid4()), 
        agent = agent3
        )

l1 = LinkedListNode(value=o1)
l2 = LinkedListNode(value=o2)
l3 = LinkedListNode(value=o3)

price_level1 = PriceLevel(price=Decimal(300), levels=l1)
price_level2 = PriceLevel(price=Decimal(100), levels=l2)
price_level3= PriceLevel(price=Decimal(200), levels=l3)

avl = AVLTree()
t1 = TreeNode(value=price_level1) 
t2 = TreeNode(value=price_level2)  
t3 = TreeNode(value=price_level3)  

avl.insert(t1)
avl.insert(t2)
avl.insert(t3)

print(avl.root.value.price, avl.root.left.value.price, avl.root.right.value.price)
print(avl.search(Decimal(300)))

