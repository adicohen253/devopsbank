from bs4 import BeautifulSoup
from datetime import datetime

def test_actions_page_get(client, set_user, set_history):
    """Tests the '/actions' page by logging in as a user, Then checks if the balance, monthly overview and stats displayed on the page are correct
       Raises:
        - AssertionError: If the balance, overview or stats is incorrect
    """
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response = client.get('/actions')
    balance_span = BeautifulSoup(response.data, 'html.parser').find("span", id='balance')
    overview = str(BeautifulSoup(response.data, 'html.parser').find('script', id="overview-data"))
    overview = eval(overview[overview.index('[')+1:overview.index(']')])
    action_number = BeautifulSoup(response.data, 'html.parser').find('td', id="action-number")
    avg_actions_per_day = BeautifulSoup(response.data, 'html.parser').find('td', id="avg-actions-per-day")
    avg_amount_per_action = BeautifulSoup(response.data, 'html.parser').find('td', id="avg-amount-per-action")
    assert action_number.text == '3'
    assert avg_actions_per_day.text == str((round(3 / datetime.today().day,1)))
    assert avg_amount_per_action.text == "93.48"
    assert overview[0]['date'] == "01/" + datetime.now().strftime("%m/%Y")
    assert overview[1]['total'] == -19.55
    assert balance_span.text == '180.45$'
    
def test_actions_page_post_valid(client, set_user):
    """Tests the '/actions' page by logging in as a user, making deposit and withdraw actions.
       Then checks if the balance and monthly overview displayed on the page are correct
       Raises:
        - AssertionError: If the balance, overview or stats is incorrect
    """
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    response = client.post('/actions', data={'action': 'deposit', 'amount': "200.12"})
    response = client.post('/actions', data={'action': 'withdraw', 'amount': "100"})
    response = client.get('/actions')
    balance_span = str(BeautifulSoup(response.data, 'html.parser').find("span", id='balance'))
    balance = balance_span[balance_span.index(">")+1:balance_span.index("</")]
    overview = str(BeautifulSoup(response.data, 'html.parser').find('script', id="overview-data"))
    overview = eval(overview[overview.index('[')+1:overview.index(']')])
    action_number = BeautifulSoup(response.data, 'html.parser').find('td', id="action-number")
    avg_actions_per_day = BeautifulSoup(response.data, 'html.parser').find('td', id="avg-actions-per-day")
    avg_amount_per_action = BeautifulSoup(response.data, 'html.parser').find('td', id="avg-amount-per-action")
    assert action_number.text == '2'
    assert avg_actions_per_day.text == str((round(2 / datetime.today().day,1)))
    assert avg_amount_per_action.text == "150.06"
    assert overview['date'] == datetime.now().strftime(f"%d/%m/%Y")
    assert overview['total'] == 100.12
    assert balance == '100.12$'
    
def test_action_page_without_user(client):
    """Tests the '/actions' page without a logged-in user, checks if the user is redirected to the login page when trying to access the '/actions' page
       Raises:
        - AssertionError: If the user is not redirected to the login page
    """
    response_get = client.get('/actions')
    response_post = client.post('/actions', data={'action': 'deposit', 'amount': "200.12"})
    assert response_get.status_code == response_post.status_code == 302
    assert response_get.headers['Location'] == response_post.headers['Location'] == '/'
    
    
def test_action_page_post_invalid_amount(client, set_user):
    """Tests the '/actions' page by logging in as a user, attempting to make a deposit with an invalid amount.
       Then checks if the error message displayed on the page is correct
       Raises:
        - AssertionError: If the error message is incorrect or user not in the actions page
    
    """
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    invalid_number_amount_response = client.post('/actions', data={'action': 'deposit', 'amount': "12.334"})
    invalid_string_amount_response = client.post('/actions', data={'action': 'deposit', 'amount': "invalid_string"})
    invalid_number_error_response = BeautifulSoup(invalid_number_amount_response.data, 'html.parser').find("span", id='error')
    invalid_string_error_response = BeautifulSoup(invalid_string_amount_response.data, 'html.parser').find("span", id='error')
    assert invalid_number_amount_response.status_code == invalid_string_amount_response.status_code == 200
    assert invalid_number_error_response.text == invalid_string_error_response.text ==  "Amount has to be valid number up to two decimal digits"
    
def test_action_page_post_invalid_action(client, set_user):
    """Tests the '/actions' page by logging in as a user, attempting to make a deposit with an invalid action.
       Then checks if the error message displayed on the page is correct
       Raises:
        - AssertionError: If the error message is incorrect or user not in the actions page
    """
    client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    invalid_string_action_response = client.post('/actions', data={'action': 'invalidaction', 'amount': "12.33"})
    invalid_string_error_response = BeautifulSoup(invalid_string_action_response.data, 'html.parser').find("span", id='error')
    assert invalid_string_action_response.status_code == 200
    assert invalid_string_error_response.text == "Invalid action (must be 'deposit' or 'withdraw')"