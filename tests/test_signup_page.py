def test_signup_page_get(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Sign up" in response.data

def test_signup_page_post_valid_user(client):
    response = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/actions'
    
    
def test_signup_page_post_existing_user(client, set_user):
    response = client.post('/signup', data={'username': 'testuser','email': "newtest@example.com", 'password': 'password123'})
    assert response.status_code == 200
    assert b"This username is already taken" in response.data

def test_signup_page_post_existing_email(client, set_user):
    response = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    assert response.status_code == 200
    assert b"This email is already taken" in response.data
    

def test_signup_page_double_resignup(client):
    client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    response_get = client.get('/signup')
    response_post = client.post('/signup', data={'username': 'newuser','email': "test@example.com", 'password': 'password123'})
    assert response_get.status_code == response_post.status_code == 302
    assert response_get.headers['Location'] == response_post.headers['Location'] == '/'
    