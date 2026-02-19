import datetime
import random
import tkinter.ttk as ttk
from tkinter import Tk


class Order:
    id_counter = 1

    def __init__(self, timestamp, order_id, quantity, market, limit, price, bid: bool, ask: bool):
        self.timestamp = timestamp
        self.order_id = order_id
        self.quantity = quantity
        self.market = market
        self.limit = limit
        self.price = price
        self.bid = bid
        self.ask = ask

    # Defines a method for comparing quotes in the book
    def better_than(self, other):
        if self.bid:
            if self.price > other.price:
                return True
            return False

        if self.ask:
            if self.price > other.price:
                return False
            return True

    def __repr__(self):
        return f"Bid: {self.bid} Ask: {self.ask}"


class Window:
    window: Tk
    bid_tree: ttk.Treeview
    ask_tree: ttk.Treeview
    fill_tree: ttk.Treeview

    def __init__(self):
        self.tx_count = 0
        self.cache_length = 15
        self.buy_book = []
        self.sell_book = []
        self.buy_cache = []
        self.sell_cache = []
        self.fill_cache = []
        self.fill_book = []

        self.eq_price = 200  # further development: periodically change this

        self.window = Tk()
        self.window.title("Order Matching Engine")
        self.window.geometry("870x470")

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)

        self.fills_frame = ttk.LabelFrame(self.window, text="Filled orders")
        self.bid_frame = ttk.LabelFrame(self.window, text="Bids")
        self.ask_frame = ttk.LabelFrame(self.window, text="Offers")

        self.bid_tree = ttk.Treeview(self.bid_frame, columns=("Price", "Quantity"), show="headings")
        self.bid_tree.heading("#1", text="Price")
        self.bid_tree.heading("#2", text="Quantity")
        self.bid_tree.pack(fill="both")
        self.bid_frame.grid(row=0, column=0, sticky="nsew")

        self.ask_tree = ttk.Treeview(self.ask_frame, columns=("Price2", "Quantity2"), show="headings")
        self.ask_tree.heading("#1", text="Price")
        self.ask_tree.heading("#2", text="Quantity")
        self.ask_tree.pack(fill="both")
        self.ask_frame.grid(row=0, column=1, sticky="nsew")

        self.fill_tree = ttk.Treeview(
            self.fills_frame,
            columns=("Date", "Time", "Price ($)", "Quantity", "Transaction ID", "Bid ID", "Ask ID"),
            show="headings",
        )
        self.fill_tree.column("#1", width=120)
        self.fill_tree.column("#2", width=120)
        self.fill_tree.column("#3", width=120)
        self.fill_tree.column("#4", width=120)
        self.fill_tree.column("#5", width=120)
        self.fill_tree.column("#6", width=120)
        self.fill_tree.column("#7", width=120)
        self.fill_tree.heading("#1", text="Date")
        self.fill_tree.heading("#2", text="Time")
        self.fill_tree.heading("#3", text="Price ($)")
        self.fill_tree.heading("#4", text="Quantity")
        self.fill_tree.heading("#5", text="Transaction ID")
        self.fill_tree.heading("#6", text="Bid ID")
        self.fill_tree.heading("#7", text="Ask ID")
        self.fill_tree.pack(fill="both")
        self.fills_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

    def draw_book(self, cache):  # refactoring opportunity
        if cache == self.buy_cache:
            tree = self.bid_tree
        elif cache == self.sell_cache:
            tree = self.ask_tree
        elif cache == self.fill_cache:
            tree = self.fill_tree

        if tree == self.bid_tree or tree == self.ask_tree:
            tree.delete(*tree.get_children())
            i = 0
            iid = 0

            if len(cache) == 0:
                return

            for record in cache:  # refactoring opportunity
                if record is None:
                    continue

                tree.insert(parent="", index=i, iid=iid, text="", values=(record.get("price"), record.get("quantity")))
                i = i + 1
                iid = iid + 1

        else:
            tree.delete(*tree.get_children())
            i = 0
            iid = 0

            for record in cache:
                tree.insert(
                    parent="",
                    index=i,
                    iid=iid,
                    text="",
                    values=(
                        record.get("Date"),
                        record.get("Time"),
                        record.get("Price ($)"),
                        record.get("Quantity"),
                        record.get("Transaction ID"),
                        record.get("Bid ID"),
                        record.get("Ask ID"),
                    ),
                )
                i = i + 1
                iid = iid + 1

    def update_cache(self, book):
        if book == self.fill_book:
            cache = self.fill_cache
        elif book == self.buy_book:
            cache = self.buy_cache
        elif book == self.sell_book:
            cache = self.sell_cache

        cache.clear()

        if cache == self.fill_cache:
            if len(self.fill_book) < self.cache_length:
                for x in range(len(self.fill_book)):
                    self.fill_cache.append(self.fill_book[x])

            else:
                for x in range(self.cache_length):
                    self.fill_cache.append(self.fill_book[x])

        elif cache == self.buy_cache or cache == self.sell_cache:
            empty_list = [None] * 10
            cache.extend(empty_list)

            if len(book) == 0:
                self.draw_book(cache)
                return

            index = 0
            current_price = book[0].price
            quantity = 0

            while index < 10:
                for order in book:
                    if order.price == current_price:
                        quantity = quantity + order.quantity

                cache_order = {"quantity": quantity, "price": current_price}

                cache[index] = cache_order

                for order in book:
                    if book == self.sell_book:
                        if order.price > current_price:
                            current_price = order.price
                            break

                    elif book == self.buy_book:
                        if order.price < current_price:
                            current_price = order.price
                            break

                quantity = 0
                index = index + 1

        self.draw_book(cache)

    def add_to_book(self, order):
        same = []
        opp = []

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
                self.insert_order(order, same)

        if order.market:
            if len(opp) != 0:
                order.price = opp[0].price

                if len(same) == 0:
                    same.append(order)
                else:
                    self.insert_order(order, same)

            else:
                if len(same) != 0:
                    order.price = same[0].price
                    self.insert_order(order, same)

                else:
                    order.price = self.eq_price
                same.append(order)

    def generate_order(self):
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

        price, bid, ask = self.sample()

        order = Order(timestamp, order_id, quantity, market, limit, price, bid, ask)
        self.add_to_book(order)

    def sample(self):
        # further development: shift the mean randomly, periodically (sample)
        ask = None
        bid = None
        std_dev = 25
        # further development: include a method of catching 0 or negative values
        price = round(random.normalvariate(self.eq_price, std_dev), 2)

        if price > self.eq_price:
            if price > (self.eq_price + (0.1 * std_dev)):
                ask = True
                bid = False

            elif price <= (self.eq_price + (0.1 * std_dev)):
                x = random.randint(1, 10)
                if x < 9:
                    ask = True
                    bid = False
                else:
                    ask = False
                    bid = True

        elif price <= self.eq_price:
            if price < (self.eq_price - (0.1 * std_dev)):
                bid = True
                ask = False

            elif price >= (self.eq_price - (0.1 * std_dev)):
                x = random.randint(1, 10)
                if x < 9:
                    bid = True
                    ask = False
                else:
                    bid = False
                    ask = True

        return price, bid, ask

    def insert_order(self, order, book):
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

    def add_to_fills(self, tx):
        self.fill_book.insert(0, tx)
        self.update_cache(self.fill_book)

    def create_tx(self, bid, ask, price, quantity):
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

        self.add_to_fills(tx)

    def remove_from_book(self, order):
        book = []
        if order.bid:
            book = self.buy_book
        elif order.ask:
            book = self.sell_book

        for entry in book:
            if entry.order_id == order.order_id:
                discard = entry
                break

        book.remove(discard)
        self.update_cache(book)

    def reduce_quantity(self, order, quantity):
        book = []
        if order.bid:
            book = self.buy_book
        elif order.ask:
            book = self.sell_book

        for entry in book:
            if entry.order_id == order.order_id:
                entry.quantity = entry.quantity - quantity
                break

        self.update_cache(book)

    def match(self):
        top_bid = self.buy_book[0]
        top_ask = self.sell_book[0]
        tx_price = top_ask.price
        tx_quantity = None

        if top_bid.quantity < top_ask.quantity:
            tx_quantity = top_bid.quantity
        else:
            tx_quantity = top_ask.quantity

        if top_bid.price < top_ask.price:
            pass

        elif top_bid.price == top_ask.price:
            self.create_tx(top_bid, top_ask, tx_price, tx_quantity)  # TODO

            if top_bid.quantity < top_ask.quantity:
                self.remove_from_book(top_bid)
                self.reduce_quantity(top_ask, top_bid.quantity)

            elif top_bid.quantity == top_ask.quantity:
                self.remove_from_book(top_bid)
                self.remove_from_book(top_ask)

            elif top_bid.quantity > top_ask.quantity:
                self.remove_from_book(top_ask)
                self.reduce_quantity(top_bid, top_ask.quantity)


def main():
    window = Window()

    run = True

    while run:
        window.generate_order()

        if len(window.buy_book) > 0 and len(window.sell_book) > 0:
            window.match()

        window.window.update_idletasks()
        window.window.update()


if __name__ == "__main__":
    main()
