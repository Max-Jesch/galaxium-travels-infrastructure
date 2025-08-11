# Testing Guide for Enhanced Error Handling

This guide explains how to test the improved error messages across all Galaxium Travels systems.

## Overview

The enhanced error handling has been implemented across three main systems:
1. **Booking System REST API** (`booking_system_rest/`)
2. **Booking System MCP Server** (`booking_system_mcp/`)
3. **HR Database System** (`HR_database/`)

## Testing the REST API

### Prerequisites
```bash
cd booking_system_rest
source venv/bin/activate  # or create a new virtual environment
pip install -r requirements.txt
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### What's Tested
- **Flight booking errors**: Flight not found, no seats available
- **User validation errors**: User not found, name mismatch
- **Booking management errors**: Booking not found, already cancelled
- **User registration errors**: Duplicate email
- **User retrieval errors**: User not found

### Test Coverage
The tests verify both:
- **HTTP status codes** (404, 400, etc.)
- **Error message content** (specific phrases and suggestions)

## Testing the MCP Server

### Prerequisites
```bash
cd booking_system_mcp
# Install MCP dependencies (requires fastmcp package)
pip install -r requirements.txt
```

### Testing Approach
Since the MCP server requires specific dependencies, testing focuses on:
- **Code review** of error message implementations
- **Manual verification** of error message content
- **Integration testing** when MCP environment is available

### Error Scenarios Covered
- Flight not found with tool suggestions
- User not found with registration guidance
- User name mismatch with correction hints
- Booking management errors with context

## Testing the HR Database

### Prerequisites
```bash
cd HR_database
# Install dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
# Start the server
python app.py

# In another terminal, test error scenarios
curl http://localhost:8000/employees/999  # Should return enhanced error
```

### What's Tested
- **Employee not found errors**: Clear guidance on next steps
- **Database operation errors**: File corruption, permission issues
- **CRUD operation errors**: Update/delete non-existent employees

## Manual Testing Scenarios

### 1. User Registration Flow
```bash
# Test duplicate email error
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# Should return enhanced error message suggesting /user_id endpoint
```

### 2. Flight Booking Flow
```bash
# Test with non-existent user
curl -X POST http://localhost:8000/book \
  -H "Content-Type: application/json" \
  -d '{"user_id": 999, "name": "Test User", "flight_id": 1}'

# Should return enhanced error message suggesting /register endpoint
```

### 3. Booking Cancellation Flow
```bash
# Test with non-existent booking
curl -X POST http://localhost:8000/cancel/999

# Should return enhanced error message with verification guidance
```

## Expected Error Message Patterns

### REST API Errors
- **404 Not Found**: Clear explanation + suggested endpoint
- **400 Bad Request**: Context + alternative actions
- **500 Internal Server Error**: Problem description + troubleshooting steps

### MCP Server Errors
- **Exception messages**: Tool suggestions + context
- **User guidance**: Clear next steps for AI agents

### HR Database Errors
- **Employee operations**: Verification steps + alternative endpoints
- **Database issues**: File system guidance + format requirements

## Validation Checklist

- [ ] Error messages explain what went wrong
- [ ] Next steps are clearly suggested
- [ ] Alternative approaches are provided
- [ ] Messages are consistent across systems
- [ ] Tests verify both status codes and content
- [ ] Error handling works for edge cases

## Troubleshooting

### Common Issues
1. **Virtual environment not activated**: Ensure you're in the correct venv
2. **Dependencies missing**: Run `pip install -r requirements.txt`
3. **Database not initialized**: Check if `booking.db` exists
4. **Port conflicts**: Ensure no other services are using the same ports

### Debug Mode
For detailed error information, you can:
- Check the application logs
- Use `curl -v` for verbose HTTP output
- Review the test output for specific failure details

## Continuous Integration

The error handling improvements are designed to:
- **Pass all existing tests** without breaking functionality
- **Maintain backward compatibility** for API consumers
- **Provide consistent experience** across all systems
- **Enable AI agent self-service** for common issues

## Future Testing Considerations

1. **Load testing**: Ensure error handling performs under stress
2. **Internationalization**: Test error messages in different languages
3. **Accessibility**: Verify error messages work with screen readers
4. **Monitoring**: Track which error messages are most common
5. **User feedback**: Collect feedback on error message clarity
