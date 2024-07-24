import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))



import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from ...main import app
from api.db.database import get_db
from api.v1.models.newsletter import Newsletter
from api.v1.schemas.newsletter import EMAILSCHEMA


client = TestClient(app)

@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    # Clean up after the test by removing the override
    app.dependency_overrides = {}

def test_get_subscribers_empty(db_session_mock):
    db_session_mock.query(Newsletter).all.return_value = []
    response = client.get("/pages/newsletter/subscribers")
    assert response.status_code == 404
    assert response.json() == {
        "message": "No subscribers found",
        "success": False,
        "status_code": 404
    }

def test_get_subscribers_with_data(db_session_mock):
    test_subscriber = Newsletter(email="test@example.com")  # Adjust based on your model
    db_session_mock.query(Newsletter).all.return_value = [test_subscriber]

    response = client.get("/pages/newsletter/subscribers")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Subscribers retrieved successfully",
        "success": True,
        "status_code": 200,
        "data": ["test@example.com"]
    }




