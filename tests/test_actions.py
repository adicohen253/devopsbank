from bs4 import BeautifulSoup

def test_actions_page_get(client, set_user):
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response = client.get('/actions')
    balance_span = BeautifulSoup(response.data, 'html.parser').find("span", id='balance')
    assert balance_span.text == '0$'
    
def test_actions_page_post(client, set_user):
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    client.post('/actions', data={'action': 'deposit', 'amount': 200.12})
    client.post('/actions', data={'action': 'withdraw', 'amount': 100})
    response = client.get('/actions')
    balance_span = BeautifulSoup(response.data, 'html.parser').find("span", id='balance')
    assert balance_span.text == '100.12$'
    
def test_action_page_without_user(client):
    response_get = client.get('/actions')
    response_post = client.post('/actions', data={'action': 'deposit', 'amount': 200.12})
    assert response_get.status_code == response_post.status_code == 302
    assert response_get.headers['Location'] == response_post.headers['Location'] == '/'