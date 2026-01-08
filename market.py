from dataclasses import astuple
from decimal import Decimal
from uuid import UUID, uuid4
from generics import Asset
from generics.datatypes import Trade
from generics.orders import Order, OrderSide, OrderStatus
from agent import Agent
from orderbook import OrderBook

class Market:
    
    def __init__(self, traders: dict[UUID, Agent], assets: dict[UUID, Asset]) -> None:
        self.traders = traders
        self.assets = assets

        self.history: list[Trade] = []
        self.cash = Decimal(0)

        self.orderbook_asset_map: dict[UUID, OrderBook] = self._create_orderbooks(assets)

    def _create_orderbooks(self, assets: dict[UUID, Asset]) -> dict[UUID, OrderBook]:
        orderbook_map: dict[UUID, OrderBook] = {}
        for asset_id, asset in assets.items():
            orderbook_map[asset_id] = OrderBook(asset_type=asset.type)
        return orderbook_map

    def buy(self, asset: Asset, trader: Agent, order: Order):
        if order.side != OrderSide.Buy:
            return OrderStatus.CANCELED

        if asset.price * order.quantity > trader.cash:
            return OrderStatus.CANCELED

        asset_orderbook = self.orderbook_asset_map[asset.id]
        trades = asset_orderbook.match(order)
        self.process_trades(trades)

        return order.status

    def sell(self, asset: Asset, trader: Agent, order: Order):
        if order.side != OrderSide.Sell:
            return OrderStatus.CANCELED

        asset_id = asset.id
        if trader.portfolio.get(asset_id, Decimal(0)) < order.quantity:
            return OrderStatus.CANCELED

        asset_orderbook = self.orderbook_asset_map[asset_id]
        trades = asset_orderbook.match(order)
        self.process_trades(trades)

        return order.status

    
    def process_trades(self, trades: list[Trade]):
        for trade in trades:
            buyer = trade.buyer
            seller = trade.seller
            trade_asset = trade.trade_asset
            quantity = trade.quantity
            amount_exchanged = trade.amount_exchanged

            asset_id = trade_asset.id

            buyer.cash -= amount_exchanged
            seller.cash += amount_exchanged
            buyer.portfolio[asset_id] = buyer.portfolio.get(asset_id, Decimal(0)) + quantity

            seller.portfolio[asset_id] = seller.portfolio.get(asset_id, Decimal(0)) - quantity
            if seller.portfolio[asset_id] == 0:
                del seller.portfolio[asset_id]

            trade_asset.price = trade_asset.price = max(Decimal(0), amount_exchanged / quantity)

            self.history.append(trade)

    def add_asset(self, asset: Asset):
        asset_id = uuid4()
        self.assets[asset_id] = asset
        self.orderbook_asset_map[asset_id] = OrderBook(asset_type=asset.type)
