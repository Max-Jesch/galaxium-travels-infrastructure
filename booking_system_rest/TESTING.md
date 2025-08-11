# Testing Framework for Galaxium Travels Booking API

This document describes the comprehensive testing framework implemented for the Galaxium Travels Booking API to address reported issues with user registration and user ID matching.

## Issues Identified and Addressed

### 1. User ID Generation and Consistency
- **Problem**: Users reported that user IDs were not properly matched to users
- **Solution**: Comprehensive testing of user ID auto-increment, persistence, and consistency across operations

### 2. User Registration Issues
- **Problem**: Users reported inability to register
- **Solution**: Testing of all registration scenarios including validation, duplicate handling, and error cases

### 3. User ID and Name Matching
- **Problem**: User ID validation against names during booking
- **Solution**: Testing of the exact matching logic used in the booking system

## Testing Framework Architecture

### Technology Stack
- **pytest**: Primary testing framework
- **FastAPI TestClient**: HTTP client for testing API endpoints
- **SQLAlchemy**: Database testing utilities
- **pytest-cov**: Code coverage reporting
- **pytest-asyncio**: Async testing support

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── test_user_management.py     # User registration and retrieval tests
├── test_booking_system.py      # Flight booking and cancellation tests
└── test_flight_management.py   # Flight management and integration tests
```

## Running Tests

### Prerequisites
Install testing dependencies:
```bash
pip install -r requirements.txt
```

### Quick Test Commands

#### Using the Test Runner Script
```bash
# Run all tests with coverage
python run_tests.py all

# Run tests without coverage (faster)
python run_tests.py fast

# Run specific test categories
python run_tests.py user      # User management tests only
python run_tests.py booking   # Booking system tests only
python run_tests.py flight    # Flight management tests only

# Generate coverage report
python run_tests.py coverage

# Show help
python run_tests.py help
```

#### Using pytest Directly
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov=models --cov=db --cov-report=term-missing

# Run specific test file
pytest tests/test_user_management.py -v

# Run specific test class
pytest tests/test_user_management.py::TestUserRegistration -v

# Run specific test method
pytest tests/test_user_management.py::TestUserRegistration::test_register_user_success -v
```

## Test Categories

### 1. User Management Tests (`test_user_management.py`)

#### User Registration Tests
- ✅ Successful user registration
- ✅ Duplicate email handling
- ✅ Missing field validation
- ✅ Invalid email format validation

#### User Retrieval Tests
- ✅ Successful user retrieval by name and email
- ✅ User not found scenarios
- ✅ Missing parameter handling

#### User ID Consistency Tests
- ✅ Auto-increment functionality
- ✅ ID persistence across operations
- ✅ Sequential ID generation

### 2. Booking System Tests (`test_booking_system.py`)

#### Flight Booking Tests
- ✅ Successful flight booking
- ✅ User ID and name mismatch handling
- ✅ Non-existent user handling
- ✅ Non-existent flight handling
- ✅ No seats available scenarios

#### Booking Retrieval Tests
- ✅ User booking retrieval
- ✅ Empty booking lists
- ✅ Invalid user ID handling

#### Booking Cancellation Tests
- ✅ Successful cancellation
- ✅ Non-existent booking handling
- ✅ Already cancelled booking handling

### 3. Flight Management Tests (`test_flight_management.py`)

#### Flight Retrieval Tests
- ✅ Empty database handling
- ✅ Data retrieval with multiple flights
- ✅ Flight data integrity

#### Flight Data Integrity Tests
- ✅ ID auto-increment
- ✅ Seat availability validation
- ✅ Price validation

#### Integration Tests
- ✅ Seat decrement on booking
- ✅ Seat increment on cancellation
- ✅ Multiple bookings on same flight

## Test Database

### In-Memory SQLite
- Tests use an in-memory SQLite database for isolation
- Each test gets a fresh database instance
- No persistent data between tests

### Fixtures
- `db_session`: Fresh database session for each test
- `client`: FastAPI TestClient with database override
- `sample_user_data`: Standard user data for testing
- `sample_flight_data`: Standard flight data for testing
- `sample_booking_data`: Standard booking data for testing

## Code Coverage

### Coverage Reports
- **Terminal**: Shows missing lines in terminal output
- **HTML**: Detailed HTML report in `htmlcov/` directory
- **XML**: Machine-readable coverage data

### Coverage Targets
- **app.py**: API endpoint logic
- **models.py**: Database models
- **db.py**: Database connection and utilities

## Continuous Integration

### GitHub Actions (Recommended)
Create `.github/workflows/test.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m pytest tests/ --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Debugging Failed Tests

### Common Issues
1. **Database Connection**: Ensure SQLite is available
2. **Import Errors**: Check Python path and module structure
3. **Fixture Issues**: Verify fixture names match test parameters

### Verbose Output
```bash
# Run with maximum verbosity
pytest tests/ -vvv -s

# Run single test with output
pytest tests/test_user_management.py::TestUserRegistration::test_register_user_success -v -s
```

### Debug Mode
```bash
# Run with debugger
pytest tests/ --pdb

# Run with debugger on failures only
pytest tests/ --pdb-fail
```

## Adding New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
def test_feature_name_scenario(self, client, db_session):
    """Test description."""
    # Arrange: Set up test data
    # Act: Execute the action
    # Assert: Verify the results
```

### Best Practices
1. **Isolation**: Each test should be independent
2. **Descriptive Names**: Test names should clearly describe what's being tested
3. **Single Responsibility**: Each test should verify one specific behavior
4. **Cleanup**: Use fixtures for automatic cleanup

## Performance Considerations

### Test Execution Time
- **Unit Tests**: < 1 second each
- **Integration Tests**: 1-5 seconds each
- **Full Suite**: ~30-60 seconds

### Optimization Tips
- Use `@pytest.mark.slow` for slow tests
- Run specific test categories during development
- Use `--tb=short` for faster failure output

## Troubleshooting

### Common Error Messages
1. **"Module not found"**: Check Python path and virtual environment
2. **"Database locked"**: Ensure no other processes are using the database
3. **"Fixture not found"**: Verify fixture names and imports

### Getting Help
1. Check pytest documentation: https://docs.pytest.org/
2. Review FastAPI testing guide: https://fastapi.tiangolo.com/tutorial/testing/
3. Examine existing test patterns in the codebase

## Next Steps

### Immediate Actions
1. Run the test suite to identify current issues
2. Fix any failing tests
3. Address code coverage gaps

### Future Enhancements
1. Add performance testing
2. Implement load testing
3. Add API contract testing
4. Integrate with CI/CD pipeline
5. Add mutation testing for robustness

---

**Note**: This testing framework is designed to catch the specific issues reported by users while providing comprehensive coverage of the entire API. Regular test execution should prevent regression of these issues in future development.
