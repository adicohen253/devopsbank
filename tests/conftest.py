import pytest
from mongomock import MongoClient as MockMongoClient
from .config import TestConfig
from app import DevopsApplication

@pytest.fixture
def setup_client_db():
    return MockMongoClient(TestConfig.MONGO_URI)[TestConfig.DB]
    

@pytest.fixture
def app(setup_client_db):
    application = DevopsApplication(setup_client_db)
    application.app.secret_key = TestConfig.SECRET_KEY
    application.create_endpoints()
    return application.app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def set_user(setup_client_db):
    db_client = setup_client_db
    # Insert a mock user into the mock MongoDB
    user_data = {
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'balance': 0
    }
    db_client.accounts.insert_one(user_data)
    yield
    db_client.accounts.delete_many({})