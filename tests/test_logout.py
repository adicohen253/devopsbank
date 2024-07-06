def test_logout_without_user(client):
    """Tests the logout functionality without a user being logged in
       Raises:
        - AssertionError: If the status code of the response is not 302 or the location header does not match '/'
    """
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_logout_with_user(client, set_user):
    """Tests the logout functionality with a user being logged in
       Raises:
        - AssertionError: If the status code of the response is not 302 or the location header does not match '/login'.
    """
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'
    