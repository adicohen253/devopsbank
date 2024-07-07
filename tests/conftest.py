import pytest
from mongomock import MongoClient as MockMongoClient
from .config import TestConfig
from app import DevopsApplication
from datetime import datetime

@pytest.fixture
def setup_client_db():
    """Creates a MockMongoClient instance with the provided MONGO_URI from TestConfig"""
    return MockMongoClient(TestConfig.MONGO_URI)
    

@pytest.fixture
def app(setup_client_db):
    """
    Creates a DevopsApplication instance with the provided setup_client_db,
    sets the secret key to the value in TestConfig.SECRET_KEY,
    creates all necessary endpoints, and returns the Flask application object
    """
    application = DevopsApplication(setup_client_db, TestConfig.DB, TestConfig.SECRET_KEY, False)
    application.create_endpoints()
    return application.app

@pytest.fixture
def client(app):
    """Creates a test client instance for the Flask application"""
    return app.test_client()


@pytest.fixture
def set_user(setup_client_db):
    """Sets up a mock user for a user login requests in the mock MongoDB"""
    db_client = setup_client_db[TestConfig.DB]
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
    
@pytest.fixture
def set_history(setup_client_db):
    """Sets up a mock history of transactions for a user in the mock MongoDB"""
    db_client = setup_client_db[TestConfig.DB]
    transactions_data = {
        "username" : 'testuser',
        "history": [
            {
            "action": "deposit",
            "amount": 200,
            "date": "01/" + datetime.now().strftime("%m/%Y")
            },
            {
            "action": "deposit",
            "amount": 30.45,
            "date": "02/" + datetime.now().strftime("%m/%Y")
            },
            {
            "action": "withdraw",
            "amount": 50,
            "date": "02/" +  datetime.now().strftime("%m/%Y")
            }
        ]
    }
    db_client.transactions.insert_one(transactions_data)
    yield
    db_client.transactions.delete_many({})