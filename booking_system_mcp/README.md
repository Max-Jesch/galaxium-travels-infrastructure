# MCP Deployment (Model Context Protocol)

This service can be deployed as an MCP server, making its booking tools available to LLMs and agentic frameworks via the Model Context Protocol.

## Running Locally

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Seed the database (optional):
   ```sh
   python seed.py
   ```
3. Start the MCP server:
   ```sh
   python mcp_server.py
   ```
   The server will listen on port 8084 by default.
4. interact with it locally
   ```sh
   export DANGEROUSLY_OMIT_AUTH=true   
   npx @modelcontextprotocol/inspector  
   ```

5. Use `MCP inspector`:

* Connect

![](../images/connect-to-mcp-locally-01.jpg)

* List tools

![](../images/connect-to-mcp-locally-02.jpg)

## Deploying to IBM Code Engine

- Build and push your Docker image (see Dockerfile).
- Deploy to Code Engine, exposing port 8484.
- The MCP server will be available at `https://<your-app-url>:8484/mcp`.

---

# Booking System Demo (FastAPI + SQLite)

This is a simple booking system for a space travel company, built with FastAPI and SQLite. It is designed for easy deployment on Fly.io.

## Features
- List available flights
- Book a flight
- View user bookings
- Cancel a booking

## Requirements
- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/)

## Setup (Local)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   uvicorn app:app --reload
   ```
3. The API will be available at `http://127.0.0.1:8484`.
4. Use the interactive docs at `http://127.0.0.1:8484/docs`.

## Database
- The SQLite database file (`booking.db`) will be created automatically on first run.
- To add initial data, you can use a SQLite client or add endpoints/scripts as needed.

## Deploying to Fly.io

1. Install the [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Run:
   ```bash
   fly launch
   fly volumes create bookings_data --size 1
   fly deploy
   ```
3. The app will be deployed and accessible via your Fly.io app URL.

## Endpoints
- `GET /flights` — List all flights
- `POST /book` — Book a flight (requires `user_id` and `flight_id`)
- `GET /bookings/{user_id}` — List bookings for a user
- `POST /cancel/{booking_id}` — Cancel a booking

## Error Handling

This MCP server features **enhanced error messages** specifically designed for AI agents using the Model Context Protocol:

### Key Improvements
- **Clear Problem Identification**: Error messages explain exactly what went wrong
- **Tool Suggestions**: Specific MCP tools are suggested for resolution
- **Context Information**: Relevant details about the failure are provided
- **AI-Friendly Format**: Messages are structured to help AI agents make decisions

### Example Error Messages
```python
# Before: Generic error
Exception: "User not found"

# After: Actionable error with tool suggestions
Exception: "User with ID 999 is not registered in our system. The user might need to register first using the register_user tool, or you may need to check if the user_id is correct."
```

### Error Scenarios Covered
- **Flight not found**: Suggests using `list_flights` tool
- **User not found**: Distinguishes between unregistered users and name mismatches
- **No seats available**: Suggests checking other flights
- **Booking errors**: Provides context and verification steps
- **Duplicate registration**: Suggests using `get_user_id` tool

### MCP Tool Integration
All error messages are designed to work seamlessly with MCP tools:
- **Flight operations**: `list_flights`, `book_flight`
- **User management**: `register_user`, `get_user_id`
- **Booking management**: `get_bookings`, `cancel_booking`

For comprehensive error handling documentation, see the [Error Handling Guide](../../docs/error-handling-guide.md) and [Error Handling Examples](../../docs/error-handling-examples.md).

---

This is a demo system and not intended for production use. 