from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from os import environ
from datetime import datetime
from dotenv import load_dotenv
from flask_session import Session
from re import match

load_dotenv()
MONGODB_HOSTNAME = environ.get('MONGODB_HOSTNAME')
MONGODB_DATABASE = environ.get('MONGODB_DATABASE')
MONGODB_USERNAME = environ.get('MONGODB_USERNAME')
MONGODB_PASSWORD = environ.get('MONGODB_PASSWORD')
SESSION_KEY = environ.get('SESSION_SECRET')

# MongoDB URI
MONGODB_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOSTNAME}:27017/{MONGODB_DATABASE}"

# Regular expressions
USER_CREDENTIALS_REGEX = r'^[A-Za-z][A-Za-z0-9]{5,14}$' # starts with a letter, followed by 5-14 letters or digits
PASSWORD_CREDENTIALS_REGEX = r'^[A-Za-z0-9]{7,15}$' # 7-15 letters or digits
MONEY_AMOUNT_REGEX = r"^[0-9]+([.,][0-9]{1,2})?$" # Amount has to be valid number up to two decimal digits

# CLIENT_MESSAGES
EMAIL_TAKEN = "This email is already taken please pick another"
USERNAME_RULE = "Username must starts with a letter, followed by 5-14 letters or digits"
PASSWORD_RULE = "Password must be 7-15 letters or digits"
INVALID_ACTION = "Invalid action (must be 'deposit' or 'withdraw')"
INVALID_AMOUNT = "Amount has to be valid number up to two decimal digits"
INVALID_LOGIN_REQUEST = "Invalid username or password"
USERNAME_TAKEN = "This username is already taken please pick another"

