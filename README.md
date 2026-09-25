# Order Matching Engine Revamp

This repository has the original code from the [order-matching-engine](https://github.com/tigeryant/order-matching-engine) project and a working copy for you to modernize.

## Purpose

This exercise teaches you how to modernize a Python project. You will learn to:

- Set up a Python project using `uv` for fast, reliable dependency management
- Refactor code to remove global variables and improve code organization
- Follow modern Python project structure best practices

These skills are essential for writing maintainable, professional Python code that can grow with your project.

## Project Structure

- **`order-matching-engine/`** - Original code from the upstream repository (left unchanged, for reference)
- **`order-matching-engine-work/`** - Your working copy of the original code. Do the exercise here.

## Requirements

- [`uv`](https://docs.astral.sh/uv/)
- Python 3.13 or later **with Tk support** (the GUI uses `tkinter`)
- No third-party packages. The program only uses the standard library (`tkinter`, `random`, `datetime`), so `dependencies = []` in `pyproject.toml` is correct. The only optional extra is `pytest`, as a dev dependency, if you write tests (`uv add --dev pytest`).

Some Python builds (for example Homebrew or some Linux distributions) ship without Tk. If you see `ModuleNotFoundError: No module named '_tkinter'`, pin a version and use a uv-managed Python, which includes Tk:

```bash
uv python pin 3.13                          # writes .python-version
uv run --managed-python ome_serial.py
```

## Task

Follow these steps to complete the exercise:

1. **Explore** `order-matching-engine-work/` to understand its structure
2. **Set up** the project with `uv init` (creates `pyproject.toml`) and pin Python 3.13 (`uv python pin 3.13`)
3. **Refactor** the code to remove global variables and improve structure
4. **Run** the program with `uv run ...` and check it against the done criteria below

### Done criteria

Your submission is done when all of the following hold:

1. `uv run ome_serial.py` (or the entry point you define in `pyproject.toml`) opens the GUI, the three tables (Bids, Offers, Filled orders) keep updating, and closing the window returns you to the prompt **without a traceback**.
2. No module-level mutable state remains: the books, caches and counters live on an object.
3. You have checked your engine against these four scenarios and report the result of each. A small headless test (no window) is the easiest way to do this. Prices are per unit.

| # | Scenario | Orders, in time order | Expected result |
|---|---|---|---|
| 1 | Price priority | Limit bids 1@90, 1@80, 1@70, 1@75 | Bid book is 90, 80, 75, 70 (best first) |
| 2 | Time priority | Limit asks A: 5@100, B: 5@100; then limit bid 5@100 | Bid trades with A (the older ask); B stays in the book |
| 3 | Partial fill | Limit ask 50@100; then limit bid 20@105 | One fill of 20 at 100 (the resting order's price); the ask stays at the front of the book with 30 left |
| 4 | Market order | Limit bids 10@99, 10@98; then market sell 25 | Fills 10@99 and 10@98; the remaining 5 are cancelled, and nothing rests in the book |

### Known issues in the original

The original code (and so your working copy) gets several of these rules wrong. You may fix them. Either way, describe what you found. If you fix a bug, say how you checked the fix (for example, which scenario now passes).

- `match()` only trades when the best bid **equals** the best ask. When the prices cross (bid above ask), no trade happens.
- `insert_order()` inserts one position too early, so the book is not sorted. For example, bids at 210, 200, 190, 195 end up as 210, 195, 200, 190.
- For asks, `better_than()` treats an equal price as better, so a new ask jumps ahead of older asks at the same price (time priority is lost).
- Market orders do not execute or cancel. They copy a price from the book (or `eq_price` when the book is empty) and then rest in the book like limit orders. The `price = None` set for market orders in `generate_order()` is overwritten straight away.
- `match()` runs once per generated order, so at most one trade happens per tick even when more orders cross.
- `update_cache()` and `draw_book()` pick the book or table with `==`, which compares list *contents*. Two empty lists compare equal, so the wrong table can be picked. When a side has fewer than 10 price levels, the last level is repeated in the table.
- The `while True: ... update()` main loop raises `TclError` when you close the window. Use `window.after(...)` with `window.mainloop()` instead.

### Submission

For your assignment submission:

- Include a screenshot of the running program
- Include a screenshot of your terminal showing the launching command line
- Include your `pyproject.toml`
- Report the result of each of the four scenarios above
- Briefly describe the changes you made to improve the code organization, and which known issues (if any) you fixed

Note: Share your learning experience and improvements, but do not share the actual code implementation.
