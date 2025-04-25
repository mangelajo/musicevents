# Music Events

A Django application for managing and displaying music events.

## Installation

### Basic Installation

```bash
# Install with uv
uv pip install -e .
```

### Development Installation

For development, including running functional tests with Playwright:

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install
```

## Running Tests

```bash
# Run all tests
pytest

# Run only functional tests
pytest events/tests/functional/
```
