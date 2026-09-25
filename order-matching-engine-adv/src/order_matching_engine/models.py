from dataclasses import dataclass


@dataclass
class Order:
    timestamp: str
    order_id: int
    quantity: int
    market: bool
    limit: bool
    price: float | None
    bid: bool
    ask: bool

    id_counter: int = 1

    def better_than(self, other: "Order") -> bool:
        """Strictly better price. An equal price is not better, so the newer order queues behind."""
        if self.bid:
            return self.price > other.price
        return self.price < other.price

    def __repr__(self) -> str:
        return f"Bid: {self.bid} Ask: {self.ask}"
