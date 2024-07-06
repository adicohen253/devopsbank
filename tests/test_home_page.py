def test_home_page_get_without_user(client):
    """Tests the home page GET request without a logged-in user
       Raises:
        - AssertionError: If the HTTP status code is not 200 or if the expected string "Join our DevOps Bank" is not found in the response data
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Join our DevOps Bank" in response.data

def test_home_page_with_user(client, set_user):
    """Tests the home page GET request with a logged-in user
       Raises:
        - AssertionError: If the HTTP status code is not 200 or if the expected string "Welcome back " + user is not found in the response data
    """
    user = "testuser"
    response = client.post('/login', data={'username': user, 'password': 'password123'})
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome back " + user.encode('utf-8') in response.data