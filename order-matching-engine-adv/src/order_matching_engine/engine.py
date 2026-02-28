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
            price = None
        else:
            market = False
            limit = True

        price, bid, ask = self._sample()

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
        same: list[Order] = []
        opp: list[Order] = []

        if order.bid:
            same = self.buy_book
            opp = self.sell_book
        elif order.ask:
            same = self.sell_book
            opp = self.buy_book

        if order.limit:
            if len(same) == 0:
                same.append(order)
            else:
                self._insert_order(order, same)

        if order.market:
            if len(opp) != 0:
                order.price = opp[0].price

                if len(same) == 0:
                    same.append(order)
                else:
                    self._insert_order(order, same)
            else:
                if len(same) != 0:
                    order.price = same[0].price
                    self._insert_order(order, same)
                else:
                    order.price = self.config.eq_price
                same.append(order)

    def _insert_order(self, order: Order, book: list[Order]) -> None:
        if order.bid:
            book = self.buy_book
        elif order.ask:
            book = self.sell_book

        if Order.better_than(order, book[0]):
            book.insert(0, order)
        elif not Order.better_than(order, book[len(book) - 1]):
            book.append(order)
        else:
            for entry in book:
                if Order.better_than(order, entry):
                    insert_point = book.index(entry) - 1
                    book.insert(insert_point, order)
                    break

    def remove_from_book(self, order: Order) -> None:
        book: list[Order] = []
        if order.bid:
            book = self.buy_book
        elif order.ask:
            book = self.sell_book

        discard = None
        for entry in book:
            if entry.order_id == order.order_id:
                discard = entry
                break

        if discard:
            book.remove(discard)

    def reduce_quantity(self, order: Order, quantity: int) -> None:
        book: list[Order] = []
        if order.bid:
            book = self.buy_book
        elif order.ask:
            book = self.sell_book

        for entry in book:
            if entry.order_id == order.order_id:
                entry.quantity = entry.quantity - quantity
                break

    def match(self) -> None:
        if len(self.buy_book) == 0 or len(self.sell_book) == 0:
            return

        top_bid = self.buy_book[0]
        top_ask = self.sell_book[0]
        tx_price = top_ask.price if top_ask.price else self.config.eq_price
        tx_quantity = min(top_bid.quantity, top_ask.quantity)

        if top_bid.price and top_ask.price and top_bid.price >= top_ask.price:
            self._create_tx(top_bid, top_ask, tx_price, tx_quantity)

            if top_bid.quantity < top_ask.quantity:
                self.remove_from_book(top_bid)
                self.reduce_quantity(top_ask, top_bid.quantity)
            elif top_bid.quantity == top_ask.quantity:
                self.remove_from_book(top_bid)
                self.remove_from_book(top_ask)
            elif top_bid.quantity > top_ask.quantity:
                self.remove_from_book(top_ask)
                self.reduce_quantity(top_bid, top_ask.quantity)

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
