import pytest
from fastapi import status
from models import Flight

class TestFlightRetrieval:
    """Test flight retrieval functionality."""
    
    def test_get_flights_empty_database(self, client, db_session):
        """Test getting flights when database is empty."""
        response = client.get("/flights")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0
    
    def test_get_flights_with_data(self, client, db_session):
        """Test getting flights when database has data."""
        # Create some test flights
        flights_data = [
            {
                "origin": "Earth",
                "destination": "Mars",
                "departure_time": "2099-01-01T09:00:00Z",
                "arrival_time": "2099-01-01T17:00:00Z",
                "price": 1000000,
                "seats_available": 5
            },
            {
                "origin": "Earth",
                "destination": "Moon",
                "departure_time": "2099-01-02T10:00:00Z",
                "arrival_time": "2099-01-02T14:00:00Z",
                "price": 500000,
                "seats_available": 3
            }
        ]
        
        for flight_data in flights_data:
            flight = Flight(**flight_data)
            db_session.add(flight)
        db_session.commit()
        
        # Get flights
        response = client.get("/flights")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        
        # Verify flight data
        for i, flight in enumerate(data):
            assert flight["origin"] == flights_data[i]["origin"]
            assert flight["destination"] == flights_data[i]["destination"]
            assert flight["price"] == flights_data[i]["price"]
            assert flight["seats_available"] == flights_data[i]["seats_available"]
            assert "flight_id" in flight
            assert flight["flight_id"] > 0

class TestFlightDataIntegrity:
    """Test flight data integrity and validation."""
    
    def test_flight_id_auto_increment(self, client, db_session):
        """Test that flight IDs auto-increment properly."""
        # Create multiple flights
        for i in range(3):
            flight = Flight(
                origin=f"Origin{i}",
                destination=f"Destination{i}",
                departure_time=f"2099-01-0{i+1}T09:00:00Z",
                arrival_time=f"2099-01-0{i+1}T17:00:00Z",
                price=1000000 + i * 100000,
                seats_available=5 + i
            )
            db_session.add(flight)
        db_session.commit()
        
        # Get flights and verify IDs
        response = client.get("/flights")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        flight_ids = [flight["flight_id"] for flight in data]
        
        # Verify IDs are unique and sequential
        assert len(set(flight_ids)) == len(flight_ids)  # All unique
        assert flight_ids == sorted(flight_ids)  # Sequential
    
    def test_flight_seats_available_validation(self, client, db_session):
        """Test that seats_available cannot go below 0."""
        # Create a flight with 0 seats
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=0
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Verify the flight exists with 0 seats
        response = client.get("/flights")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["seats_available"] == 0
    
    def test_flight_price_validation(self, client, db_session):
        """Test that flight prices are properly stored and retrieved."""
        test_prices = [0, 100000, 999999999]
        
        for price in test_prices:
            flight = Flight(
                origin="Earth",
                destination="Mars",
                departure_time="2099-01-01T09:00:00Z",
                arrival_time="2099-01-01T17:00:00Z",
                price=price,
                seats_available=5
            )
            db_session.add(flight)
        db_session.commit()
        
        # Get flights and verify prices
        response = client.get("/flights")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        retrieved_prices = [flight["price"] for flight in data]
        
        for price in test_prices:
            assert price in retrieved_prices

class TestFlightBookingIntegration:
    """Test integration between flights and bookings."""
    
    def test_flight_seats_decrement_on_booking(self, client, db_session, sample_user_data):
        """Test that flight seats are properly decremented when booking."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight with 3 seats
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=3
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Book the flight
        booking_data = {
            "user_id": user_id,
            "name": sample_user_data["name"],
            "flight_id": flight.flight_id
        }
        
        response = client.post("/book", json=booking_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify seats were decremented
        updated_flight = db_session.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
        assert updated_flight.seats_available == 2  # 3 - 1
    
    def test_flight_seats_increment_on_cancellation(self, client, db_session, sample_user_data):
        """Test that flight seats are properly incremented when cancelling."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight with 2 seats
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=2
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Create a booking
        from models import Booking
        booking = Booking(
            user_id=user_id,
            flight_id=flight.flight_id,
            status="booked",
            booking_time="2099-01-01T10:00:00Z"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)
        
        # Cancel the booking
        response = client.post(f"/cancel/{booking.booking_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify seats were incremented
        updated_flight = db_session.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
        assert updated_flight.seats_available == 3  # 2 + 1
    
    def test_multiple_bookings_same_flight(self, client, db_session, sample_user_data):
        """Test multiple bookings on the same flight."""
        # Register multiple users
        users = []
        for i in range(3):
            user_data = {
                "name": f"User{i}",
                "email": f"user{i}@example.com"
            }
            user_response = client.post("/register", json=user_data)
            assert user_response.status_code == status.HTTP_200_OK
            users.append(user_response.json())
        
        # Create a flight with 3 seats
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=3
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Book all available seats
        for user in users:
            booking_data = {
                "user_id": user["user_id"],
                "name": user["name"],
                "flight_id": flight.flight_id
            }
            
            response = client.post("/book", json=booking_data)
            assert response.status_code == status.HTTP_200_OK
        
        # Verify no seats are available
        updated_flight = db_session.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
        assert updated_flight.seats_available == 0
        
        # Try to book one more seat (should fail)
        extra_user_data = {
            "name": "ExtraUser",
            "email": "extra@example.com"
        }
        extra_user_response = client.post("/register", json=extra_user_data)
        assert extra_user_response.status_code == status.HTTP_200_OK
        
        extra_booking_data = {
            "user_id": extra_user_response.json()["user_id"],
            "name": "ExtraUser",
            "flight_id": flight.flight_id
        }
        
        extra_response = client.post("/book", json=extra_booking_data)
        assert extra_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No seats available" in extra_response.json()["detail"]
