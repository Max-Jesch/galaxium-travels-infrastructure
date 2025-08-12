from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User as UserModel, Flight as FlightModel, Booking as BookingModel
from db import get_db, init_db
from seed import seed
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Union
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Galaxium Travels Booking API",
    description="API for booking flights and managing users",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()
    seed()

class Flight(BaseModel):
    flight_id: int
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: int
    seats_available: int
    class Config:
        from_attributes = True

class BookingRequest(BaseModel):
    user_id: int
    name: str
    flight_id: int

class Booking(BaseModel):
    booking_id: int
    user_id: int
    flight_id: int
    status: str
    booking_time: str
    class Config:
        from_attributes = True

class UserRegistration(BaseModel):
    name: str
    email: EmailStr

class User(BaseModel):
    user_id: int
    name: str
    email: str
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
    details: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool = True
    data: Union[Flight, list[Flight], Booking, list[Booking], User]

def create_error_response(error: str, error_code: str, details: Optional[str] = None):
    """Create a standardized error response that returns 200 status code"""
    return JSONResponse(
        status_code=200,
        content=ErrorResponse(
            success=False,
            error=error,
            error_code=error_code,
            details=details
        ).dict()
    )

@app.get(
    "/flights",
    response_model=list[Flight],
    operation_id="getFlights",
    summary="List all available flights",
    description="Retrieve a list of all available flights, including origin, destination, departure and arrival times, price, and the number of seats currently available for booking."
)
def get_flights(db: Session = Depends(get_db)):
    try:
        flights = db.query(FlightModel).all()
        return flights
    except Exception as e:
        # This is a truly fatal error - database connection issue
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post(
    "/book",
    response_model=Union[Booking, ErrorResponse],
    operation_id="bookFlight",
    summary="Book a flight for a user",
    description="Book a seat on a specific flight for a user. Requires user_id, name, and flight_id in the request body. If the flight has available seats and the user_id matches the name, a new booking is created and the number of available seats is decremented by one. Returns the booking details."
)
def book_flight(booking: BookingRequest, db: Session = Depends(get_db)):
    try:
        flight = db.query(FlightModel).filter(FlightModel.flight_id == booking.flight_id).first()
        if not flight:
            return create_error_response(
                "Flight not found",
                "FLIGHT_NOT_FOUND",
                f"The specified flight_id {booking.flight_id} does not exist in our system. Please check the flight_id or use the /flights endpoint to see available flights."
            )
        
        if flight.seats_available < 1:
            return create_error_response(
                "No seats available",
                "NO_SEATS_AVAILABLE",
                "The flight is fully booked. Please check other flights or try again later if seats become available."
            )
        
        user = db.query(UserModel).filter(UserModel.user_id == booking.user_id, UserModel.name == booking.name).first()
        if not user:
            # Check if user exists but name doesn't match
            existing_user = db.query(UserModel).filter(UserModel.user_id == booking.user_id).first()
            if existing_user:
                return create_error_response(
                    "Name mismatch",
                    "NAME_MISMATCH",
                    f"User ID {booking.user_id} exists but the name '{booking.name}' does not match the registered name '{existing_user.name}'. Please verify the user's name or use the correct name for this user ID."
                )
            else:
                return create_error_response(
                    "User not found",
                    "USER_NOT_FOUND",
                    f"User with ID {booking.user_id} is not registered in our system. The user might need to register first using the /register endpoint, or you may need to check if the user_id is correct."
                )
        
        # Decrement seat
        flight.seats_available -= 1
        new_booking = BookingModel(
            user_id=booking.user_id,
            flight_id=booking.flight_id,
            status="booked",
            booking_time=datetime.utcnow().isoformat()
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking
        
    except Exception as e:
        # This is a truly fatal error - database transaction issue
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get(
    "/bookings/{user_id}",
    response_model=list[Booking],
    operation_id="getUserBookings",
    summary="List all bookings for a user",
    description="Retrieve all bookings for a specific user by user_id. Returns a list of bookings, including booking status and booking time, for the given user."
)
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    try:
        bookings = db.query(BookingModel).filter(BookingModel.user_id == user_id).all()
        return bookings
    except Exception as e:
        # This is a truly fatal error - database connection issue
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post(
    "/cancel/{booking_id}",
    response_model=Union[Booking, ErrorResponse],
    operation_id="cancelBooking",
    summary="Cancel a booking by booking ID",
    description="Cancel an existing booking by its booking_id. If the booking is active, its status is set to 'cancelled' and the number of available seats for the associated flight is incremented by one. Returns the updated booking details."
)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    try:
        booking = db.query(BookingModel).filter(BookingModel.booking_id == booking_id).first()
        if not booking:
            return create_error_response(
                "Booking not found",
                "BOOKING_NOT_FOUND",
                f"Booking with ID {booking_id} not found. The booking may have been deleted or the booking_id may be incorrect. Please verify the booking_id or check if the booking exists."
            )
        
        if booking.status == "cancelled":
            return create_error_response(
                "Booking already cancelled",
                "ALREADY_CANCELLED",
                f"Booking {booking_id} is already cancelled and cannot be cancelled again. The booking status is currently '{booking.status}'. If you need to make changes, please contact support."
            )
        
        flight = db.query(FlightModel).filter(FlightModel.flight_id == booking.flight_id).first()
        if flight:
            flight.seats_available += 1
        booking.status = "cancelled"
        db.commit()
        db.refresh(booking)
        return booking
        
    except Exception as e:
        # This is a truly fatal error - database transaction issue
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post(
    "/register",
    response_model=Union[User, ErrorResponse],
    operation_id="registerUser",
    summary="Register a new user",
    description="Register a new user with a name and unique email. Returns the created user."
)
def register_user(user: UserRegistration, db: Session = Depends(get_db)):
    try:
        existing = db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing:
            return create_error_response(
                "Email already registered",
                "EMAIL_EXISTS",
                f"Email '{user.email}' is already registered. A user with this email already exists in our system. If you're trying to access an existing account, use the /user_id endpoint with the correct name and email to get the user_id."
            )
        
        new_user = UserModel(name=user.name, email=user.email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except Exception as e:
        # This is a truly fatal error - database transaction issue
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get(
    "/user_id",
    response_model=Union[User, ErrorResponse],
    operation_id="getUser",
    summary="Get user by name and email",
    description="Retrieve a user's information (including user_id) by providing both name and email. Returns error response if not found."
)
def get_user(name: str, email: str, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(UserModel.name == name, UserModel.email == email).first()
        if not user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                f"User not found with name '{name}' and email '{email}'. The user may not be registered in our system. Please check the spelling of both name and email, or register the user first using the /register endpoint."
            )
        return user
        
    except Exception as e:
        # This is a truly fatal error - database connection issue
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082) 