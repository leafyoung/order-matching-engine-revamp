# Order Matching Engine

## Introduction

This program simulates how electronic exchanges match buy and sell orders for financial instruments. This software is called an **order matching engine**.

### Key Concepts

**Orders:** Buyers place **bids** (offers to buy) and sellers place **asks** (offers to sell). Each order specifies:

- Quantity: how much of the asset to trade
- Price: the price per unit
- Type: market order (execute immediately) or limit order (execute only at a specified price or better)

**Order Book:** All unmatched orders are stored in the **order book**. The book has two sides:

- Buy side: contains all bid orders
- Sell side: contains all ask orders

**Matching:** The engine matches compatible buy and sell orders. When orders are matched, they are **filled** (executed). The engine continues matching until no more compatible orders remain in the book.

## Algorithm

This program uses **price/time priority** (also called **FIFO** - First In, First Out) matching.

### How It Works

Orders are matched based on two rules:

1. **Price priority:** Orders with better prices are matched first
   - For buyers: higher bid prices are better
   - For sellers: lower ask prices are better
2. **Time priority:** At the same price, earlier orders are matched first

### Why This Algorithm?

**Advantage:** Encourages traders to narrow the **spread** (the difference between the best bid and best ask), making markets more efficient.

**Trade-off:** More computationally intensive than alternatives like pro-rata matching, but simpler to understand and implement.

## Control Flow

### Overview

The control flow of the program is detailed by the flowchart shown below. At runtime, `main()` initialises many of the data structures used by the rest of the application. An order is generated and passed to one side of the order book. If the order book is not empty, `match()` is called. It selects the best quote on either side of the book and consummates a trade if each order satisfies a certain price.

![Program control flow](https://i.imgur.com/rELEZrD.png)

### Order Generation and Sampling

To create test data for the `match()` function and simulate market activity, the program generates orders based on certain parameters. These parameters determine the order's characteristics:

- **Quantity:** How many units to trade
- **Type:** Market or limit order

The price is determined by sampling from a normal distribution using Python's `random.normalvariate()` method.

### Update Book

Once an order is generated, the program adds it to the appropriate side of the book. The order's side depends on whether it is a buy or sell order, and its position in the book is determined by its price and order type.

### Match

The `match()` function evaluates the best quotes from both sides of the book to determine if they satisfy each other's price constraints. If a trade can be executed, a **transaction** is created and the appropriate quantity is removed from the book. The transaction is recorded in the fill book, which keeps track of all filled orders.

### Update Cache

Each list used by the program (`buy_book`, `sell_book`, and `fill_book`) has an associated **cache**:

- **Buy and sell caches:** Aggregate all orders at the same price into a single record
- **Fill cache:** Shows the most recently filled orders

These caches are passed to the `draw_book` method for display.

### Update GUI

The cache contents are displayed using a `Treeview` widget from the `Tkinter` GUI module, which shows tabular data. The interface contains three tables displaying bids, offers, and filled orders.

![GUI output showing order books](https://i.imgur.com/N3SEd82.png)

## Challenges

### Concurrency and Multiprocessing

The original architecture used multiprocessing pools for concurrency. Due to various bugs in that approach, the program now uses a simpler single-threaded model. The flowchart below illustrates the control flow of the original multiprocessing design.

![Original multiprocessing architecture flow](https://i.imgur.com/8LWFVen.png)

## Future Improvements

This section outlines potential enhancements for future versions.

### Depth Chart

A **depth chart** visualizes the quantity of buy and sell orders at different price levels. According to trading terminology:

> Depth refers to the market's ability to sustain large orders without significantly moving the asset's price.

A depth chart could be derived from the order book and displayed in the GUI.

### Order Generation Visualization

Another useful feature would be a chart showing how order prices are determined. This would display a normal distribution curve with markers indicating where each order's price was sampled from the distribution.

### Price Action Simulation

A more advanced order generation process could better simulate real-world price movements:

- Periodically shifting the mean of the distribution
- Creating imbalance between buy and sell order volumes to simulate market "pressure"

These changes would demonstrate bullish or bearish price action, though this is secondary to the program's main purpose of matching orders.

### Order Book Data Structure

After completing this project, it became clear that the current approach to storing and managing orders in the book is inefficient. A better solution would use:

- **Min heap** for sell orders (to quickly find the lowest ask)
- **Max heap** for buy orders (to quickly find the highest bid)

These data structures are much better suited for this problem and would significantly improve performance.
