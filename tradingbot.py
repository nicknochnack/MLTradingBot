from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.data.historical.news import NewsClient
from timedelta import Timedelta
from finbert_utils import estimate_sentiment
from dotenv import load_dotenv
import os


ALPACA_CREDS = {
    "API_KEY": "ALPACA_Key",
    "API_SECRET": "ALPACA_Secret",
    "PAPER": True
}



class MLTrader(Strategy):
    def initialize(self, symbol: str = "SPY", cash_at_risk: float = .5):

        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.newsClient = NewsClient(ALPACA_CREDS["API_KEY"],ALPACA_CREDS["API_SECRET"])

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_alpaca_news(self,today, three_days_prior):
        newsRequest = NewsRequest(
            symbols=self.symbol,
            start=three_days_prior,
            end=today,
            limit=20
        )
        news = self.newsClient.get_news(newsRequest)
        headlines = []
        summaries = []

        for news_item in news.news:
            headlines.append(news_item.headline)
            summaries.append(news_item.summary)

        return headlines

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.get_alpaca_news(today, three_days_prior)
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        print(sentiment, probability)

        if cash > last_price:
            if sentiment == "positive" and probability > .999:
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price * 1.20,
                    stop_loss_price=last_price * .95
                )
                self.submit_order(order)
                print("buying")
                self.last_trade = "buy"
            elif sentiment == "negative" and probability > .999:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price * .8,
                    stop_loss_price=last_price * 1.05
                )
                self.submit_order(order)
                print("selling")
                self.last_trade = "sell"


if __name__ == "__main__":
    print("Initializing MLTrader")
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(name='mlstrat', broker=broker,
                        parameters={"symbol": "SPY",
                                    "cash_at_risk": .5})
    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters={"symbol": "SPY", "cash_at_risk": .5}
    )
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()
