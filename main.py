from decimal import Decimal
from uuid import uuid4
from agent import Agent
from generics import Asset, OrderSide, OrderType, OrderStatus
from market import Market
from behaviors import RandomTrader, MarketMaker, MomentumTrader
import random
from dash import Dash, dcc, html, no_update
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import webbrowser
from threading import Timer

NUM_AGENTS = 200
SIMULATION_STEPS = 100
TRADES_TO_SHOW = 50
DEPTH_LEVELS = 10

def setup_market():
    apple_stock = Asset(
        type="stock",
        id=uuid4(),
        price=Decimal(150),
        quantity=Decimal(1000)
    )
    agents = {}
    for _ in range(NUM_AGENTS):
        cash = Decimal(random.randint(50_000, 150_000))
        portfolio = {apple_stock.id: Decimal(random.randint(0, 100))} if random.random() < 0.3 else {}
        behavior = random.choice([RandomTrader(), MarketMaker(), MomentumTrader()])
        agent = Agent(cash, portfolio, behavior=behavior)
        agents[uuid4()] = agent
    market = Market(agents, {apple_stock.id: apple_stock})
    return market, list(agents.values()), apple_stock

def simulate_step(market, agents, asset):
    for agent in agents:
        order = agent.behavior.decide(agent, asset)
        if order is None:
            continue
        if order.side == OrderSide.Buy:
            market.buy(asset, agent, order)
        else:
            market.sell(asset, agent, order)

def run_simulation(market, agents, asset, steps):
    price_history = []
    bid_history = []
    ask_history = []
    volume_history = []

    for step in range(steps):
        simulate_step(market, agents, asset)

        price_history.append(float(asset.price))
        orderbook = market.orderbook_asset_map[asset.id]
        best_bid = orderbook.get_best_bid()
        best_ask = orderbook.get_best_ask()
        bid_history.append(float(best_bid.price) if best_bid else None)
        ask_history.append(float(best_ask.price) if best_ask else None)
        volume_history.append(sum([float(trade.quantity) for trade in market.history[-len(agents):]]))

        yield price_history, bid_history, ask_history, volume_history, market.history[-TRADES_TO_SHOW:], market

# Dash App
app = Dash(__name__)
app.title = "Exchange Simulation Dashboard"

app.layout = html.Div([
    html.H2("Exchange Simulation Dashboard", style={'textAlign':'center'}),
    html.Div([
        html.Div([
            dcc.Graph(id='live-price-chart'),
            dcc.Graph(id='orderbook-depth')  # New depth chart
        ], style={'width':'65%', 'display':'inline-block'}),
        html.Div([
            html.H4("Top Agents"),
            dcc.Graph(id='top-agents'),
            html.H4("Summary Stats"),
            html.Div(id='summary-stats', style={'fontSize':16})
        ], style={'width':'34%', 
                  'display':'inline-block', 
                  'verticalAlign':'top', 
                  'paddingLeft': '1%',
                  })
    ]),
    dcc.Interval(
        id='interval-component',
        interval=500,
        n_intervals=0
    )
], style={'width':'95%', 
          'margin':'auto',
          "fontFamily": "Open Sans, Arial, sans-serif"
          })

# Global simulation objects
market, agents, asset = setup_market()
sim_generator = run_simulation(market, agents, asset, SIMULATION_STEPS)

@app.callback(
    Output('live-price-chart', 'figure'),
    Output('orderbook-depth', 'figure'),
    Output('top-agents', 'figure'),
    Output('summary-stats', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    try:
        price_history, bid_history, ask_history, volume_history, recent_trades, market_state = next(sim_generator)
    except StopIteration:
        return no_update, no_update, no_update, no_update

    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(y=price_history, mode='lines+markers', name='Price', line=dict(color='black')))
    price_fig.add_trace(go.Scatter(y=bid_history, mode='lines', name='Best Bid', line=dict(color='green', dash='dash')))
    price_fig.add_trace(go.Scatter(y=ask_history, mode='lines', name='Best Ask', line=dict(color='red', dash='dash')))
    price_fig.update_layout(title="Price & Orderbook", yaxis=dict(title='Price'), xaxis=dict(title='Step'))

    orderbook = market_state.orderbook_asset_map[asset.id]

    def get_top_orders(tree, n, reverse=False):
        if tree.root is None:
            return []

        nodes = []
        stack = []
        node = tree.root

        while stack or node:
            while node:
                stack.append(node)
                node = node.right if reverse else node.left

            node = stack.pop()
            pl = node.value

            total_qty = 0
            order_node = pl.levels
            while order_node:
                total_qty += float(order_node.value.quantity)
                order_node = order_node.next

            nodes.append((float(pl.price), total_qty))

            if len(nodes) >= n:
                break

            node = node.left if reverse else node.right

        return nodes


    top_bids = get_top_orders(orderbook.buy_side_tree, DEPTH_LEVELS, reverse=True)
    top_asks = get_top_orders(orderbook.sell_side_tree, DEPTH_LEVELS)

    depth_fig = go.Figure()
    if top_bids:
        prices, qtys = zip(*top_bids)
        depth_fig.add_bar(x=qtys, y=prices, orientation='h', name="Bids", marker_color='green')
    if top_asks:
        prices, qtys = zip(*top_asks)
        depth_fig.add_bar(x=qtys, y=prices, orientation='h', name="Asks", marker_color='red')
    depth_fig.update_layout(title="Order Book Depth", barmode="overlay", xaxis_title="Quantity", yaxis_title="Price")

    top_agents = sorted(agents, key=lambda a: a.cash, reverse=True)[:5]
    names = [f"{a.behavior.__class__.__name__}" for a in top_agents]
    cash_values = [float(a.cash) for a in top_agents]
    share_values = [float(a.portfolio.get(asset.id,0)) for a in top_agents]
    top_agents_fig = go.Figure()
    top_agents_fig.add_trace(go.Bar(y=names, x=cash_values, name='Cash', orientation='h', marker_color='gold'))
    top_agents_fig.add_trace(go.Bar(y=names, x=share_values, name='Shares', orientation='h', marker_color='lightblue'))
    top_agents_fig.update_layout(title="Top 5 Agents", barmode='stack', xaxis_title="Value", yaxis_title="Agent Type")

    total_trades = len(market_state.history)
    last_price = float(asset.price)
    total_volume = sum([float(t.quantity) for t in market_state.history])
    summary_text = [
        html.P(f"Simulation Step: {len(price_history)}"),
        html.P(f"Last Price: {last_price}"),
        html.P(f"Total Trades: {total_trades}"),
        html.P(f"Total Volume: {total_volume}")
    ]

    return price_fig, depth_fig, top_agents_fig, summary_text

if __name__ == "__main__":
    port = 8050
    Timer(1, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(debug=True, port=port)
