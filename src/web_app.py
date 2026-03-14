"""
Online Banking System - Web Application
Flask-based web interface for banking operations
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager
from transaction_manager import TransactionManager
from db_connection import db

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, customer_id, email, first_name, last_name):
        self.id = customer_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

@login_manager.user_loader
def load_user(customer_id):
    """Load user for Flask-Login"""
    customer = AccountManager.get_customer(int(customer_id))
    if customer:
        return User(customer['customer_id'], customer['email'], 
                   customer['first_name'], customer['last_name'])
    return None

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Simple authentication (in production, use proper password hashing)
        # For demo purposes, we'll use email as password
        try:
            # Find customer by email
            query = "SELECT * FROM customers WHERE email = ?"
            result = db.execute_query(query, (email,))
            
            if result and len(result) > 0:
                customer = dict(result[0])
                # Simple password check (email as password for demo)
                if password == email.split('@')[0]:  # Use part before @ as password
                    user = User(customer['customer_id'], customer['email'],
                              customer['first_name'], customer['last_name'])
                    login_user(user)
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password!', 'error')
            else:
                flash('User not found!', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        dob = request.form.get('date_of_birth', '')
        
        try:
            customer_id = AccountManager.create_customer(
                first_name, last_name, email, phone, address, dob
            )
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        # Get user's accounts
        accounts = AccountManager.get_customer_accounts(current_user.id)
        
        # Get recent transactions for all accounts
        recent_transactions = []
        for account in accounts:
            transactions = TransactionManager.get_transaction_history(account['account_id'], 5)
            for txn in transactions:
                txn['account_number'] = account['account_number']
                recent_transactions.append(txn)
        
        # Sort by date and take latest 10
        recent_transactions.sort(key=lambda x: x['transaction_date'], reverse=True)
        recent_transactions = recent_transactions[:10]
        
        # Calculate total balance
        total_balance = sum(float(acc['balance']) for acc in accounts)
        
        return render_template('dashboard.html', 
                             accounts=accounts,
                             recent_transactions=recent_transactions,
                             total_balance=total_balance)
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/accounts')
@login_required
def accounts():
    """Account management page"""
    try:
        accounts = AccountManager.get_customer_accounts(current_user.id)
        return render_template('accounts.html', accounts=accounts)
    except Exception as e:
        flash(f'Error loading accounts: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/create_account', methods=['GET', 'POST'])
@login_required
def create_account():
    """Create new account"""
    if request.method == 'POST':
        account_type = request.form['account_type']
        initial_balance = float(request.form.get('initial_balance', 0))
        
        try:
            account = AccountManager.create_account(
                current_user.id, account_type, initial_balance
            )
            flash('Account created successfully!', 'success')
            return redirect(url_for('accounts'))
        except Exception as e:
            flash(f'Error creating account: {str(e)}', 'error')
    
    return render_template('create_account.html')

@app.route('/transactions')
@login_required
def transactions():
    """Transaction page"""
    try:
        accounts = AccountManager.get_customer_accounts(current_user.id)
        return render_template('transactions.html', accounts=accounts)
    except Exception as e:
        flash(f'Error loading transactions: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/deposit', methods=['POST'])
@login_required
def deposit():
    """Process deposit"""
    account_id = int(request.form['account_id'])
    amount = float(request.form['amount'])
    description = request.form.get('description', '')
    
    try:
        # Verify account belongs to user
        account = AccountManager.get_account(account_id)
        if not account or account['customer_id'] != current_user.id:
            flash('Invalid account!', 'error')
            return redirect(url_for('transactions'))
        
        TransactionManager.deposit(account_id, amount, description)
        flash('Deposit successful!', 'success')
    except Exception as e:
        flash(f'Deposit error: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    """Process withdrawal"""
    account_id = int(request.form['account_id'])
    amount = float(request.form['amount'])
    description = request.form.get('description', '')
    
    try:
        # Verify account belongs to user
        account = AccountManager.get_account(account_id)
        if not account or account['customer_id'] != current_user.id:
            flash('Invalid account!', 'error')
            return redirect(url_for('transactions'))
        
        TransactionManager.withdraw(account_id, amount, description)
        flash('Withdrawal successful!', 'success')
    except Exception as e:
        flash(f'Withdrawal error: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/transfer', methods=['POST'])
@login_required
def transfer():
    """Process transfer"""
    from_account_id = int(request.form['from_account_id'])
    to_account_number = request.form['to_account_number']
    amount = float(request.form['amount'])
    description = request.form.get('description', '')
    
    try:
        # Verify from account belongs to user
        from_account = AccountManager.get_account(from_account_id)
        if not from_account or from_account['customer_id'] != current_user.id:
            flash('Invalid source account!', 'error')
            return redirect(url_for('transactions'))
        
        # Find destination account
        to_account = AccountManager.get_account_by_number(to_account_number)
        if not to_account:
            flash('Destination account not found!', 'error')
            return redirect(url_for('transactions'))
        
        TransactionManager.transfer(from_account_id, to_account['account_id'], 
                                  amount, description)
        flash('Transfer successful!', 'success')
    except Exception as e:
        flash(f'Transfer error: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/account/<int:account_id>')
@login_required
def account_details(account_id):
    """Account details page"""
    try:
        account = AccountManager.get_account(account_id)
        if not account or account['customer_id'] != current_user.id:
            flash('Account not found!', 'error')
            return redirect(url_for('accounts'))
        
        transactions = TransactionManager.get_transaction_history(account_id, 50)
        transfers = TransactionManager.get_transfer_history(account_id, 20)
        
        return render_template('account_details.html', 
                             account=account,
                             transactions=transactions,
                             transfers=transfers)
    except Exception as e:
        flash(f'Error loading account details: {str(e)}', 'error')
        return redirect(url_for('accounts'))

@app.route('/api/balance/<int:account_id>')
@login_required
def api_balance(account_id):
    """API endpoint for account balance"""
    try:
        account = AccountManager.get_account(account_id)
        if not account or account['customer_id'] != current_user.id:
            return jsonify({'error': 'Account not found'}), 404
        
        balance = AccountManager.get_balance(account_id)
        return jsonify({'balance': balance, 'account_number': account['account_number']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:account_id>')
@login_required
def api_transactions(account_id):
    """API endpoint for transaction history"""
    try:
        account = AccountManager.get_account(account_id)
        if not account or account['customer_id'] != current_user.id:
            return jsonify({'error': 'Account not found'}), 404
        
        limit = request.args.get('limit', 10, type=int)
        transactions = TransactionManager.get_transaction_history(account_id, limit)
        return jsonify({'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
