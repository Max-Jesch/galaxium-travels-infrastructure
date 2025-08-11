import pytest
from fastapi import status
from models import User, Flight, Booking

class TestFlightBooking:
    """Test flight booking functionality."""
    
    def test_book_flight_success(self, client, db_session, sample_user_data):
        """Test successful flight booking."""
        # First register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight in the database
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=5
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
        data = response.json()
        assert data["user_id"] == user_id
        assert data["flight_id"] == flight.flight_id
        assert data["status"] == "booked"
        assert "booking_time" in data
        
        # Verify booking was created in database
        booking = db_session.query(Booking).filter(Booking.booking_id == data["booking_id"]).first()
        assert booking is not None
        assert booking.user_id == user_id
        assert booking.flight_id == flight.flight_id
        
        # Verify seat count was decremented
        updated_flight = db_session.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
        assert updated_flight.seats_available == 4  # 5 - 1
    
    def test_book_flight_user_id_name_mismatch(self, client, db_session, sample_user_data):
        """Test that booking fails when user_id doesn't match the name."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=5
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Try to book with wrong name
        booking_data = {
            "user_id": user_id,
            "name": "Wrong Name",  # Different from registered name
            "flight_id": flight.flight_id
        }
        
        response = client.post("/book", json=booking_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User ID" in response.json()["detail"]
        assert "exists but the name" in response.json()["detail"]
        assert "does not match the registered name" in response.json()["detail"]
        
        # Verify no booking was created
        bookings = db_session.query(Booking).filter(Booking.flight_id == flight.flight_id).all()
        assert len(bookings) == 0
        
        # Verify seat count wasn't changed
        updated_flight = db_session.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
        assert updated_flight.seats_available == 5
    
    def test_book_flight_user_not_found(self, client, db_session):
        """Test booking fails when user doesn't exist."""
        # Create a flight
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=5
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Try to book with non-existent user
        booking_data = {
            "user_id": 999,  # Non-existent user ID
            "name": "Non Existent User",
            "flight_id": flight.flight_id
        }
        
        response = client.post("/book", json=booking_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User with ID 999 is not registered" in response.json()["detail"]
        assert "might need to register first" in response.json()["detail"]
    
    def test_book_flight_not_found(self, client, db_session, sample_user_data):
        """Test booking fails when flight doesn't exist."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Try to book non-existent flight
        booking_data = {
            "user_id": user_id,
            "name": sample_user_data["name"],
            "flight_id": 999  # Non-existent flight ID
        }
        
        response = client.post("/book", json=booking_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Flight not found" in response.json()["detail"]
        assert "does not exist in our system" in response.json()["detail"]
        assert "/flights endpoint" in response.json()["detail"]
    
    def test_book_flight_no_seats_available(self, client, db_session, sample_user_data):
        """Test booking fails when no seats are available."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight with no seats
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
        
        # Try to book
        booking_data = {
            "user_id": user_id,
            "name": sample_user_data["name"],
            "flight_id": flight.flight_id
        }
        
        response = client.post("/book", json=booking_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No seats available" in response.json()["detail"]
        assert "fully booked" in response.json()["detail"]
        assert "check other flights" in response.json()["detail"]

class TestBookingRetrieval:
    """Test booking retrieval functionality."""
    
    def test_get_user_bookings_success(self, client, db_session, sample_user_data):
        """Test successful retrieval of user bookings."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=5
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Create a booking
        booking = Booking(
            user_id=user_id,
            flight_id=flight.flight_id,
            status="booked",
            booking_time="2099-01-01T10:00:00Z"
        )
        db_session.add(booking)
        db_session.commit()
        
        # Retrieve user bookings
        response = client.get(f"/bookings/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == user_id
        assert data[0]["flight_id"] == flight.flight_id
        assert data[0]["status"] == "booked"
    
    def test_get_user_bookings_no_bookings(self, client, db_session, sample_user_data):
        """Test retrieval when user has no bookings."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Try to get bookings
        response = client.get(f"/bookings/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0
    
    def test_get_user_bookings_invalid_user_id(self, client):
        """Test retrieval with invalid user ID."""
        response = client.get("/bookings/999")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0

class TestBookingCancellation:
    """Test booking cancellation functionality."""
    
    def test_cancel_booking_success(self, client, db_session, sample_user_data):
        """Test successful booking cancellation."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=4
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Create a booking
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
        data = response.json()
        assert data["status"] == "cancelled"
        
        # Verify booking was updated in database
        updated_booking = db_session.query(Booking).filter(Booking.booking_id == booking.booking_id).first()
        assert updated_booking.status == "cancelled"
        
        # Verify seat count was incremented
        updated_flight = db_session.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
        assert updated_flight.seats_available == 5  # 4 + 1
    
    def test_cancel_booking_not_found(self, client):
        """Test cancellation of non-existent booking."""
        response = client.post("/cancel/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Booking with ID 999 not found" in response.json()["detail"]
        assert "may have been deleted" in response.json()["detail"]
        assert "verify the booking_id" in response.json()["detail"]
    
    def test_cancel_already_cancelled_booking(self, client, db_session, sample_user_data):
        """Test cancellation of already cancelled booking."""
        # Register a user
        user_response = client.post("/register", json=sample_user_data)
        assert user_response.status_code == status.HTTP_200_OK
        user_id = user_response.json()["user_id"]
        
        # Create a flight
        flight = Flight(
            origin="Earth",
            destination="Mars",
            departure_time="2099-01-01T09:00:00Z",
            arrival_time="2099-01-01T17:00:00Z",
            price=1000000,
            seats_available=5
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        
        # Create a cancelled booking
        booking = Booking(
            user_id=user_id,
            flight_id=flight.flight_id,
            status="cancelled",
            booking_time="2099-01-01T10:00:00Z"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)
        
        # Try to cancel again
        response = client.post(f"/cancel/{booking.booking_id}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already cancelled" in response.json()["detail"]
        assert "cannot be cancelled again" in response.json()["detail"]
        assert "contact support" in response.json()["detail"]
