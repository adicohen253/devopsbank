from bs4 import BeautifulSoup

def test_signup_page_get(client):
    """Tests the GET request to the '/signup' endpoint
       Raises:
        - AssertionError: If status code is not 200 (Ok) or the response data doesn't contains the "Sign up" message
    """
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Sign up" in response.data

def test_signup_page_post_valid_user(client):
    """Tests the POST request to the '/signup' endpoint with valid user data
       Raises:
        - AssertionError: If the status code is not 302 (Redirect) or the Location header does not equal '/actions'
    """
    response = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/actions'
    
def test_signup_page_post_existing_user(client, set_user):
    """Tests the POST request to the '/signup' endpoint with an existing user data
       Raises:
        - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contain the "User exist" error message
    """
    response = client.post('/signup', data={'username': 'testuser','email': "newtest@example.com", 'password': 'password123'})
    assert response.status_code == 200
    assert b"This username is already taken" in response.data

def test_signup_page_post_existing_email(client, set_user):
    """Tests the POST request to the '/signup' endpoint with an existing Email data
       Raises:
        - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contain the "Email exist" error message
    """
    response = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    assert response.status_code == 200
    assert b"This email is already taken" in response.data
    
def test_signup_page_double_resignup(client):
    """Tests the double submission of the signup form
       Raises:
        - AssertionError: If the status codes are not 302 (Redirect) the Location headers are not '/'
    """
    client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    response_get = client.get('/signup')
    response_post = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    assert response_get.status_code == response_post.status_code == 302
    assert response_get.headers['Location'] == response_post.headers['Location'] == '/'
    
def test_signup_page_post_invalid_username(client):
    """Tests the POST request to the '/signup' endpoint with an invalid username input
       Raises:
        - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contain the "Invalid username input" error message.
    """
    response = client.post('/signup', data={'username': 'n','email': "test@example.com", 'password': 'password123'})
    assert response.status_code == 200
    error = BeautifulSoup(response.data, 'html.parser').find("span", id='error')
    assert error.text == "Username must starts with a letter, followed by 5-14 letters or digits"
    
def test_signup_page_post_invalid_password(client):
    """Tests the POST request to the '/signup' endpoint with an invalid password input
       Raises:
        - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contain the "Invalid password input" error message.
    """
    response = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': '123'})
    assert response.status_code == 200
    error = BeautifulSoup(response.data, 'html.parser').find("span", id='error')
    assert error.text == "Password must be 7-15 letters or digits"
    