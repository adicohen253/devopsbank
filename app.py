from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv

load_dotenv()
MONGODB_HOSTNAME = environ.get('MONGODB_HOSTNAME')
MONGODB_DATABASE = environ.get('MONGODB_DATABASE')
MONGODB_USERNAME = environ.get('MONGODB_USERNAME')
MONGODB_PASSWORD = environ.get('MONGODB_PASSWORD')

# MongoDB URI
uri = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOSTNAME}:27017/{MONGODB_DATABASE}"

class DevopsApplication:
    def __init__(self, client):
        self.app = Flask(__name__)
        self.dbclient = client

    def create_endpoints(self):
        @self.app.route('/')
        def home():
            return render_template("index.html")
        
        @self.app.route('/actions', methods=['GET', 'POST'])
        def actions():
            return render_template("actions.html")

        @self.app.route('/signup', methods=['GET', 'POST'])
        def signup():
            if request.method == 'GET':
                return render_template("signup.html")
            else: # POST request
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                error = check_signup_request(username, email)
                if error is None: # can create new account
                    self.dbclient.accounts.insert_one({"username": username, "email": email, "password": password, "balance": 0})
                    return redirect(url_for('actions'))
                return render_template("signup.html", error=error)

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                return render_template("login.html")
            else: # POST request
                user, password = request.form.get('username'), request.form.get('password')
                error = check_login_request(user, password)
                if error is None:
                    return render_template("actions.html")
                return render_template("login.html", error=error)
        
        def check_signup_request(username, email):
            if self.dbclient.accounts.find_one({"username": username}) is not None:
                return  "This username is already taken please pick another"
            if self.dbclient.accounts.find_one({"email": email}) is not None: # email already exists
                return "This email is already taken please pick another"
            return None
        
        def check_login_request(username, password):
            if self.dbclient.accounts.find_one({"username": username, "password":  password}) is None:
                return "Invalid username or password"
            return None
    
    def setup_accounts_collection(self):
        if 'accounts' not in self.dbclient.list_collection_names():
            client.create_collection('accounts')
            print("created 'accounts' collection")
    
    def start(self):
        self.setup_accounts_collection()
        self.create_endpoints()
        self.app.run(host="0.0.0.0", port="5000",debug=True)


if __name__ == '__main__':
    client = MongoClient(uri)[MONGODB_DATABASE]
    app = DevopsApplication(client)
    app.start()
    