def test_logout_without_user(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_logout_with_user(client, set_user):
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'
    