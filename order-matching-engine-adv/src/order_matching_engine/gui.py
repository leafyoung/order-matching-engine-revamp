import tkinter.ttk as ttk
from tkinter import Tk
from typing import Any

from .config import EngineConfig
from .engine import MatchingEngine


class OrderBookWindow:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.engine = MatchingEngine(config)
        self.config = config or EngineConfig()

        self.tx_count = 0
        self.cache_length = self.config.cache_length
        self.buy_cache: list[dict[str, Any] | None] = []
        self.sell_cache: list[dict[str, Any] | None] = []
        self.fill_cache: list[dict[str, Any] | None] = []

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
            columns=(
                "Date",
                "Time",
                "Price ($)",
                "Quantity",
                "Transaction ID",
                "Bid ID",
                "Ask ID",
            ),
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

    def draw_book(self, cache: list[dict[str, Any] | None]) -> None:
        if cache is self.buy_cache:
            tree = self.bid_tree
        elif cache is self.sell_cache:
            tree = self.ask_tree
        elif cache is self.fill_cache:
            tree = self.fill_tree
        else:
            return

        if tree is self.bid_tree or tree is self.ask_tree:
            tree.delete(*tree.get_children())

            if len(cache) == 0:
                return

            for i, record in enumerate(cache):
                if record is None:
                    continue

                tree.insert(
                    parent="",
                    index=i,
                    iid=i,
                    text="",
                    values=(record.get("price"), record.get("quantity")),
                )
        else:
            tree.delete(*tree.get_children())

            for i, record in enumerate(cache):
                if record is None:
                    continue
                tree.insert(
                    parent="",
                    index=i,
                    iid=i,
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

    def update_cache(self, book: list) -> None:

        if book is self.engine.fill_book:
            cache = self.fill_cache
        elif book is self.engine.buy_book:
            cache = self.buy_cache
        elif book is self.engine.sell_book:
            cache = self.sell_cache
        else:
            return

        cache.clear()

        if cache is self.fill_cache:
            if len(self.engine.fill_book) < self.cache_length:
                cache.extend(self.engine.fill_book)
            else:
                cache.extend(self.engine.fill_book[: self.cache_length])
        elif cache is self.buy_cache or cache is self.sell_cache:
            empty_list = [None] * 10
            cache.extend(empty_list)

            if len(book) == 0:
                self.draw_book(cache)
                return

            index = 0
            if book:
                current_price = book[0].price
            else:
                current_price = self.config.eq_price
            quantity = 0

            while index < 10:
                for order in book:
                    if order.price == current_price:
                        quantity = quantity + order.quantity

                cache_order = {"quantity": quantity, "price": current_price}
                cache[index] = cache_order

                for order in book:
                    if book is self.engine.sell_book:
                        if order.price and order.price > current_price:
                            current_price = order.price
                            break
                    elif book is self.engine.buy_book:
                        if order.price and order.price < current_price:
                            current_price = order.price
                            break
                else:
                    break  # no further price level

                quantity = 0
                index = index + 1

        self.draw_book(cache)

    def run(self) -> None:
        self.window.after(100, self._update_loop)
        self.window.mainloop()

    def _update_loop(self) -> None:
        self.engine.generate_order()  # add_to_book() matches the new order immediately

        self.update_cache(self.engine.buy_book)
        self.update_cache(self.engine.sell_book)
        self.update_cache(self.engine.fill_book)

        self.window.after(100, self._update_loop)


def main() -> None:
    window = OrderBookWindow()
    window.run()
