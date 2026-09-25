import datetime
import random
from typing import Any

from .config import EngineConfig
from .models import Order


class MatchingEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.tx_count = 0
        self.buy_book: list[Order] = []
        self.sell_book: list[Order] = []
        self.fill_book: list[dict[str, Any]] = []

    def generate_order(self) -> Order:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        order_id = Order.id_counter
        Order.id_counter += 1
        quantity = random.randint(1, 100)

        random_type = random.randint(1, 10)
        if random_type < 8:
            market = True
            limit = False
        else:
            market = False
            limit = True

        price, bid, ask = self._sample()  # the sampled price also decides the side
        if market:
            price = None  # a market order trades at the resting orders' prices

        order = Order(timestamp, order_id, quantity, market, limit, price, bid, ask)
        self.add_to_book(order)
        return order

    def _sample(self) -> tuple[float | None, bool, bool]:
        ask: bool = False
        bid: bool = False
        std_dev = self.config.std_dev
        price = round(random.normalvariate(self.config.eq_price, std_dev), 2)

        if price > self.config.eq_price:
            if price > (self.config.eq_price + (0.1 * std_dev)):
                ask = True
                bid = False
            elif price <= (self.config.eq_price + (0.1 * std_dev)):
                x = random.randint(1, 10)
                if x < 9:
                    ask = True
                    bid = False
                else:
                    ask = False
                    bid = True

        elif price <= self.config.eq_price:
            if price < (self.config.eq_price - (0.1 * std_dev)):
                bid = True
                ask = False
            elif price >= (self.config.eq_price - (0.1 * std_dev)):
                x = random.randint(1, 10)
                if x < 9:
                    bid = True
                    ask = False
                else:
                    bid = False
                    ask = True

        return price, bid, ask

    def add_to_book(self, order: Order) -> None:
        """Match an incoming order, then rest what is left of a limit order.

        A market order trades against the opposite side until it is filled or that side is
        empty; any unfilled remainder is cancelled, so market orders never rest in the book.
        """
        if order.bid:
            same, opp = self.buy_book, self.sell_book
        else:
            same, opp = self.sell_book, self.buy_book

        self.match(order, opp)

        if order.limit and order.quantity > 0:
            self._insert_order(order, same)

    @staticmethod
    def _insert_order(order: Order, book: list[Order]) -> None:
        """Keep the book best price first, oldest first within a price level."""
        for index, entry in enumerate(book):
            if order.better_than(entry):
                book.insert(index, order)
                return
        book.append(order)

    @staticmethod
    def _crosses(order: Order, resting: Order) -> bool:
        if order.market:
            return True
        if order.bid:
            return order.price >= resting.price
        return order.price <= resting.price

    def match(self, order: Order, opp: list[Order]) -> None:
        """Trade the incoming order against the best resting orders while the prices cross.

        Each trade is at the resting order's price; a partly filled resting order keeps its place.
        """
        while order.quantity > 0 and opp and self._crosses(order, opp[0]):
            resting = opp[0]
            quantity = min(order.quantity, resting.quantity)
            bid, ask = (order, resting) if order.bid else (resting, order)
            self._create_tx(bid, ask, resting.price, quantity)

            order.quantity -= quantity
            resting.quantity -= quantity
            if resting.quantity == 0:
                opp.pop(0)

    def _create_tx(self, bid: Order, ask: Order, price: float, quantity: int) -> None:
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        time = datetime.datetime.now().strftime("%H:%M:%S")
        tx_id = self.tx_count
        self.tx_count = self.tx_count + 1
        bid_id = bid.order_id
        ask_id = ask.order_id

        tx = {
            "Date": date,
            "Time": time,
            "Transaction ID": tx_id,
            "Bid ID": bid_id,
            "Ask ID": ask_id,
            "Price ($)": price,
            "Quantity": quantity,
        }

        self.fill_book.insert(0, tx)
