import pytest
from fastapi import status
from models import User

class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_user_success(self, client, db_session, sample_user_data):
        """Test successful user registration."""
        response = client.post("/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert "user_id" in data
        assert data["user_id"] > 0
        
        # Verify user was actually created in database
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        assert user is not None
        assert user.name == sample_user_data["name"]
        assert user.user_id == data["user_id"]
    
    def test_register_user_duplicate_email(self, client, db_session, sample_user_data):
        """Test registration with duplicate email fails."""
        # Register first user
        response1 = client.post("/register", json=sample_user_data)
        assert response1.status_code == status.HTTP_200_OK
        
        # Try to register second user with same email
        duplicate_user = sample_user_data.copy()
        duplicate_user["name"] = "Different Name"
        response2 = client.post("/register", json=duplicate_user)
        
        assert response2.status_code == status.HTTP_200_OK
        data = response2.json()
        assert data["success"] == False
        assert data["error"] == "Email already registered"
        assert data["error_code"] == "EMAIL_EXISTS"
        assert "already registered" in data["details"]
        assert "already exists in our system" in data["details"]
        assert "/user_id endpoint" in data["details"]
    
    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        # Missing name
        response1 = client.post("/register", json={"email": "test@example.com"})
        assert response1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response2 = client.post("/register", json={"name": "Test User"})
        assert response2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Empty request
        response3 = client.post("/register", json={})
        assert response3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_invalid_email_format(self, client):
        """Test registration with invalid email format."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test.example.com",
            ""
        ]
        
        for email in invalid_emails:
            response = client.post("/register", json={"name": "Test User", "email": email})
            # Note: FastAPI with Pydantic will validate email format
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestUserRetrieval:
    """Test user retrieval functionality."""
    
    def test_get_user_success(self, client, db_session, sample_user_data):
        """Test successful user retrieval by name and email."""
        # First register a user
        register_response = client.post("/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK
        user_data = register_response.json()
        
        # Then retrieve the user
        response = client.get(f"/user_id?name={sample_user_data['name']}&email={sample_user_data['email']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == user_data["user_id"]
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
    
    def test_get_user_not_found(self, client):
        """Test user retrieval when user doesn't exist."""
        response = client.get("/user_id?name=NonExistent&email=nonexistent@example.com")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] == False
        assert data["error"] == "User not found"
        assert data["error_code"] == "USER_NOT_FOUND"
        assert "may not be registered" in data["details"]
        assert "check the spelling" in data["details"]
        assert "/register endpoint" in data["details"]
    
    def test_get_user_missing_parameters(self, client):
        """Test user retrieval with missing parameters."""
        # Missing name
        response1 = client.get("/user_id?email=test@example.com")
        assert response1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response2 = client.get("/user_id?name=Test User")
        assert response2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # No parameters
        response3 = client.get("/user_id")
        assert response3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_user_empty_parameters(self, client):
        """Test user retrieval with empty parameters."""
        response = client.get("/user_id?name=&email=")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] == False
        assert data["error"] == "User not found"
        assert data["error_code"] == "USER_NOT_FOUND"
