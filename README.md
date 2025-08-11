# Galaxium Travels Infrastructure

This repository contains infrastructure and demo applications for the imaginary space travel company, **Galaxium Travels**. It is designed to showcase agentic and generative AI capabilities in a modular, easy-to-deploy way.

The main repo is this https://github.com/Max-Jesch/galaxium-travels

#TODO:
- deploy this on code engine. Create the easiest possible startup script! 

## Recent Improvements 🆕

### Enhanced Error Messages for AI Agents
We've significantly improved error messages across all systems to make them more actionable for AI agents:

- **Clear Problem Identification**: Error messages now explain exactly what went wrong
- **Actionable Next Steps**: Specific suggestions for resolution are provided
- **Alternative Approaches**: Other endpoints or tools are suggested when applicable
- **AI-Friendly Format**: Messages are structured to help AI agents make decisions

**Examples:**
- **Before**: `"User not found"`
- **After**: `"User with ID 999 is not registered. Please register first using /register endpoint"`

See the [Error Handling Guide](docs/error-handling-guide.md) for detailed examples and the [Error Handling Examples](docs/error-handling-examples.md) for before/after comparisons.

## Repository Structure

```
galaxium-travels-infrastructure/
  booking_system_rest/     # FastAPI + SQLite REST API booking system
  booking_system_mcp/      # MCP (Model Context Protocol) server version
  HR_database/             # HR database app with markdown backend
  docs/                    # Documentation and guides
  README.md                # This file
```

## Applications

### 1. Booking System (REST API)
- **Path:** `booking_system_rest/`
- **Description:** A mock space travel booking system built with FastAPI and SQLite. Demonstrates core booking flows and is ready for agentic integration.
- **Features:**
  - List available flights
  - Book a flight
  - View user bookings
  - Cancel a booking
  - Auto-seeded demo data on startup
- **See:** [`booking_system_rest/README.md`](booking_system_rest/README.md) for setup, usage, and deployment instructions.

### 2. Booking System (MCP Server)
- **Path:** `booking_system_mcp/`
- **Description:** Model Context Protocol (MCP) server version of the booking system, designed for direct AI agent integration.
- **Features:**
  - Same functionality as REST API but via MCP tools
  - Optimized for AI agent workflows
  - Enhanced error messages for better agent understanding

### 3. HR Database
- **Path:** `HR_database/`
- **Description:** HR database application with markdown backend for employee management.
- **Features:**
  - Employee CRUD operations
  - Markdown-based data storage
  - Enhanced error handling for AI agents

## Documentation

- **[Error Handling Guide](docs/error-handling-guide.md)**: Comprehensive overview of error message improvements
- **[Error Handling Examples](docs/error-handling-examples.md)**: Before/after examples with AI agent actions
- **[Testing Guide](docs/testing-guide.md)**: How to test the improved error handling

## Prerequisites
- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/) for cloud deployment

## Local Development
Each app is self-contained. To run an app locally:
1. `cd` into the app directory (e.g., `cd booking_system_rest`)
2. Follow the instructions in that app's `README.md`

## Deployment
- Each app can be deployed independently to Fly.io or another platform.
- See the per-app `README.md` for deployment steps and configuration.

## Contributing
Feel free to fork, open issues, or submit pull requests for improvements or new demo apps!

---

**This repository is for demonstration and prototyping purposes only.** 