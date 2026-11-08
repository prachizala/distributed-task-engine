# Contributing to Distributed Task Engine

Thank you for your interest in contributing! We welcome bug fixes, documentation improvements, architectural proposals, and performance optimizations.

## Getting Started
1. Fork the repository and clone your fork locally.
2. Create a virtual environment with Python 3.11+.
3. Install dependencies: `pip install -r requirements.txt`.
4. Install pre-commit or run `ruff check .` and `ruff format .` before pushing.

## Development Workflow
- Create a feature branch: `git checkout -b feature/my-new-feature`.
- Write unit tests under `tests/` for any new logic.
- Run the test suite: `pytest -v`.
- Open a Pull Request targeting the `main` branch.

## Code Standards
- Adhere to PEP 8 standards enforced via Ruff.
- Type hints are required for all public function signatures.
- Async database operations must use explicit transaction boundaries.
