# THIS IS THE SERVER WITH SIMULATED DELAY TIMES  
from dotenv import load_dotenv
from generics.asset import Asset
from yfrlt import Client
import time 
import yfinance as yf 

class DataFeed : 
    def __init__(self, symbols_track : list[str]) -> None:
        self.client = Client()
        self.track : dict[str, Asset] = {} 
        for symbol in symbols_track :
            print(symbol)
            self.client.subscribe([symbol], self.on_price_update)
            self.track[symbol] = self.get_snapshot_price(symbol)
        print(self.track)
        self.client.start()

    def get_snapshot_price(self, symbol : str ) : 
        t =  yf.Ticker(symbol) 
        price = t.fast_info['last_price']
        return price 

    def on_price_update(self, data):
        self.track[data.symbol] = data.price 
        print(data.symbol, data.price, data.change_percent)
        print(self.track)

    def get_current_price(self, symbol : str) : 
        return self.track[symbol]

    def add_symbol(self, symbol : str) : 
        self.client.subscribe(symbol)
        self.track[symbol] = self.get_snapshot_price(symbol)

