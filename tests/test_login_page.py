from bs4 import BeautifulSoup
def test_login_page_get(client):
    """Tests the login page GET request
       Raises:
        - AssertionError: If status code is not 200 (Ok) or the response data doesn't contains the "Login" message
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data 
    
def test_login_page_post_valid_user(client, set_user):
    """Tests the login page POST request with valid user credentials
       Raises:
        - AssertionError: If the status code is not 302 (Redirect) or the location header does not match '/actions'
    """
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/actions'
    
def test_login_page_post_dont_exist_user(client, set_user):
    """Tests the login page POST request with user credentials that are not exists
       Raises:
       - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contains the "Invalid login" message
    """
    response = client.post('/login', data={'username': 'fakeuser', 'password': 'password123'})
    assert response.status_code == 200
    assert b"Invalid username" in response.data
    
def test_login_page_relogin(client, set_user):
    """Tests the login page POST request after a successful login
       Raises:
        - AssertionError: If the status code is not 302 (Redirect) or the location header does not match '/'.
    """
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response_get = client.get('/login')
    response_post = client.post('/login', data={'username': 'test', 'password': 'password123'})
    assert response_get.status_code == response_post.status_code == 302
    assert response_get.headers['Location'] == response_post.headers['Location'] == '/'
    

def test_login_page_post_invalid_username(client):
    """Tests the login page POST request with an invalid username input
       Raises:
        - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contain the "invalid username input" error message
    """
    response = client.post('/login', data={'username': 'n', 'password': 'password123'})
    assert response.status_code == 200
    error = BeautifulSoup(response.data, 'html.parser').find("span", id='error')
    assert error.text == "Username must starts with a letter, followed by 5-14 letters or digits"
    
    
def test_login_page_post_invalid_password(client):
    """Tests the login page POST request with an invalid password input
       Raises:
        - AssertionError: If the status code is not 200 (Ok) or the response data doesn't contain the "invalid password input" error message
    """
    response = client.post('/login', data={'username': 'newuser', 'password': '123'})
    assert response.status_code == 200
    error = BeautifulSoup(response.data, 'html.parser').find("span", id='error')
    assert error.text == "Password must be 7-15 letters or digits"
    