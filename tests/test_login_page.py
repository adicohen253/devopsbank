def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data 
    
def test_login_page_post_valid_user(client, set_user):
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/actions'
    
def test_login_page_post_dont_exist_user(client, set_user):
    response = client.post('/login', data={'username': 'fakeuser', 'password': 'password123'})
    assert response.status_code == 200
    assert b"Invalid username" in response.data
    
def test_login_page_relogin(client, set_user):
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response_get = client.get('/login')
    response_post = client.post('/login', data={'username': 'test', 'password': 'password123'})
    assert response_get.status_code == response_post.status_code == 302
    assert response_get.headers['Location'] == response_post.headers['Location'] == '/'
    

    