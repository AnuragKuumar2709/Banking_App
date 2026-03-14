# Database Design Documentation

## Overview
The Online Banking System uses a relational database to manage customers, accounts, transactions, and transfers. The design follows normalization principles and ensures data integrity through constraints and triggers.

## Database Schema

### Tables

#### 1. Customers Table
Stores customer personal information.

**Columns:**
- `customer_id` (INTEGER, PRIMARY KEY): Auto-incrementing unique identifier
- `first_name` (VARCHAR(50), NOT NULL): Customer's first name
- `last_name` (VARCHAR(50), NOT NULL): Customer's last name
- `email` (VARCHAR(100), UNIQUE, NOT NULL): Customer's email address
- `phone` (VARCHAR(20)): Contact phone number
- `address` (TEXT): Physical address
- `date_of_birth` (DATE): Date of birth
- `created_at` (TIMESTAMP): Record creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Constraints:**
- Email must be unique
- Trigger updates `updated_at` on modifications

#### 2. Accounts Table
Stores bank account information for customers.

**Columns:**
- `account_id` (INTEGER, PRIMARY KEY): Auto-incrementing unique identifier
- `customer_id` (INTEGER, FOREIGN KEY, NOT NULL): References customers table
- `account_number` (VARCHAR(20), UNIQUE, NOT NULL): Unique account number
- `account_type` (VARCHAR(20), NOT NULL): SAVINGS, CHECKING, or BUSINESS
- `balance` (DECIMAL(15,2), DEFAULT 0.00): Current account balance
- `currency` (VARCHAR(3), DEFAULT 'USD'): Currency code
- `status` (VARCHAR(20), DEFAULT 'ACTIVE'): ACTIVE, INACTIVE, CLOSED, or FROZEN
- `created_at` (TIMESTAMP): Record creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Constraints:**
- Balance must be >= 0
- Account type must be SAVINGS, CHECKING, or BUSINESS
- Status must be ACTIVE, INACTIVE, CLOSED, or FROZEN
- Foreign key to customers with CASCADE delete
- Trigger updates `updated_at` on modifications

#### 3. Transactions Table
Records all deposits and withdrawals.

**Columns:**
- `transaction_id` (INTEGER, PRIMARY KEY): Auto-incrementing unique identifier
- `account_id` (INTEGER, FOREIGN KEY, NOT NULL): References accounts table
- `transaction_type` (VARCHAR(20), NOT NULL): DEPOSIT or WITHDRAWAL
- `amount` (DECIMAL(15,2), NOT NULL): Transaction amount (must be positive)
- `balance_after` (DECIMAL(15,2), NOT NULL): Account balance after transaction
- `description` (TEXT): Optional transaction description
- `transaction_date` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Transaction timestamp

**Constraints:**
- Amount must be > 0
- Transaction type must be DEPOSIT or WITHDRAWAL
- Foreign key to accounts with CASCADE delete

#### 4. Transfers Table
Records transfers between accounts.

**Columns:**
- `transfer_id` (INTEGER, PRIMARY KEY): Auto-incrementing unique identifier
- `from_account_id` (INTEGER, FOREIGN KEY, NOT NULL): Source account
- `to_account_id` (INTEGER, FOREIGN KEY, NOT NULL): Destination account
- `amount` (DECIMAL(15,2), NOT NULL): Transfer amount (must be positive)
- `description` (TEXT): Optional transfer description
- `status` (VARCHAR(20), DEFAULT 'COMPLETED'): PENDING, COMPLETED, FAILED, or CANCELLED
- `transfer_date` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Transfer timestamp

**Constraints:**
- Amount must be > 0
- Source and destination accounts must be different
- Status must be PENDING, COMPLETED, FAILED, or CANCELLED
- Foreign keys to accounts with CASCADE delete

## Indexes

For optimized query performance:

- `idx_customers_email` on customers(email)
- `idx_accounts_customer` on accounts(customer_id)
- `idx_accounts_number` on accounts(account_number)
- `idx_transactions_account` on transactions(account_id)
- `idx_transactions_date` on transactions(transaction_date)
- `idx_transfers_from` on transfers(from_account_id)
- `idx_transfers_to` on transfers(to_account_id)
- `idx_transfers_date` on transfers(transfer_date)

## Triggers

### Update Timestamp Triggers
- `update_customer_timestamp`: Automatically updates `updated_at` when customer records are modified
- `update_account_timestamp`: Automatically updates `updated_at` when account records are modified

## Relationships

```
customers (1) ----< (N) accounts
accounts (1) ----< (N) transactions
accounts (1) ----< (N) transfers (as from_account)
accounts (1) ----< (N) transfers (as to_account)
```

## ACID Compliance

The system ensures ACID properties:

- **Atomicity**: All transactions use database transactions to ensure all-or-nothing execution
- **Consistency**: Constraints ensure data validity (e.g., positive balances, valid account types)
- **Isolation**: SQLite's transaction isolation prevents concurrent modification issues
- **Durability**: Committed transactions are persisted to disk

## Transaction Integrity

### Deposits and Withdrawals
1. Verify account exists and is active
2. Check sufficient funds (withdrawals only)
3. Update account balance
4. Record transaction with balance_after
5. Commit atomically

### Transfers
1. Verify both accounts exist and are active
2. Check sufficient funds in source account
3. Deduct from source account
4. Add to destination account
5. Record transfer
6. Record transactions for both accounts
7. Commit all changes atomically or rollback on failure

## Data Validation

### Application Level
- Email format validation
- Amount must be positive
- Account types restricted to predefined values
- Status values restricted to predefined values

### Database Level
- CHECK constraints on amounts
- CHECK constraints on status/type enumerations
- UNIQUE constraints on emails and account numbers
- FOREIGN KEY constraints for referential integrity
- NOT NULL constraints on required fields

## Security Considerations

1. **Data Integrity**: Foreign keys prevent orphaned records
2. **Balance Protection**: CHECK constraint ensures non-negative balances
3. **Transaction Atomicity**: Database transactions prevent partial updates
4. **Audit Trail**: All transactions and transfers are permanently logged with timestamps

## Future Enhancements

Potential improvements:
- Add authentication/authorization tables for users
- Implement account interest rates table
- Add transaction fees configuration
- Include audit logs for all modifications
- Add scheduled transfers table
- Implement account statements generation
- Add support for multiple currencies with exchange rates
