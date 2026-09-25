"""Headless checks of the matching rules: price priority, time priority, partial fill, market order.

Run with:  uv run pytest
Tk is replaced by a mock, so no window (and no display) is needed.
"""

from unittest import mock

import pytest

import ome_serial
from ome_serial import Order


@pytest.fixture
def window():
    with mock.patch.object(ome_serial, "Tk"), mock.patch.object(ome_serial, "ttk"):
        yield ome_serial.Window()


def submit(window, order_id, side, quantity, price=None):
    """Submit a limit order (price given) or a market order (price None)."""
    market = price is None
    order = Order("t", order_id, quantity, market, not market, price, side == "bid", side == "ask")
    window.add_to_book(order)


def fills(window):
    """(price, quantity) of every fill, oldest first."""
    return [(tx["Price ($)"], tx["Quantity"]) for tx in reversed(window.fill_book)]


def test_price_priority(window):
    for order_id, price in enumerate((90.0, 80.0, 70.0, 75.0)):
        submit(window, order_id, "bid", 1, price)
    assert [o.price for o in window.buy_book] == [90.0, 80.0, 75.0, 70.0]

    for order_id, price in enumerate((105.0, 101.0, 103.0), start=10):
        submit(window, order_id, "ask", 1, price)
    assert [o.price for o in window.sell_book] == [101.0, 103.0, 105.0]


def test_crossed_limit_order_trades_at_resting_price(window):
    submit(window, 1, "ask", 10, 100.0)
    submit(window, 2, "bid", 10, 105.0)
    assert fills(window) == [(100.0, 10)]
    assert window.buy_book == [] and window.sell_book == []


def test_time_priority(window):
    submit(window, 1, "ask", 5, 100.0)
    submit(window, 2, "ask", 5, 100.0)
    submit(window, 3, "bid", 5, 100.0)
    assert window.fill_book[0]["Ask ID"] == 1  # oldest ask trades first
    assert [o.order_id for o in window.sell_book] == [2]

    submit(window, 4, "bid", 5, 90.0)
    submit(window, 5, "bid", 5, 90.0)
    submit(window, 6, "ask", 5, 90.0)
    assert window.fill_book[0]["Bid ID"] == 4


def test_partial_fill(window):
    submit(window, 1, "ask", 50, 100.0)
    submit(window, 2, "bid", 20, 105.0)
    assert fills(window) == [(100.0, 20)]
    assert [(o.order_id, o.quantity) for o in window.sell_book] == [(1, 30)]  # keeps its place

    submit(window, 3, "ask", 30, 101.0)
    submit(window, 4, "bid", 70, 101.0)  # walks two levels, rests the remaining 10
    assert fills(window)[1:] == [(100.0, 30), (101.0, 30)]
    assert window.sell_book == []
    assert [(o.order_id, o.price, o.quantity) for o in window.buy_book] == [(4, 101.0, 10)]


def test_market_order(window):
    submit(window, 1, "bid", 10, 99.0)
    submit(window, 2, "bid", 10, 98.0)
    submit(window, 3, "ask", 25)
    assert fills(window) == [(99.0, 10), (98.0, 10)]
    assert window.buy_book == [] and window.sell_book == []  # 5 unfilled units cancelled, not rested

    submit(window, 4, "bid", 5)  # empty opposite side: nothing happens
    assert window.fill_book[0]["Ask ID"] == 3 and window.buy_book == []


def test_market_order_is_filled_at_most_once(window):
    # regression: a market order was inserted AND appended, then filled twice
    submit(window, 1, "bid", 1, 100.0)
    submit(window, 2, "bid", 5)
    submit(window, 3, "ask", 20, 100.0)
    assert sum(tx["Quantity"] for tx in window.fill_book if tx["Bid ID"] == 2) == 0
    assert [o.order_id for o in window.buy_book] == []
    assert [(o.order_id, o.quantity) for o in window.sell_book] == [(3, 19)]


def test_random_orders_keep_book_sorted_and_uncrossed(window):
    ome_serial.random.seed(0)
    for _ in range(2000):
        window.generate_order()
        bid_prices = [o.price for o in window.buy_book]
        ask_prices = [o.price for o in window.sell_book]
        assert bid_prices == sorted(bid_prices, reverse=True)
        assert ask_prices == sorted(ask_prices)
        assert None not in bid_prices + ask_prices  # no market order rests
        if bid_prices and ask_prices:
            assert bid_prices[0] < ask_prices[0]
    assert len(window.fill_book) > 0
