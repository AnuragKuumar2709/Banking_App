"""
Load Sample Data Script
Populates the database with sample customers, accounts, and transactions
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from account_manager import AccountManager
from transaction_manager import TransactionManager


def load_sample_data():
    """Load sample data into the database"""
    print("Loading sample data...")
    print("-" * 60)
    
    try:
        # Create sample customers
        print("\n1. Creating sample customers...")
        
        customer1_id = AccountManager.create_customer(
            "John", "Doe", "john.doe@email.com",
            phone="+1-555-0101",
            address="123 Main St, New York, NY 10001",
            date_of_birth="1985-06-15"
        )
        
        customer2_id = AccountManager.create_customer(
            "Jane", "Smith", "jane.smith@email.com",
            phone="+1-555-0102",
            address="456 Oak Ave, Los Angeles, CA 90001",
            date_of_birth="1990-03-22"
        )
        
        customer3_id = AccountManager.create_customer(
            "Robert", "Johnson", "robert.j@email.com",
            phone="+1-555-0103",
            address="789 Elm St, Chicago, IL 60601",
            date_of_birth="1978-11-08"
        )
        
        print(f"\n+ Created 3 customers (IDs: {customer1_id}, {customer2_id}, {customer3_id})")
        
        # Create sample accounts
        print("\n2. Creating sample accounts...")
        
        account1 = AccountManager.create_account(customer1_id, "SAVINGS", 5000.00)
        account2 = AccountManager.create_account(customer1_id, "CHECKING", 1500.00)
        account3 = AccountManager.create_account(customer2_id, "SAVINGS", 10000.00)
        account4 = AccountManager.create_account(customer2_id, "BUSINESS", 25000.00)
        account5 = AccountManager.create_account(customer3_id, "CHECKING", 3000.00)
        
        print(f"\n+ Created 5 accounts")
        
        # Perform sample transactions
        print("\n3. Performing sample transactions...")
        
        # Deposits
        TransactionManager.deposit(account1['account_id'], 1000.00, "Monthly salary")
        TransactionManager.deposit(account3['account_id'], 5000.00, "Bonus payment")
        TransactionManager.deposit(account5['account_id'], 500.00, "Freelance income")
        
        # Withdrawals
        TransactionManager.withdraw(account2['account_id'], 200.00, "ATM withdrawal")
        TransactionManager.withdraw(account4['account_id'], 1000.00, "Business expense")
        
        print(f"\n+ Completed 5 transactions")
        
        # Perform sample transfers
        print("\n4. Performing sample transfers...")
        
        TransactionManager.transfer(
            account1['account_id'], 
            account2['account_id'], 
            500.00, 
            "Transfer to checking"
        )
        
        TransactionManager.transfer(
            account3['account_id'], 
            account5['account_id'], 
            2000.00, 
            "Loan to friend"
        )
        
        print(f"\n+ Completed 2 transfers")
        
        # Print summary
        print("\n" + "=" * 60)
        print("SAMPLE DATA SUMMARY")
        print("=" * 60)
        
        print("\nCustomers:")
        print(f"  1. John Doe (ID: {customer1_id})")
        print(f"     - Savings: ₹{AccountManager.get_balance(account1['account_id']):.2f}")
        print(f"     - Checking: ₹{AccountManager.get_balance(account2['account_id']):.2f}")
        
        print(f"\n  2. Jane Smith (ID: {customer2_id})")
        print(f"     - Savings: ₹{AccountManager.get_balance(account3['account_id']):.2f}")
        print(f"     - Business: ₹{AccountManager.get_balance(account4['account_id']):.2f}")
        
        print(f"\n  3. Robert Johnson (ID: {customer3_id})")
        print(f"     - Checking: ₹{AccountManager.get_balance(account5['account_id']):.2f}")
        
        print("\n" + "=" * 60)
        print("Sample data loaded successfully!")
        print("You can now run 'python src/main.py' to interact with the system.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n- Error loading sample data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ONLINE BANKING SYSTEM - SAMPLE DATA LOADER")
    print("=" * 60)
    
    # Auto-confirm for automated execution
    confirm = 'yes'
    if confirm.lower() == 'yes':
        load_sample_data()
    else:
        print("Operation cancelled.")
