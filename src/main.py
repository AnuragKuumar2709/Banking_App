"""
Online Banking System - Main Application
Command-line interface for banking operations
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager
from transaction_manager import TransactionManager
from db_connection import db

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_menu():
    """Display main menu"""
    print_header("ONLINE BANKING SYSTEM")
    print("\n1.  Customer Management")
    print("2.  Account Management")
    print("3.  Transactions")
    print("4.  Transfers")
    print("5.  View Account Details")
    print("6.  Transaction History")
    print("0.  Exit")
    print("-" * 60)


def customer_menu():
    """Customer management submenu"""
    while True:
        print_header("Customer Management")
        print("\n1. Create New Customer")
        print("2. View Customer Details")
        print("3. Update Customer Info")
        print("0. Back to Main Menu")
        print("-" * 60)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            create_customer()
        elif choice == '2':
            view_customer()
        elif choice == '3':
            update_customer()
        elif choice == '0':
            break
        else:
            print("Invalid choice!")


def create_customer():
    """Create a new customer"""
    print("\n--- Create New Customer ---")
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone (optional): ").strip() or None
    address = input("Address (optional): ").strip() or None
    dob = input("Date of Birth YYYY-MM-DD (optional): ").strip() or None
    
    try:
        customer_id = AccountManager.create_customer(
            first_name, last_name, email, phone, address, dob
        )
        print(f"\n✓ Customer created with ID: {customer_id}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def view_customer():
    """View customer details"""
    print("\n--- View Customer ---")
    customer_id = input("Customer ID: ").strip()
    
    try:
        customer = AccountManager.get_customer(int(customer_id))
        if customer:
            print("\nCustomer Details:")
            for key, value in customer.items():
                print(f"  {key}: {value}")
            
            # Show customer accounts
            accounts = AccountManager.get_customer_accounts(int(customer_id))
            if accounts:
                print(f"\n{len(accounts)} account(s) found:")
                for acc in accounts:
                    print(f"  - {acc['account_number']} ({acc['account_type']}): ₹{acc['balance']:.2f}")
        else:
            print("Customer not found!")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def update_customer():
    """Update customer information"""
    print("\n--- Update Customer ---")
    customer_id = input("Customer ID: ").strip()
    
    try:
        customer = AccountManager.get_customer(int(customer_id))
        if not customer:
            print("Customer not found!")
            return
        
        print("\nLeave blank to keep current value:")
        updates = {}
        
        email = input(f"Email [{customer['email']}]: ").strip()
        if email:
            updates['email'] = email
        
        phone = input(f"Phone [{customer['phone']}]: ").strip()
        if phone:
            updates['phone'] = phone
        
        if updates:
            AccountManager.update_customer(int(customer_id), **updates)
        else:
            print("No changes made.")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def account_menu():
    """Account management submenu"""
    while True:
        print_header("Account Management")
        print("\n1. Create New Account")
        print("2. View Account Balance")
        print("3. Close Account")
        print("0. Back to Main Menu")
        print("-" * 60)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            create_account()
        elif choice == '2':
            view_balance()
        elif choice == '3':
            close_account()
        elif choice == '0':
            break
        else:
            print("Invalid choice!")


def create_account():
    """Create a new account"""
    print("\n--- Create New Account ---")
    customer_id = input("Customer ID: ").strip()
    
    print("\nAccount Types:")
    print("1. SAVINGS")
    print("2. CHECKING")
    print("3. BUSINESS")
    account_type_choice = input("Select type (1-3): ").strip()
    
    account_types = {'1': 'SAVINGS', '2': 'CHECKING', '3': 'BUSINESS'}
    account_type = account_types.get(account_type_choice)
    
    if not account_type:
        print("Invalid account type!")
        return
    
    initial_balance = input("Initial Balance (default 0): ").strip() or "0"
    
    try:
        account = AccountManager.create_account(
            int(customer_id), account_type, float(initial_balance)
        )
        print(f"\n✓ Account created successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def view_balance():
    """View account balance"""
    print("\n--- View Balance ---")
    account_id = input("Account ID: ").strip()
    
    try:
        balance = AccountManager.get_balance(int(account_id))
        account = AccountManager.get_account(int(account_id))
        print(f"\nAccount: {account['account_number']}")
        print(f"Type: {account['account_type']}")
        print(f"Status: {account['status']}")
        print(f"Current Balance: ₹{balance:.2f}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def close_account():
    """Close an account"""
    print("\n--- Close Account ---")
    account_id = input("Account ID: ").strip()
    
    confirm = input("Are you sure? Account must have zero balance (yes/no): ").strip().lower()
    if confirm == 'yes':
        try:
            AccountManager.close_account(int(account_id))
        except Exception as e:
            print(f"\n✗ Error: {e}")


def transaction_menu():
    """Transaction submenu"""
    while True:
        print_header("Transactions")
        print("\n1. Deposit")
        print("2. Withdraw")
        print("0. Back to Main Menu")
        print("-" * 60)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            deposit()
        elif choice == '2':
            withdraw()
        elif choice == '0':
            break
        else:
            print("Invalid choice!")


def deposit():
    """Make a deposit"""
    print("\n--- Deposit ---")
    account_id = input("Account ID: ").strip()
    amount = input("Amount: ").strip()
    description = input("Description (optional): ").strip()
    
    try:
        TransactionManager.deposit(int(account_id), float(amount), description)
    except Exception as e:
        print(f"\n✗ Error: {e}")


def withdraw():
    """Make a withdrawal"""
    print("\n--- Withdraw ---")
    account_id = input("Account ID: ").strip()
    amount = input("Amount: ").strip()
    description = input("Description (optional): ").strip()
    
    try:
        TransactionManager.withdraw(int(account_id), float(amount), description)
    except Exception as e:
        print(f"\n✗ Error: {e}")


def transfer_money():
    """Transfer money between accounts"""
    print("\n--- Transfer Funds ---")
    from_account = input("From Account ID: ").strip()
    to_account = input("To Account ID: ").strip()
    amount = input("Amount: ").strip()
    description = input("Description (optional): ").strip()
    
    try:
        TransactionManager.transfer(
            int(from_account), int(to_account), float(amount), description
        )
    except Exception as e:
        print(f"\n✗ Error: {e}")


def view_account_details():
    """View comprehensive account details"""
    print("\n--- Account Details ---")
    account_id = input("Account ID: ").strip()
    
    try:
        account = AccountManager.get_account(int(account_id))
        if not account:
            print("Account not found!")
            return
        
        customer = AccountManager.get_customer(account['customer_id'])
        
        print("\n--- Account Information ---")
        print(f"Account Number: {account['account_number']}")
        print(f"Account Type: {account['account_type']}")
        print(f"Status: {account['status']}")
        print(f"Balance: ₹{account['balance']:.2f}")
        print(f"Currency: {account['currency']}")
        print(f"Created: {account['created_at']}")
        
        print("\n--- Customer Information ---")
        print(f"Name: {customer['first_name']} {customer['last_name']}")
        print(f"Email: {customer['email']}")
        if customer['phone']:
            print(f"Phone: {customer['phone']}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def view_transaction_history():
    """View transaction history"""
    print("\n--- Transaction History ---")
    account_id = input("Account ID: ").strip()
    limit = input("Number of transactions (default 10): ").strip() or "10"
    
    try:
        transactions = TransactionManager.get_transaction_history(
            int(account_id), int(limit)
        )
        
        if not transactions:
            print("\nNo transactions found.")
            return
        
        print(f"\n{len(transactions)} transaction(s) found:")
        for txn in transactions:
            print(f"\nID: {txn['transaction_id']}")
            print(f"Type: {txn['transaction_type']}")
            print(f"Amount: ₹{txn['amount']:.2f}")
            print(f"Balance After: ₹{txn['balance_after']:.2f}")
            print(f"Date: {txn['transaction_date']}")
            if txn['description']:
                print(f"Description: {txn['description']}")
            print("-" * 40)
    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """Main application loop"""
    print("\nWelcome to Online Banking System!")
    print("Initializing database...")
    
    # Database is automatically initialized via db_connection module
    
    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            customer_menu()
        elif choice == '2':
            account_menu()
        elif choice == '3':
            transaction_menu()
        elif choice == '4':
            transfer_money()
        elif choice == '5':
            view_account_details()
        elif choice == '6':
            view_transaction_history()
        elif choice == '0':
            print("\nThank you for using Online Banking System!")
            sys.exit(0)
        else:
            print("\n✗ Invalid choice! Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye!")
        sys.exit(0)
