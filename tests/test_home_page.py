def test_home_page_get_without_user(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Join our DevOps Bank" in response.data

def test_home_page_with_user(client, set_user):
    user = "testuser"
    response = client.post('/login', data={'username': user, 'password': 'password123'})
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome back " + user.encode('utf-8') in response.data