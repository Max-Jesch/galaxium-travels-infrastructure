# Error Message Improvement Examples

This document shows concrete examples of the error message improvements made across the Galaxium Travels infrastructure project.

## Before vs After Examples

### 1. Flight Not Found

**Before:**
```
HTTP 404: "Flight not found"
```

**After:**
```
HTTP 404: "Flight not found. The specified flight_id does not exist in our system. Please check the flight_id or use the /flights endpoint to see available flights."
```

**AI Agent Action**: The agent can now immediately understand that it should check the `/flights` endpoint to see what flights are available.

### 2. User Not Found

**Before:**
```
HTTP 404: "User not found or name does not match user ID"
```

**After (User doesn't exist):**
```
HTTP 404: "User with ID 999 is not registered in our system. The user might need to register first using the /register endpoint, or you may need to check if the user_id is correct."
```

**After (User exists but name doesn't match):**
```
HTTP 404: "User ID 123 exists but the name 'John Doe' does not match the registered name 'John Smith'. Please verify the user's name or use the correct name for this user ID."
```

**AI Agent Action**: The agent can now distinguish between two different scenarios and take appropriate action:
- If user doesn't exist: Register the user first
- If user exists but name is wrong: Use the correct name

### 3. No Seats Available

**Before:**
```
HTTP 400: "No seats available"
```

**After:**
```
HTTP 400: "No seats available on this flight. The flight is fully booked. Please check other flights or try again later if seats become available."
```

**AI Agent Action**: The agent knows to either check other flights or suggest waiting for seats to become available.

### 4. Booking Not Found

**Before:**
```
HTTP 404: "Booking not found"
```

**After:**
```
HTTP 404: "Booking with ID 456 not found. The booking may have been deleted or the booking_id may be incorrect. Please verify the booking_id or check if the booking exists."
```

**AI Agent Action**: The agent can verify the booking ID or check if the booking still exists in the system.

### 5. Email Already Registered

**Before:**
```
HTTP 400: "Email already registered"
```

**After:**
```
HTTP 400: "Email 'john@example.com' is already registered. A user with this email already exists in our system. If you're trying to access an existing account, use the /user_id endpoint with the correct name and email to get the user_id."
```

**AI Agent Action**: The agent knows to use the `/user_id` endpoint to retrieve the existing user's information instead of trying to register again.

### 6. User Retrieval Not Found

**Before:**
```
HTTP 404: "User not found"
```

**After:**
```
HTTP 404: "User not found with name 'John Doe' and email 'john@example.com'. The user may not be registered in our system. Please check the spelling of both name and email, or register the user first using the /register endpoint."
```

**AI Agent Action**: The agent can check spelling or register the user if they don't exist.

## MCP Server Examples

### 1. Flight Not Found (MCP Context)

**Before:**
```
Exception: "Flight not found"
```

**After:**
```
Exception: "Flight not found. The specified flight_id 999 does not exist in our system. Please check the flight_id or use the list_flights tool to see available flights."
```

**AI Agent Action**: The agent knows to use the `list_flights` tool to see what flights are available.

### 2. User Not Found (MCP Context)

**Before:**
```
Exception: "User not found or name does not match user ID"
```

**After:**
```
Exception: "User with ID 999 is not registered in our system. The user might need to register first using the register_user tool, or you may need to check if the user_id is correct."
```

**AI Agent Action**: The agent knows to use the `register_user` tool to create the user first.

## HR Database Examples

### 1. Employee Not Found

**Before:**
```
HTTP 404: "Employee not found"
```

**After:**
```
HTTP 404: "Employee with ID 123 not found. The employee may have been deleted or the employee_id may be incorrect. Please verify the employee_id or use the /employees endpoint to see all available employees."
```

**AI Agent Action**: The agent can use the `/employees` endpoint to see what employees are available.

### 2. Database Read Error

**Before:**
```
HTTP 500: "Error reading database: [Errno 2] No such file or directory: 'data/employees.md'"
```

**After:**
```
HTTP 500: "Error reading employee database: [Errno 2] No such file or directory: 'data/employees.md'. The database file may be corrupted or missing. Please check if the data/employees.md file exists and has the correct format."
```

**AI Agent Action**: The agent knows to check if the database file exists and verify its format.

## Key Improvements Summary

1. **Context**: Each error now explains what went wrong in detail
2. **Actionability**: Clear next steps are provided
3. **Alternatives**: Other endpoints or tools are suggested
4. **Specificity**: Error messages include relevant IDs and values
5. **Consistency**: Similar errors across different systems now have similar formats
6. **AI-Friendly**: Messages are structured to help AI agents make decisions

## Benefits for AI Agents

- **Faster Resolution**: Agents can immediately understand what to do next
- **Reduced Confusion**: Clear distinction between different error scenarios
- **Self-Service**: Many issues can be resolved without human intervention
- **Better UX**: Users get helpful guidance instead of cryptic error messages
- **Consistent Experience**: Similar errors are handled consistently across systems

## Testing

All error message improvements have been tested and verified:
- REST API tests pass with updated assertions
- Error message content is validated
- Both positive and negative test cases are covered
- MCP server error handling is implemented (though not fully testable in this environment)
- HR database error handling is improved and tested
