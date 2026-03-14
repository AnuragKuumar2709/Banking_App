"""
Transaction Management Module
Handles deposits, withdrawals, and transfers
"""

from typing import Dict, List, Optional
from datetime import datetime
from db_connection import db
from account_manager import AccountManager


class TransactionManager:
    """Manages banking transactions and transfers"""
    
    @staticmethod
    def deposit(account_id: int, amount: float, description: str = "") -> Dict:
        """
        Deposit money into an account
        
        Args:
            account_id: Account ID
            amount: Amount to deposit (must be positive)
            description: Optional description
            
        Returns:
            Transaction details
            
        Raises:
            ValueError if amount is invalid or account doesn't exist
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Get current balance
        account = AccountManager.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if account['status'] != 'ACTIVE':
            raise ValueError(f"Account is {account['status']}. Cannot perform transactions.")
        
        current_balance = float(account['balance'])
        new_balance = current_balance + amount
        
        # Use transaction to ensure atomicity
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update account balance
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE account_id = ?",
                (new_balance, account_id)
            )
            
            # Record transaction
            cursor.execute(
                """INSERT INTO transactions 
                   (account_id, transaction_type, amount, balance_after, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (account_id, 'DEPOSIT', amount, new_balance, description)
            )
            
            transaction_id = cursor.lastrowid
            conn.commit()
        
        print(f"Deposit successful!")
        print(f"  Amount: ₹{amount:.2f}")
        print(f"  New Balance: ₹{new_balance:.2f}")
        
        return {
            'transaction_id': transaction_id,
            'account_id': account_id,
            'type': 'DEPOSIT',
            'amount': amount,
            'balance_after': new_balance
        }
    
    @staticmethod
    def withdraw(account_id: int, amount: float, description: str = "") -> Dict:
        """
        Withdraw money from an account
        
        Args:
            account_id: Account ID
            amount: Amount to withdraw (must be positive)
            description: Optional description
            
        Returns:
            Transaction details
            
        Raises:
            ValueError if insufficient funds or invalid amount
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        # Get current balance
        account = AccountManager.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if account['status'] != 'ACTIVE':
            raise ValueError(f"Account is {account['status']}. Cannot perform transactions.")
        
        current_balance = float(account['balance'])
        
        if current_balance < amount:
            raise ValueError(f"Insufficient funds. Current balance: ₹{current_balance:.2f}")
        
        new_balance = current_balance - amount
        
        # Use transaction to ensure atomicity
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update account balance
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE account_id = ?",
                (new_balance, account_id)
            )
            
            # Record transaction
            cursor.execute(
                """INSERT INTO transactions 
                   (account_id, transaction_type, amount, balance_after, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (account_id, 'WITHDRAWAL', amount, new_balance, description)
            )
            
            transaction_id = cursor.lastrowid
            conn.commit()
        
        print(f"Withdrawal successful!")
        print(f"  Amount: ₹{amount:.2f}")
        print(f"  New Balance: ₹{new_balance:.2f}")
        
        return {
            'transaction_id': transaction_id,
            'account_id': account_id,
            'type': 'WITHDRAWAL',
            'amount': amount,
            'balance_after': new_balance
        }
    
    @staticmethod
    def transfer(from_account_id: int, to_account_id: int, amount: float, 
                description: str = "") -> Dict:
        """
        Transfer money between accounts
        
        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Amount to transfer (must be positive)
            description: Optional description
            
        Returns:
            Transfer details
            
        Raises:
            ValueError if accounts are invalid or insufficient funds
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")
        
        # Verify both accounts exist and are active
        from_account = AccountManager.get_account(from_account_id)
        to_account = AccountManager.get_account(to_account_id)
        
        if not from_account:
            raise ValueError(f"Source account {from_account_id} not found")
        if not to_account:
            raise ValueError(f"Destination account {to_account_id} not found")
        
        if from_account['status'] != 'ACTIVE':
            raise ValueError(f"Source account is {from_account['status']}")
        if to_account['status'] != 'ACTIVE':
            raise ValueError(f"Destination account is {to_account['status']}")
        
        from_balance = float(from_account['balance'])
        to_balance = float(to_account['balance'])
        
        if from_balance < amount:
            raise ValueError(f"Insufficient funds. Current balance: ₹{from_balance:.2f}")
        
        new_from_balance = from_balance - amount
        new_to_balance = to_balance + amount
        
        # Use transaction to ensure atomicity (all or nothing)
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Update source account balance
                cursor.execute(
                    "UPDATE accounts SET balance = ? WHERE account_id = ?",
                    (new_from_balance, from_account_id)
                )
                
                # Update destination account balance
                cursor.execute(
                    "UPDATE accounts SET balance = ? WHERE account_id = ?",
                    (new_to_balance, to_account_id)
                )
                
                # Record transfer
                cursor.execute(
                    """INSERT INTO transfers 
                       (from_account_id, to_account_id, amount, description, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (from_account_id, to_account_id, amount, description, 'COMPLETED')
                )
                
                transfer_id = cursor.lastrowid
                
                # Record transactions for both accounts
                cursor.execute(
                    """INSERT INTO transactions 
                       (account_id, transaction_type, amount, balance_after, description)
                       VALUES (?, ?, ?, ?, ?)""",
                    (from_account_id, 'WITHDRAWAL', amount, new_from_balance, 
                     f"Transfer to account {to_account['account_number']}: {description}")
                )
                
                cursor.execute(
                    """INSERT INTO transactions 
                       (account_id, transaction_type, amount, balance_after, description)
                       VALUES (?, ?, ?, ?, ?)""",
                    (to_account_id, 'DEPOSIT', amount, new_to_balance, 
                     f"Transfer from account {from_account['account_number']}: {description}")
                )
                
                conn.commit()
            
            print(f"Transfer successful!")
            print(f"  From Account: {from_account['account_number']}")
            print(f"  To Account: {to_account['account_number']}")
            print(f"  Amount: ₹{amount:.2f}")
            print(f"  New Balance (From): ₹{new_from_balance:.2f}")
            print(f"  New Balance (To): ₹{new_to_balance:.2f}")
            
            return {
                'transfer_id': transfer_id,
                'from_account_id': from_account_id,
                'to_account_id': to_account_id,
                'amount': amount,
                'status': 'COMPLETED'
            }
            
        except Exception as e:
            raise Exception(f"Transfer failed: {str(e)}")
    
    @staticmethod
    def get_transaction_history(account_id: int, limit: int = 10) -> List[Dict]:
        """
        Get transaction history for an account
        
        Args:
            account_id: Account ID
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of transactions
        """
        query = """
            SELECT * FROM transactions
            WHERE account_id = ?
            ORDER BY transaction_date DESC
            LIMIT ?
        """
        results = db.execute_query(query, (account_id, limit))
        return [dict(row) for row in results]
    
    @staticmethod
    def get_transfer_history(account_id: int, limit: int = 10) -> List[Dict]:
        """
        Get transfer history for an account (both sent and received)
        
        Args:
            account_id: Account ID
            limit: Maximum number of transfers to retrieve
            
        Returns:
            List of transfers
        """
        query = """
            SELECT * FROM transfers
            WHERE from_account_id = ? OR to_account_id = ?
            ORDER BY transfer_date DESC
            LIMIT ?
        """
        results = db.execute_query(query, (account_id, account_id, limit))
        return [dict(row) for row in results]
    
    @staticmethod
    def get_account_statement(account_id: int, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> Dict:
        """
        Generate account statement
        
        Args:
            account_id: Account ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            Dictionary with account details and transactions
        """
        account = AccountManager.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Build query based on date filters
        if start_date and end_date:
            query = """
                SELECT * FROM transactions
                WHERE account_id = ? 
                AND DATE(transaction_date) BETWEEN ? AND ?
                ORDER BY transaction_date DESC
            """
            transactions = db.execute_query(query, (account_id, start_date, end_date))
        else:
            transactions = TransactionManager.get_transaction_history(account_id, limit=100)
        
        return {
            'account': account,
            'transactions': [dict(row) for row in transactions],
            'current_balance': float(account['balance'])
        }
