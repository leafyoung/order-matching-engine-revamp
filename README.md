# Order Matching Engine Revamp

This repository has the original code from [order-matching-engine](https://github.com/tigeryant/order-matching-engine) project and a revamped version.

## Purpose

This exercise demonstrates modernizing a Python project using `uv` for project setup and dependency management, along with refactoring the codebase to eliminate global variables and improve code organization.

## Project Structure

- **`order-matching-engine/`** - Original code from the upstream repository
- **`order-matching-engine-new/`** - Reference version for the revamped version of following updates:
    - `uv`-based project setup (pyproject.toml, uv.lock)
    - Removal of global variables
    - Improved code structure and maintainability

## Changes

The revamped version includes:

- Migration to `uv` for Python package management
- Refactored code to eliminate global state
- Modern Python project configuration with pyproject.toml

## Task

1. Work on `order-matching-engine-work` which is a copy of the original code.
2. Set up the project using `uv` for dependency management.
3. Add packages to the project using `uv add <package-name>`.
4. Refactor the code to remove global variables and improve structure.
5. Use `uv run ...` to start the program and incude the screenshot of the program and the terminal window in the submission of your assignment. Do not share the code.
