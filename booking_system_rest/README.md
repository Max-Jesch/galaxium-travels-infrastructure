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

1. Set up virtual environment:
   ```sh
   python3.12 -m venv .venv
   source ./.venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. The API will be available at `http://127.0.0.1:8082`.
5. Use the interactive docs at `http://127.0.0.1:8082/docs`.

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

---

This is a demo system and not intended for production use. 