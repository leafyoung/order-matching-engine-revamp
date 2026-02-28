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
        if self.bid:
            return self.price > other.price if self.price and other.price else False

        if self.ask:
            return (
                not (self.price > other.price) if self.price and other.price else True
            )

        return False

    def __repr__(self) -> str:
        return f"Bid: {self.bid} Ask: {self.ask}"
