"""
Account Management Module
Handles customer and account operations
"""

import random
from datetime import datetime
from typing import Optional, List, Dict
from db_connection import db


class AccountManager:
    """Manages customer accounts and related operations"""
    
    @staticmethod
    def generate_account_number() -> str:
        """Generate a unique account number"""
        # Format: XXXX-XXXX-XXXX (12 digits)
        return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    @staticmethod
    def create_customer(first_name: str, last_name: str, email: str, 
                       phone: Optional[str] = None, address: Optional[str] = None,
                       date_of_birth: Optional[str] = None) -> int:
        """
        Create a new customer
        
        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            email: Customer's email (must be unique)
            phone: Customer's phone number
            address: Customer's address
            date_of_birth: Date of birth (YYYY-MM-DD format)
            
        Returns:
            Customer ID
            
        Raises:
            Exception if email already exists
        """
        query = """
            INSERT INTO customers (first_name, last_name, email, phone, address, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            customer_id = db.execute_insert(query, (first_name, last_name, email, phone, address, date_of_birth))
            print(f"Customer created successfully. ID: {customer_id}")
            return customer_id
        except Exception as e:
            raise Exception(f"Failed to create customer: {str(e)}")
    
    @staticmethod
    def create_account(customer_id: int, account_type: str, 
                      initial_balance: float = 0.0) -> Dict:
        """
        Create a new account for a customer
        
        Args:
            customer_id: ID of the customer
            account_type: Type of account (SAVINGS, CHECKING, BUSINESS)
            initial_balance: Initial deposit amount
            
        Returns:
            Dictionary with account details
            
        Raises:
            Exception if customer doesn't exist or invalid account type
        """
        # Validate account type
        valid_types = ['SAVINGS', 'CHECKING', 'BUSINESS']
        if account_type.upper() not in valid_types:
            raise ValueError(f"Invalid account type. Must be one of: {valid_types}")
        
        # Verify customer exists
        customer_query = "SELECT customer_id FROM customers WHERE customer_id = ?"
        customer = db.execute_query(customer_query, (customer_id,))
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} does not exist")
        
        # Generate unique account number
        account_number = AccountManager.generate_account_number()
        
        # Create account
        query = """
            INSERT INTO accounts (customer_id, account_number, account_type, balance)
            VALUES (?, ?, ?, ?)
        """
        try:
            account_id = db.execute_insert(query, (customer_id, account_number, 
                                                   account_type.upper(), initial_balance))
            
            print(f"Account created successfully.")
            print(f"  Account Number: {account_number}")
            print(f"  Account Type: {account_type.upper()}")
            print(f"  Initial Balance: ₹{initial_balance:.2f}")
            
            return {
                'account_id': account_id,
                'account_number': account_number,
                'account_type': account_type.upper(),
                'balance': initial_balance
            }
        except Exception as e:
            raise Exception(f"Failed to create account: {str(e)}")
    
    @staticmethod
    def get_customer(customer_id: int) -> Optional[Dict]:
        """Get customer details by ID"""
        query = "SELECT * FROM customers WHERE customer_id = ?"
        result = db.execute_query(query, (customer_id,))
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def get_account(account_id: int) -> Optional[Dict]:
        """Get account details by account ID"""
        query = "SELECT * FROM accounts WHERE account_id = ?"
        result = db.execute_query(query, (account_id,))
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def get_account_by_number(account_number: str) -> Optional[Dict]:
        """Get account details by account number"""
        query = "SELECT * FROM accounts WHERE account_number = ?"
        result = db.execute_query(query, (account_number,))
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def get_customer_accounts(customer_id: int) -> List[Dict]:
        """Get all accounts for a customer"""
        query = """
            SELECT * FROM accounts 
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """
        results = db.execute_query(query, (customer_id,))
        return [dict(row) for row in results]
    
    @staticmethod
    def get_balance(account_id: int) -> float:
        """Get current balance for an account"""
        query = "SELECT balance FROM accounts WHERE account_id = ?"
        result = db.execute_query(query, (account_id,))
        if result:
            return float(result[0]['balance'])
        raise ValueError(f"Account with ID {account_id} does not exist")
    
    @staticmethod
    def update_customer(customer_id: int, **kwargs) -> bool:
        """
        Update customer information
        
        Args:
            customer_id: Customer ID
            **kwargs: Fields to update (first_name, last_name, email, phone, address)
            
        Returns:
            True if successful
        """
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            raise ValueError("No valid fields to update")
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE customers SET {set_clause} WHERE customer_id = ?"
        
        values = list(updates.values()) + [customer_id]
        rows_affected = db.execute_update(query, tuple(values))
        
        if rows_affected > 0:
            print(f"Customer {customer_id} updated successfully")
            return True
        return False
    
    @staticmethod
    def close_account(account_id: int) -> bool:
        """
        Close an account (set status to CLOSED)
        Account must have zero balance
        """
        account = AccountManager.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if float(account['balance']) != 0:
            raise ValueError("Cannot close account with non-zero balance")
        
        query = "UPDATE accounts SET status = 'CLOSED' WHERE account_id = ?"
        rows_affected = db.execute_update(query, (account_id,))
        
        if rows_affected > 0:
            print(f"Account {account_id} closed successfully")
            return True
        return False