class DevopsApplication:
    def __init__(self, client, db, session_key, use_backend_session):
        self.app = Flask(__name__)
        self.app.secret_key = session_key
        self.dbclient = client[db]
        if use_backend_session:
            self.app.config['SESSION_TYPE'] = 'mongodb'
            self.app.config['SESSION_MONGODB'] = client
            self.app.config['SESSION_MONGODB_DB'] = db
            Session(self.app)

    def create_endpoints(self):
        """Creates the necessary endpoints for the application."""
        @self.app.route('/')
        def home():
            """Renders the home page"""
            username = ""
            if 'username' in session:
                username = session['username']
            return render_template("index.html", username=username)

        @self.app.route('/logout')
        def logout():
            """Logs the user out and redirects them to the login page"""
            if 'username' in session:
                session.pop('username')
                return redirect(url_for("login"))
            return redirect(url_for('home'))
        
        @self.app.route('/actions', methods=['GET', 'POST'])
        def actions():
            """Handles the actions endpoint, where user can deposit/withdraw money and watch his history"""
            if 'username' not in session:
                return redirect(url_for('home'))
            username = session['username']
            balance = self.dbclient.accounts.find_one({'username': session['username']}).get('balance')
            monthly_overview = overall_monthly(username, datetime.now().strftime("%m/%Y"))
            stats = stats_monthly(username)
            error = None
            if request.method == 'POST':
                action, amount = request.form.get('action'), request.form.get('amount')
                if match(MONEY_AMOUNT_REGEX, amount):
                    amount = float(amount)
                    if action in ['deposit', 'withdraw']:
                        balance = calculate_balance(balance, amount, action)
                        self.dbclient.accounts.update_one({"username": username}, {"$set": {"balance": balance}})
                        update_history(username, amount, action, datetime.now().strftime("%d/%m/%Y"))
                        return redirect(url_for('actions'))
                    else:
                        error = INVALID_ACTION
                else:
                    error = INVALID_AMOUNT
            return render_template("actions.html", username=username, balance=balance,
                                   stats=stats, overview=monthly_overview, error=error)
            
        @self.app.route('/signup', methods=['GET', 'POST'])
        def signup():
            """Handles the signup endpoint, accesible for clients who aren't logged in yet"""
            if 'username' in session:
                return redirect(url_for('home'))
            if request.method == 'GET':
                return render_template("signup.html")   
            else: # POST request
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                error = check_signup_request(username, password, email)
                if error is None: # can create new account
                    self.dbclient.accounts.insert_one({"username": username, "email": email, "password": password, "balance": 0})
                    session["username"] = username
                    return redirect(url_for('actions'))
                return render_template("signup.html", error=error)

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Handles the login endpoint, accesible for clients who aren't logged in yet"""
            if 'username' in session:
                return redirect(url_for('home'))
            if request.method == 'GET':
                return render_template("login.html")
            else: # POST request
                username, password = request.form.get('username'), request.form.get('password')
                error = check_login_request(username, password)
                if error is None:
                    session['username'] = username
                    return redirect(url_for("actions"))
                return render_template("login.html", error=error)
            
        def calculate_balance(balance, amount,request):
            """Calculates the new balance after a deposit or withdrawal"""
            if request == "deposit":
                return round(balance + amount,2)
            else: # withdraw
                return round(balance - amount, 2)
            
        def stats_monthly(username):
            transaction_history = self.dbclient.transactions.find_one({"username": username}) 
            if transaction_history is not None:
                history = transaction_history['history']
                actions_number_in_month = len(list(filter(lambda x: x['date'].endswith(datetime.now().strftime('/%m/%Y')), history)))
                avg_actions_per_day = actions_number_in_month / datetime.today().day
                avg_amount_per_action = round(sum(transaction['amount'] for transaction in history) / actions_number_in_month, 2)
                return [actions_number_in_month, avg_actions_per_day, avg_amount_per_action]
            return [0, 0, 0]
            
        def overall_monthly(username, month_year):
            """Calculates the total amount deposited or withdrawn per day in a given month
                Args:
                username (str): The username of the account.
                month_year (str): The month and year to calculate the total for.

                Returns:
                    list: A list of dictionaries containing the total amount deposited or withdrawn for each day in the given month.
                """
            pipeline = [{'$match': {"username": username}},{"$unwind": "$history"},{"$match": {"history.date": {"$regex": f"{month_year}$"}}},
            {
                "$group": {
                    "_id": "$history.date",
                    "total": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$history.action", "deposit"]},
                                "$history.amount",
                                {"$multiply": ["$history.amount", -1]}
                            ]
                        }
                    }
                }
            },
            {"$project": {"_id": 0, "date": "$_id", "total": 1}}]
            overall_daily_list = list(self.dbclient.transactions.aggregate(pipeline))
            return overall_daily_list
             
        def update_history(username, amount, action, date):
            """Updates the transaction history with a new transaction.
                Args:
                    username (str): The username of the account.
                    amount (float): The amount of the transaction.
                    action (str): The type of the transaction ('deposit' or 'withdraw').
                    date (str): The date of the transaction.
            """
            transaction = {"action": action, "amount": amount, "date": date}
            if self.dbclient.transactions.find_one({"username": username}) is not None:
                self.dbclient.transactions.update_one({"username": username}, {"$push": {"history": transaction}})
            else:
                self.dbclient.transactions.insert_one({"username": username, "history": [transaction]})
        
        def check_signup_request(username, password, email):
            """Validates the signup request.
            Args:
                username (str): The username to validate.
                password (str): The password to validate.
                email (str): The email to validate.

            Returns:
                str: A message indicating the error if the request is invalid.
            """
            if not match(USER_CREDENTIALS_REGEX, username):
                return USERNAME_RULE
            if not match(PASSWORD_CREDENTIALS_REGEX, password):
                return PASSWORD_RULE
            if self.dbclient.accounts.find_one({"username": username}) is not None:
                return USERNAME_TAKEN
            if self.dbclient.accounts.find_one({"email": email}) is not None: # email already exists
                return EMAIL_TAKEN
            return None
        
        def check_login_request(username, password):
            """Validates the signup request.
            Args:
                username (str): The username to validate.
                password (str): The password to validate.

            Returns:
                str: A message indicating the error if the request is invalid.
            """
            if not match(USER_CREDENTIALS_REGEX, username):
                return USERNAME_RULE
            if not match(PASSWORD_CREDENTIALS_REGEX, password):
                return PASSWORD_RULE
            if self.dbclient.accounts.find_one({"username": username, "password":  password}) is None:
                return INVALID_LOGIN_REQUEST
            return None
    
    def start(self):
        self.create_endpoints()
        self.app.run(host="0.0.0.0", port="5000",debug=True)

if __name__ == '__main__':
    client = MongoClient(MONGODB_URI)
    app = DevopsApplication(client, MONGODB_DATABASE, SESSION_KEY, True)
    app.start()
    