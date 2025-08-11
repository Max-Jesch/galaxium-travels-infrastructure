from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User as UserModel, Flight as FlightModel, Booking as BookingModel
from db import get_db, init_db
from seed import seed
from pydantic import BaseModel, EmailStr
from datetime import datetime

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

@app.get(
    "/flights",
    response_model=list[Flight],
    operation_id="getFlights",
    summary="List all available flights",
    description="Retrieve a list of all available flights, including origin, destination, departure and arrival times, price, and the number of seats currently available for booking."
)
def get_flights(db: Session = Depends(get_db)):
    return db.query(FlightModel).all()

@app.post(
    "/book",
    response_model=Booking,
    operation_id="bookFlight",
    summary="Book a flight for a user",
    description="Book a seat on a specific flight for a user. Requires user_id, name, and flight_id in the request body. If the flight has available seats and the user_id matches the name, a new booking is created and the number of available seats is decremented by one. Returns the booking details."
)
def book_flight(booking: BookingRequest, db: Session = Depends(get_db)):
    flight = db.query(FlightModel).filter(FlightModel.flight_id == booking.flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=404, 
            detail="Flight not found. The specified flight_id does not exist in our system. Please check the flight_id or use the /flights endpoint to see available flights."
        )
    if flight.seats_available < 1:
        raise HTTPException(
            status_code=400, 
            detail="No seats available on this flight. The flight is fully booked. Please check other flights or try again later if seats become available."
        )
    user = db.query(UserModel).filter(UserModel.user_id == booking.user_id, UserModel.name == booking.name).first()
    if not user:
        # Check if user exists but name doesn't match
        existing_user = db.query(UserModel).filter(UserModel.user_id == booking.user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=404, 
                detail=f"User ID {booking.user_id} exists but the name '{booking.name}' does not match the registered name '{existing_user.name}'. Please verify the user's name or use the correct name for this user ID."
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID {booking.user_id} is not registered in our system. The user might need to register first using the /register endpoint, or you may need to check if the user_id is correct."
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

@app.get(
    "/bookings/{user_id}",
    response_model=list[Booking],
    operation_id="getUserBookings",
    summary="List all bookings for a user",
    description="Retrieve all bookings for a specific user by user_id. Returns a list of bookings, including booking status and booking time, for the given user."
)
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    return db.query(BookingModel).filter(BookingModel.user_id == user_id).all()

@app.post(
    "/cancel/{booking_id}",
    response_model=Booking,
    operation_id="cancelBooking",
    summary="Cancel a booking by booking ID",
    description="Cancel an existing booking by its booking_id. If the booking is active, its status is set to 'cancelled' and the number of available seats for the associated flight is incremented by one. Returns the updated booking details."
)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=404, 
            detail=f"Booking with ID {booking_id} not found. The booking may have been deleted or the booking_id may be incorrect. Please verify the booking_id or check if the booking exists."
        )
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=400, 
            detail=f"Booking {booking_id} is already cancelled and cannot be cancelled again. The booking status is currently '{booking.status}'. If you need to make changes, please contact support."
        )
    flight = db.query(FlightModel).filter(FlightModel.flight_id == booking.flight_id).first()
    if flight:
        flight.seats_available += 1
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking

@app.post(
    "/register",
    response_model=User,
    operation_id="registerUser",
    summary="Register a new user",
    description="Register a new user with a name and unique email. Returns the created user."
)
def register_user(user: UserRegistration, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Email '{user.email}' is already registered. A user with this email already exists in our system. If you're trying to access an existing account, use the /user_id endpoint with the correct name and email to get the user_id."
        )
    new_user = UserModel(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get(
    "/user_id",
    response_model=User,
    operation_id="getUser",
    summary="Get user by name and email",
    description="Retrieve a user's information (including user_id) by providing both name and email. Returns 404 if not found."
)

def get_user(name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.name == name, UserModel.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=f"User not found with name '{name}' and email '{email}'. The user may not be registered in our system. Please check the spelling of both name and email, or register the user first using the /register endpoint."
        )
    return user 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082) 