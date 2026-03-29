# Testing

Testing workflow and conventions for this project.

## Framework

- **pytest** for test discovery and execution
- **pytest-mock** for mocking with `mocker.patch()` fixture
- **pytest-cov** for coverage reports

## Running Tests

```bash
poetry run pytest tests/ -v                    # Run all tests
poetry run pytest tests/ -v --cov=. --cov-report=term-missing  # With coverage
poetry run pytest tests/path/to/test.py -v     # Run specific file
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
└── unit/
    ├── test_property.py      # PropertyRecord, generate_property_hash
    ├── test_rate_limiter.py  # RateLimiter.wait(), jitter
    └── test_retry_handler.py # RetryHandler.backoff_delay(), is_retryable()
```

## Conventions

1. **Test naming**: `test_<what_is_being_tested>.py`
2. **Test class naming**: `Test<ClassName>` or `Test<ModuleName>`
3. **Fixture naming**: `sample_<descriptor>` for minimal fixtures
4. **Use class-based organization**: Group related tests in classes

## Fixtures (conftest.py)

```python
@pytest.fixture
def sample_property_record() -> PropertyRecord:
    """Minimal property record with required fields only."""
    ...

def make_property(**overrides) -> PropertyRecord:
    """Factory function to create PropertyRecord with overrides."""
    ...
```

## Mocking Patterns

```python
def test_something(self, mocker):
    # Mock time-based functions
    mocker.patch("time.sleep")
    mocker.patch("time.time", return_value=100.0)
    
    # Mock random for deterministic tests
    mocker.patch("random.uniform", return_value=0.5)
    
    # Use spy for verification without behavior change
    spy = mocker.spy(obj, "method")
```

## Adding Tests

1. Add test file to `tests/unit/` for unit tests
2. Use `@pytest.fixture` in `conftest.py` for shared test data
3. Use `@pytest.mark.parametrize` for multiple input combinations
4. Mock external dependencies (time, random, requests)
5. Always run `poetry run ruff check .` before committing
