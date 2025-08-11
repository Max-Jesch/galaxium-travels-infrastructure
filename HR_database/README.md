# Galaxium Travels HR API

A simple HR database API that stores employee information in a Markdown file. This service is designed to demonstrate basic CRUD operations and can be used as a sample service for showcasing Agentic AI concepts.

## Features

- Store employee data in a human-readable Markdown format
- RESTful API endpoints for CRUD operations
- Simple and lightweight implementation
- Easy to deploy and maintain

## Setup

1. Set up virtual environment:
```sh
python3.12 -m venv .venv
source ./.venv/bin/activate
```

2. Install the required dependencies:
```bash
pip install --upgrade pip
pip install pandas
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:8081`

## API Endpoints

- `GET /employees` - List all employees
- `GET /employees/{employee_id}` - Get a specific employee
- `POST /employees` - Create a new employee
- `PUT /employees/{employee_id}` - Update an existing employee
- `DELETE /employees/{employee_id}` - Delete an employee

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8081/docs`
- ReDoc: `http://localhost:8081/redoc`

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