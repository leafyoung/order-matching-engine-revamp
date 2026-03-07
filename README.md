# Order Matching Engine Revamp

This repository has the original code from [order-matching-engine](https://github.com/tigeryant/order-matching-engine) project and a revamped version.

## Purpose

This exercise teaches you how to modernize a Python project. You will learn to:

- Set up a Python project using `uv` for fast, reliable dependency management
- Refactor code to remove global variables and improve code organization
- Follow modern Python project structure best practices

These skills are essential for writing maintainable, professional Python code that can grow with your project.

## Project Structure

- **`order-matching-engine/`** - Original code from the upstream repository
- **`order-matching-engine-new/`** - Reference version for the revamped version of following updates:
  - `uv`-based project setup (pyproject.toml, uv.lock)
  - Removal of global variables
  - Improved code structure and maintainability
- **`order-matching-engine-adv/`** - Advanced reference with a fully modular package layout:
  - Code split into dedicated modules: `models.py`, `engine.py`, `gui.py`, `config.py`
  - `uv`-based project setup (pyproject.toml, uv.lock)
  - Serves as an example of a more production-oriented code organization

## Changes

The revamped version includes:

- Migration to `uv` for Python package management
- Refactored code to eliminate global state
- Modern Python project configuration with pyproject.toml

## Task

Follow these steps to complete the exercise:

1. **Explore** `order-matching-engine-work/` (a copy of the original code) to understand its structure
2. **Set up** the project using `uv` for dependency management
3. **Add packages** using `uv add <package-name>` as needed
4. **Refactor** the code to remove global variables and improve structure
5. **Run** the program with `uv run ...` and verify it works correctly

For your assignment submission:

- Include a screenshot of the running program
- Include a screenshot of your terminal showing the launching command line
- Include your pyproject.toml
- Briefly describe the changes you made to improve the code organization

Note: Share your learning experience and improvements, but do not share the actual code implementation.
