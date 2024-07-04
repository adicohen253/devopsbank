from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from os import environ
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MONGODB_HOSTNAME = environ.get('MONGODB_HOSTNAME')
MONGODB_DATABASE = environ.get('MONGODB_DATABASE')
MONGODB_USERNAME = environ.get('MONGODB_USERNAME')
MONGODB_PASSWORD = environ.get('MONGODB_PASSWORD')
SESSION_KEY = environ.get('SESSION_SECRET')

# MongoDB URI
MONGODB_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOSTNAME}:27017/{MONGODB_DATABASE}"

class DevopsApplication:
    def __init__(self, client):
        self.app = Flask(__name__)
        self.app.secret_key = SESSION_KEY
        self.dbclient = client

    def create_endpoints(self):
        @self.app.route('/')
        def home():
            username = ""
            if 'username' in session:
                username = session['username']
            return render_template("index.html", username=username)

        @self.app.route('/logout')
        def logout():
            if 'username' in session:
                session.pop('username')
            return redirect(url_for('home'))
        
        @self.app.route('/actions', methods=['GET', 'POST'])
        def actions():
            if 'username' not in session:
                return redirect(url_for('login'))

            username = session['username']
            balance = self.dbclient.accounts.find_one({'username': session['username']}).get('balance')
            monthly_overview = overall_monthly(username, datetime.now().strftime("%m/%Y"))
            if request.method == 'POST':
                action, amount = request.form['action'], float(request.form['amount'])
                balance = calculate_balance(balance, amount, action)
                self.dbclient.accounts.update_one({"username": username}, {"$set": {"balance": balance}})
                update_history(username, amount, action, datetime.now().strftime("%d/%m/%Y"))
                return redirect(url_for('actions'))
            else: # get request
                return render_template("actions.html", username=username, balance=balance, overview=monthly_overview)
            
        @self.app.route('/signup', methods=['GET', 'POST'])
        def signup():
            if 'username' in session:
                return redirect(url_for('actions'))
            if request.method == 'GET':
                return render_template("signup.html")   
            else: # POST request
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                error = check_signup_request(username, email)
                if error is None: # can create new account
                    self.dbclient.accounts.insert_one({"username": username, "email": email, "password": password, "balance": 0})
                    session["username"] = username
                    return redirect(url_for('actions'))
                return render_template("signup.html", error=error)

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if 'username' in session:
                return redirect(url_for('actions'))
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
            if request == "deposit":
                return round(balance + amount,2)
            else: # withdraw
                return round(balance - amount, 2)
            
        def overall_monthly(username, month_year):
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
            transaction = {"action": action, "amount": amount, "date": date}
            if self.dbclient.transactions.find_one({"username": username}) is not None:
                self.dbclient.transactions.update_one({"username": username}, {"$push": {"history": transaction}})
            else:
                self.dbclient.transactions.insert_one({"username": username, "history": [transaction]})
        
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
    
    
    def start(self):
        self.create_endpoints()
        self.app.run(host="0.0.0.0", port="5000",debug=True)

if __name__ == '__main__':
    client = MongoClient(MONGODB_URI)[MONGODB_DATABASE]
    app = DevopsApplication(client)
    app.start()
    