# Galaxium Travels Booking API

A FastAPI-based REST service for booking interplanetary flights in the Galaxium Travels system.

## Overview

This API provides endpoints for:
- User registration and management
- Flight browsing and booking
- Booking management (view, cancel)
- Flight seat availability tracking

## Issues Addressed

### User Registration and ID Matching Problems
The system had reported issues with:
1. **User Registration Failures**: Users couldn't register properly
2. **User ID Mismatches**: User IDs were not properly matched to users during booking operations

### Root Causes Identified and Fixed
1. **Double Database Commit**: Fixed duplicate `db.commit()` calls in booking operations
2. **Missing Auto-increment**: Added proper `autoincrement=True` to primary key columns
3. **Email Validation**: Enhanced Pydantic models with proper email validation
4. **Pydantic Deprecation**: Updated from deprecated `orm_mode` to `from_attributes`

## Testing Framework

A comprehensive testing framework has been implemented to prevent regression of these issues:

- **100% Code Coverage** achieved
- **34 Test Cases** covering all critical functionality
- **pytest** with FastAPI TestClient for integration testing
- **In-memory SQLite** for isolated test execution

### Quick Test Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python run_tests.py all

# Run tests without coverage (faster)
python run_tests.py fast

# Run specific test categories
python run_tests.py user      # User management tests
python run_tests.py booking   # Booking system tests
python run_tests.py flight    # Flight management tests
```

For detailed testing information, see [TESTING.md](TESTING.md).

## Error Handling

The API has been redesigned to work better with agentic systems by ensuring that only truly fatal errors return non-200 status codes. Business logic errors now return 200 status codes with detailed error information in the response body.

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": "Detailed error description"
}
```

### Error Codes
- `FLIGHT_NOT_FOUND` - Specified flight doesn't exist
- `NO_SEATS_AVAILABLE` - Flight is fully booked
- `USER_NOT_FOUND` - User is not registered
- `NAME_MISMATCH` - User ID doesn't match the provided name
- `EMAIL_EXISTS` - Email is already registered
- `BOOKING_NOT_FOUND` - Booking doesn't exist
- `ALREADY_CANCELLED` - Booking is already cancelled

### Success Response Format
Successful operations return the expected data directly (e.g., booking details, user information, flight list).

## API Endpoints

### User Management
- `POST /register` - Register a new user
- `GET /user_id` - Get user by name and email

### Flight Management
- `GET /flights` - List all available flights

### Booking Management
- `POST /book` - Book a flight
- `GET /bookings/{user_id}` - Get user's bookings
- `POST /cancel/{booking_id}` - Cancel a booking

## Installation

1. **Clone the repository**
2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
# Start the server
uvicorn app:app --reload

# Access the API documentation
open http://localhost:8000/docs
```

## Database

The application uses SQLite with SQLAlchemy ORM. The database is automatically initialized and seeded with sample data on startup.

## Development

### Code Quality
- **100% Test Coverage** maintained
- **PEP 8** compliance
- **Type Hints** throughout

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Data integrity verification
- **Edge Case Testing**: Error handling and validation

## Contributing

1. **Write Tests**: All new features must include tests
2. **Maintain Coverage**: Ensure 100% code coverage
3. **Run Tests**: Execute test suite before submitting changes
4. **Follow Patterns**: Use existing test structure and naming conventions

## Troubleshooting

### Common Issues
1. **Database Locked**: Ensure no other processes are using the database
2. **Import Errors**: Check virtual environment activation
3. **Test Failures**: Review test output and fix underlying issues

### Getting Help
- Check [TESTING.md](TESTING.md) for testing guidance
- Review FastAPI documentation for API development
- Examine existing test patterns in the codebase

---

**Note**: This API has been thoroughly tested to address the reported user registration and ID matching issues. The comprehensive test suite ensures these problems won't recur in future development. 