"""
Online Banking System - REST API
Comprehensive API endpoints for external integrations
"""

from flask import Flask, request, jsonify, g
from flask_restful import Api, Resource, reqparse
from functools import wraps
import jwt
import datetime
import os
import sys
from typing import Dict, List, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager
from transaction_manager import TransactionManager
from db_connection import db

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'api-secret-key-change-in-production')
api = Api(app)

# API Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return {'message': 'Token is missing!'}, 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return {'message': 'Token is invalid!'}, 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# API Resources
class CustomerAPI(Resource):
    """Customer management API endpoints"""
    
    @token_required
    def get(self, current_user_id, customer_id=None):
        """Get customer information"""
        try:
            if customer_id and customer_id != current_user_id:
                return {'error': 'Unauthorized access'}, 403
            
            customer = AccountManager.get_customer(current_user_id)
            if not customer:
                return {'error': 'Customer not found'}, 404
            
            # Remove sensitive information
            customer_data = {
                'customer_id': customer['customer_id'],
                'first_name': customer['first_name'],
                'last_name': customer['last_name'],
                'email': customer['email'],
                'phone': customer['phone'],
                'address': customer['address'],
                'date_of_birth': customer['date_of_birth'],
                'created_at': customer['created_at']
            }
            
            return {'customer': customer_data}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    def post(self):
        """Create new customer"""
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', required=True, help='First name is required')
        parser.add_argument('last_name', required=True, help='Last name is required')
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('phone')
        parser.add_argument('address')
        parser.add_argument('date_of_birth')
        
        args = parser.parse_args()
        
        try:
            customer_id = AccountManager.create_customer(
                args['first_name'], args['last_name'], args['email'],
                args['phone'], args['address'], args['date_of_birth']
            )
            
            # Generate JWT token for new customer
            token = jwt.encode({
                'user_id': customer_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return {
                'message': 'Customer created successfully',
                'customer_id': customer_id,
                'token': token
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 400

class AccountAPI(Resource):
    """Account management API endpoints"""
    
    @token_required
    def get(self, current_user_id, account_id=None):
        """Get account information"""
        try:
            if account_id:
                # Get specific account
                account = AccountManager.get_account(account_id)
                if not account or account['customer_id'] != current_user_id:
                    return {'error': 'Account not found or unauthorized'}, 404
                
                return {'account': account}, 200
            else:
                # Get all customer accounts
                accounts = AccountManager.get_customer_accounts(current_user_id)
                return {'accounts': accounts}, 200
                
        except Exception as e:
            return {'error': str(e)}, 500
    
    @token_required
    def post(self, current_user_id):
        """Create new account"""
        parser = reqparse.RequestParser()
        parser.add_argument('account_type', required=True, help='Account type is required')
        parser.add_argument('initial_balance', type=float, default=0.0)
        
        args = parser.parse_args()
        
        try:
            account = AccountManager.create_account(
                current_user_id, args['account_type'], args['initial_balance']
            )
            
            return {
                'message': 'Account created successfully',
                'account': account
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 400

class TransactionAPI(Resource):
    """Transaction management API endpoints"""
    
    @token_required
    def get(self, current_user_id, account_id):
        """Get transaction history for an account"""
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=10)
        parser.add_argument('start_date')
        parser.add_argument('end_date')
        
        args = parser.parse_args()
        
        try:
            # Verify account belongs to user
            account = AccountManager.get_account(account_id)
            if not account or account['customer_id'] != current_user_id:
                return {'error': 'Account not found or unauthorized'}, 404
            
            if args['start_date'] and args['end_date']:
                statement = TransactionManager.get_account_statement(
                    account_id, args['start_date'], args['end_date']
                )
                transactions = statement['transactions']
            else:
                transactions = TransactionManager.get_transaction_history(
                    account_id, args['limit']
                )
            
            return {'transactions': transactions}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @token_required
    def post(self, current_user_id):
        """Create new transaction (deposit/withdrawal)"""
        parser = reqparse.RequestParser()
        parser.add_argument('account_id', type=int, required=True, help='Account ID is required')
        parser.add_argument('transaction_type', required=True, help='Transaction type is required')
        parser.add_argument('amount', type=float, required=True, help='Amount is required')
        parser.add_argument('description')
        
        args = parser.parse_args()
        
        try:
            # Verify account belongs to user
            account = AccountManager.get_account(args['account_id'])
            if not account or account['customer_id'] != current_user_id:
                return {'error': 'Account not found or unauthorized'}, 404
            
            if args['transaction_type'].upper() == 'DEPOSIT':
                result = TransactionManager.deposit(
                    args['account_id'], args['amount'], args['description']
                )
            elif args['transaction_type'].upper() == 'WITHDRAWAL':
                result = TransactionManager.withdraw(
                    args['account_id'], args['amount'], args['description']
                )
            else:
                return {'error': 'Invalid transaction type'}, 400
            
            return {
                'message': 'Transaction completed successfully',
                'transaction': result
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 400

class TransferAPI(Resource):
    """Transfer management API endpoints"""
    
    @token_required
    def get(self, current_user_id, account_id):
        """Get transfer history for an account"""
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=10)
        
        args = parser.parse_args()
        
        try:
            # Verify account belongs to user
            account = AccountManager.get_account(account_id)
            if not account or account['customer_id'] != current_user_id:
                return {'error': 'Account not found or unauthorized'}, 404
            
            transfers = TransactionManager.get_transfer_history(account_id, args['limit'])
            return {'transfers': transfers}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @token_required
    def post(self, current_user_id):
        """Create new transfer"""
        parser = reqparse.RequestParser()
        parser.add_argument('from_account_id', type=int, required=True, help='From account ID is required')
        parser.add_argument('to_account_number', required=True, help='To account number is required')
        parser.add_argument('amount', type=float, required=True, help='Amount is required')
        parser.add_argument('description')
        
        args = parser.parse_args()
        
        try:
            # Verify from account belongs to user
            from_account = AccountManager.get_account(args['from_account_id'])
            if not from_account or from_account['customer_id'] != current_user_id:
                return {'error': 'Source account not found or unauthorized'}, 404
            
            # Find destination account
            to_account = AccountManager.get_account_by_number(args['to_account_number'])
            if not to_account:
                return {'error': 'Destination account not found'}, 404
            
            result = TransactionManager.transfer(
                args['from_account_id'], to_account['account_id'],
                args['amount'], args['description']
            )
            
            return {
                'message': 'Transfer completed successfully',
                'transfer': result
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 400

class BalanceAPI(Resource):
    """Balance inquiry API endpoints"""
    
    @token_required
    def get(self, current_user_id, account_id):
        """Get account balance"""
        try:
            # Verify account belongs to user
            account = AccountManager.get_account(account_id)
            if not account or account['customer_id'] != current_user_id:
                return {'error': 'Account not found or unauthorized'}, 404
            
            balance = AccountManager.get_balance(account_id)
            
            return {
                'account_id': account_id,
                'account_number': account['account_number'],
                'balance': balance,
                'currency': account['currency'],
                'status': account['status']
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class StatementAPI(Resource):
    """Account statement API endpoints"""
    
    @token_required
    def get(self, current_user_id, account_id):
        """Get account statement"""
        parser = reqparse.RequestParser()
        parser.add_argument('start_date')
        parser.add_argument('end_date')
        
        args = parser.parse_args()
        
        try:
            # Verify account belongs to user
            account = AccountManager.get_account(account_id)
            if not account or account['customer_id'] != current_user_id:
                return {'error': 'Account not found or unauthorized'}, 404
            
            statement = TransactionManager.get_account_statement(
                account_id, args['start_date'], args['end_date']
            )
            
            return {'statement': statement}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class LoginAPI(Resource):
    """Authentication API endpoints"""
    
    def post(self):
        """Login and get JWT token"""
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        
        args = parser.parse_args()
        
        try:
            # Find customer by email
            query = "SELECT * FROM customers WHERE email = ?"
            result = db.execute_query(query, (args['email'],))
            
            if result and len(result) > 0:
                customer = dict(result[0])
                # Simple password check (email as password for demo)
                if args['password'] == args['email'].split('@')[0]:
                    token = jwt.encode({
                        'user_id': customer['customer_id'],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                    }, app.config['SECRET_KEY'], algorithm='HS256')
                    
                    return {
                        'message': 'Login successful',
                        'token': token,
                        'customer_id': customer['customer_id']
                    }, 200
                else:
                    return {'error': 'Invalid password'}, 401
            else:
                return {'error': 'User not found'}, 404
                
        except Exception as e:
            return {'error': str(e)}, 500

# API Routes
api.add_resource(CustomerAPI, '/api/customers', '/api/customers/<int:customer_id>')
api.add_resource(AccountAPI, '/api/accounts', '/api/accounts/<int:account_id>')
api.add_resource(TransactionAPI, '/api/transactions/<int:account_id>', '/api/transactions')
api.add_resource(TransferAPI, '/api/transfers/<int:account_id>', '/api/transfers')
api.add_resource(BalanceAPI, '/api/balance/<int:account_id>')
api.add_resource(StatementAPI, '/api/statement/<int:account_id>')
api.add_resource(LoginAPI, '/api/login')

# API Documentation endpoint
@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    docs = {
        'title': 'Online Banking System API',
        'version': '1.0.0',
        'description': 'RESTful API for banking operations',
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer <token>',
            'login_endpoint': '/api/login'
        },
        'endpoints': {
            'customers': {
                'GET /api/customers': 'Get current user info',
                'GET /api/customers/{id}': 'Get specific customer info',
                'POST /api/customers': 'Create new customer'
            },
            'accounts': {
                'GET /api/accounts': 'Get user accounts',
                'GET /api/accounts/{id}': 'Get specific account',
                'POST /api/accounts': 'Create new account'
            },
            'transactions': {
                'GET /api/transactions/{account_id}': 'Get transaction history',
                'POST /api/transactions': 'Create transaction (deposit/withdrawal)'
            },
            'transfers': {
                'GET /api/transfers/{account_id}': 'Get transfer history',
                'POST /api/transfers': 'Create transfer between accounts'
            },
            'balance': {
                'GET /api/balance/{account_id}': 'Get account balance'
            },
            'statements': {
                'GET /api/statement/{account_id}': 'Get account statement'
            }
        },
        'example_requests': {
            'login': {
                'method': 'POST',
                'url': '/api/login',
                'body': {
                    'email': 'user@example.com',
                    'password': 'user'
                }
            },
            'create_account': {
                'method': 'POST',
                'url': '/api/accounts',
                'headers': {
                    'Authorization': 'Bearer <token>'
                },
                'body': {
                    'account_type': 'SAVINGS',
                    'initial_balance': 1000.00
                }
            },
            'deposit': {
                'method': 'POST',
                'url': '/api/transactions',
                'headers': {
                    'Authorization': 'Bearer <token>'
                },
                'body': {
                    'account_id': 1,
                    'transaction_type': 'DEPOSIT',
                    'amount': 500.00,
                    'description': 'Salary deposit'
                }
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
