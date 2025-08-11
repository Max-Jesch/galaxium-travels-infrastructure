# Galaxium Travels HR API

A simple HR database API that stores employee information in a Markdown file. This service is designed to demonstrate basic CRUD operations and can be used as a sample service for showcasing Agentic AI concepts.

## Features

- Store employee data in a human-readable Markdown format
- RESTful API endpoints for CRUD operations
- Simple and lightweight implementation
- Easy to deploy and maintain

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /employees` - List all employees
- `GET /employees/{employee_id}` - Get a specific employee
- `POST /employees` - Create a new employee
- `PUT /employees/{employee_id}` - Update an existing employee
- `DELETE /employees/{employee_id}` - Delete an employee

## Error Handling

This HR API features **enhanced error messages** designed specifically for AI agents and better user experience:

### Key Improvements
- **Clear Problem Identification**: Error messages explain exactly what went wrong
- **Actionable Next Steps**: Specific suggestions for resolution are provided
- **Alternative Approaches**: Other endpoints are suggested when applicable
- **AI-Friendly Format**: Messages are structured to help AI agents make decisions

### Example Error Messages
```json
// Before: Generic error
{
  "detail": "Employee not found"
}

// After: Actionable error
{
  "detail": "Employee with ID 123 not found. The employee may have been deleted or the employee_id may be incorrect. Please verify the employee_id or use the /employees endpoint to see all available employees."
}
```

### Error Scenarios Covered
- **Employee not found**: Suggests using `/employees` endpoint to see available data
- **Database read errors**: Explains file corruption or permission issues
- **Database write errors**: Provides troubleshooting steps for file system issues
- **CRUD operation errors**: Clear guidance for update/delete operations

### Database Error Handling
The system provides detailed error messages for:
- **File corruption**: Guidance on checking file format and existence
- **Permission issues**: Suggestions for file system access problems
- **Data validation**: Clear explanation of required fields and formats

For comprehensive error handling documentation, see the [Error Handling Guide](../../docs/error-handling-guide.md) and [Error Handling Examples](../../docs/error-handling-examples.md).

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Data Structure

The employee data is stored in `data/employees.md` with the following fields:
- ID
- First Name
- Last Name
- Department
- Position
- Hire Date
- Salary

## Deployment to Fly.io

1. Install the Fly.io CLI:
```bash
# For Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

2. Login to Fly.io:
```bash
fly auth login
```

3. Launch the application:
```bash
fly launch
```

4. Deploy the application:
```bash
fly deploy
```

The application will be available at `https://galaxium-hr-api.fly.dev`

### Configuration

The application is configured to:
- Run in the Frankfurt region (fra)
- Use a shared CPU with 256MB of memory
- Auto-stop when not in use to save costs
- Force HTTPS for all connections

### Important Notes

- The data is stored in a Markdown file, which means it will be reset when the application is redeployed
- For production use, consider using a persistent storage solution like Fly Volumes
- The application is configured to scale to zero when not in use to minimize costs 