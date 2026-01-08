from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import uuid4
from generics import Order, OrderSide, OrderType, OrderStatus
from collections import deque
import random

class Behavior(ABC):
    @abstractmethod
    def decide(self, agent, asset):
        pass

class RandomTrader(Behavior):
    def decide(self, agent, asset):
        if random.random() < 0.7:
            return None

        side = random.choice([OrderSide.Buy, OrderSide.Sell])
        quantity = Decimal(random.randint(1, 10))
        price = asset.price + Decimal(random.randint(-2, 2))

        if side == OrderSide.Buy and agent.cash < price * quantity:
            return None

        return Order(
            id=str(uuid4()),
            asset=asset,
            agent=agent,
            quantity=quantity,
            offer=max(price, Decimal(1)),
            side=side,
            type=OrderType.Limit,
            status=OrderStatus.WAITING
        )
    
class MarketMaker(Behavior):
    def __init__(self, spread=Decimal(2), size=Decimal(5)):
        self.spread = spread
        self.size = size

    def decide(self, agent, asset):
        mid = asset.price
        buy_price = mid - self.spread / 2
        sell_price = mid + self.spread / 2

        side = OrderSide.Buy if random.random() < 0.5 else OrderSide.Sell
        price = buy_price if side == OrderSide.Buy else sell_price

        return Order(
            id=str(uuid4()),
            asset=asset,
            agent=agent,
            quantity=self.size,
            offer=price,
            side=side,
            type=OrderType.Limit,
            status=OrderStatus.WAITING
        )

class MomentumTrader:
    def __init__(self, memory=5, threshold=Decimal(1)):
        self.prices = deque(maxlen=memory)
        self.threshold = threshold

    def decide(self, agent, asset):
        self.prices.append(asset.price)
        if len(self.prices) < 2:
            return None

        momentum = self.prices[-1] - self.prices[0]

        if abs(momentum) < self.threshold:
            return None

        side = OrderSide.Buy if momentum > 0 else OrderSide.Sell
        quantity = Decimal(random.randint(1, 5))  # small trades

        return Order(
            id=str(uuid4()),
            asset=asset,
            agent=agent,
            quantity=quantity,
            offer=asset.price,
            side=side,
            type=OrderType.Market,
            status=OrderStatus.WAITING
        )