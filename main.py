from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
import datetime as dt
import json

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your desired origins
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")

class Trade(BaseModel):
    assetClass: str = Field(default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: str = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrumentId: str = Field(description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrumentName: str = Field(description="The name of the instrument traded.")
    tradeDateTime: dt.datetime = Field(description="The date-time the Trade was executed")
    tradeDetails: TradeDetails = Field(description="The details of the trade, i.e. price, quantity")
    tradeId: str = Field(default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")


# Mocked data
trades = [
    Trade(
        tradeId="1",
        assetClass="Equity",
        counterparty="XYZ Bank",
        instrumentId="AAPL",
        instrumentName="Apple Inc",
        tradeDateTime=dt.datetime(2023, 6, 1, 10, 30),
        tradeDetails=TradeDetails(buySellIndicator="BUY", price=150.0, quantity=100),
        trader="John Doe"
    ),
    Trade(
        tradeId="2",
        assetClass="Share",
        counterparty="Z Bank",
        instrumentId="BBPL",
        instrumentName="Meta Inc",
        tradeDateTime=dt.datetime(2023, 7, 2, 11, 31),
        tradeDetails=TradeDetails(buySellIndicator="SELL", price=150.0, quantity=100),
        trader="Mohan Deepak"
    )
]



# Endpoint for root
@app.get("/")
def root():
    return {"msg : Welcome to fastapi"}

# Endpoint to fetch a list of trades
@app.get("/trades", response_model=List[Trade])
def get_trades():
    return trades


# Endpoint to fetch the trades by id
@app.get("/trades/{tradeId}", response_model= Trade)
def get_trades_by_id(tradeId : str):
    for trade in trades:
        if trade.tradeId == tradeId:
            return trade

    raise HTTPException(status_code=404, detail="Trade not found")


# Search Trades
@app.get("/trades/search", response_model=List[Trade])
def search_trades(search: str = Query(..., description="Text to search for in trade fields")):
    matched_trades = []
    for trade in trades:
        trade_dict = trade.dict()
        for field in ["counterparty", "instrumentId", "instrumentName", "trader"]:
            value = trade_dict.get(field, "")
            if isinstance(value, str) and search.lower() in value.lower():
                matched_trades.append(trade)
                break
    if len(matched_trades) == 0:
        raise HTTPException(status_code=404, detail="Trades not found")
    return matched_trades


# Filter trades with advanced parameters
@app.get("/trades/filter", response_model=List[Trade])
def filter_trades(
    asset_class: Optional[str] = None,
    end: Optional[dt.datetime] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    start: Optional[dt.datetime] = None,
    trade_type: Optional[str] = None
):
    filtered_trades = trades

    if asset_class:
        filtered_trades = [trade for trade in filtered_trades if trade.asset_class == asset_class]

    if end:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_date_time <= end]

    if max_price:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.price <= max_price]

    if min_price:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.price >= min_price]

    if start:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_date_time >= start]

    if trade_type:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.buySellIndicator == trade_type]

    return filtered_trades

