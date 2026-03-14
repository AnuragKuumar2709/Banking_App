-- Online Banking System Database Schema
-- SQLite compatible (can be adapted for PostgreSQL)

-- Enable foreign key support (SQLite specific)
PRAGMA foreign_keys = ON;

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account Types: SAVINGS, CHECKING, BUSINESS
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK(account_type IN ('SAVINGS', 'CHECKING', 'BUSINESS')),
    balance DECIMAL(15, 2) DEFAULT 0.00 CHECK(balance >= 0),
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'INACTIVE', 'CLOSED', 'FROZEN')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Transaction Types: DEPOSIT, WITHDRAWAL
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK(transaction_type IN ('DEPOSIT', 'WITHDRAWAL')),
    amount DECIMAL(15, 2) NOT NULL CHECK(amount > 0),
    balance_after DECIMAL(15, 2) NOT NULL,
    description TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- Transfers between accounts
CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_account_id INTEGER NOT NULL,
    to_account_id INTEGER NOT NULL,
    amount DECIMAL(15, 2) NOT NULL CHECK(amount > 0),
    description TEXT,
    status VARCHAR(20) DEFAULT 'COMPLETED' CHECK(status IN ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (to_account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    CHECK (from_account_id != to_account_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts(account_number);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transfers_from ON transfers(from_account_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to ON transfers(to_account_id);
CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(transfer_date);

-- Trigger to update updated_at timestamp for customers
CREATE TRIGGER IF NOT EXISTS update_customer_timestamp 
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE customer_id = NEW.customer_id;
END;

-- Trigger to update updated_at timestamp for accounts
CREATE TRIGGER IF NOT EXISTS update_account_timestamp 
AFTER UPDATE ON accounts
FOR EACH ROW
BEGIN
    UPDATE accounts SET updated_at = CURRENT_TIMESTAMP WHERE account_id = NEW.account_id;
END;

-- Audit Log Table for tracking all changes
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    operation VARCHAR(20) NOT NULL CHECK(operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values TEXT,
    new_values TEXT,
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- Views for common queries
CREATE VIEW IF NOT EXISTS customer_account_summary AS
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(a.account_id) as total_accounts,
    SUM(a.balance) as total_balance,
    MAX(a.created_at) as last_account_created
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id AND a.status = 'ACTIVE'
GROUP BY c.customer_id, c.first_name, c.last_name, c.email;

CREATE VIEW IF NOT EXISTS transaction_summary AS
SELECT 
    a.account_id,
    a.account_number,
    a.account_type,
    c.first_name || ' ' || c.last_name as customer_name,
    COUNT(t.transaction_id) as total_transactions,
    SUM(CASE WHEN t.transaction_type = 'DEPOSIT' THEN t.amount ELSE 0 END) as total_deposits,
    SUM(CASE WHEN t.transaction_type = 'WITHDRAWAL' THEN t.amount ELSE 0 END) as total_withdrawals,
    MAX(t.transaction_date) as last_transaction_date
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
WHERE a.status = 'ACTIVE'
GROUP BY a.account_id, a.account_number, a.account_type, c.first_name, c.last_name;

CREATE VIEW IF NOT EXISTS monthly_transaction_summary AS
SELECT 
    strftime('%Y-%m', transaction_date) as month,
    transaction_type,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as average_amount
FROM transactions
GROUP BY strftime('%Y-%m', transaction_date), transaction_type
ORDER BY month DESC, transaction_type;

-- Stored Procedures (SQLite doesn't support stored procedures, so we'll create functions)
-- These would be implemented in the application layer

-- Function to calculate account interest (for savings accounts)
-- This would be implemented as a Python function in the application

-- Function to generate account statement
-- This would be implemented as a Python function in the application

-- Function to validate account status before transactions
-- This would be implemented as a Python function in the application

-- Additional constraints and business rules
-- Add check constraint for minimum balance
ALTER TABLE accounts ADD CONSTRAINT check_minimum_balance 
CHECK (balance >= 0 OR account_type = 'CHECKING' AND balance >= -1000);

-- Add constraint for maximum daily transaction amount
-- This would be enforced at the application level

-- Add constraint for account number format
-- This would be enforced at the application level

-- Additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(first_name, last_name);
CREATE INDEX IF NOT EXISTS idx_accounts_type_status ON accounts(account_type, status);
CREATE INDEX IF NOT EXISTS idx_transactions_type_date ON transactions(transaction_type, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transfers_status_date ON transfers(status, transfer_date);

-- Create a view for account balances with customer info
CREATE VIEW IF NOT EXISTS account_balances AS
SELECT 
    a.account_id,
    a.account_number,
    a.account_type,
    a.balance,
    a.currency,
    a.status,
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    a.created_at as account_created,
    a.updated_at as last_updated
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.status IN ('ACTIVE', 'INACTIVE');

-- Create a view for recent transactions with account details
CREATE VIEW IF NOT EXISTS recent_transactions AS
SELECT 
    t.transaction_id,
    t.transaction_type,
    t.amount,
    t.balance_after,
    t.description,
    t.transaction_date,
    a.account_number,
    a.account_type,
    c.first_name || ' ' || c.last_name as customer_name
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
ORDER BY t.transaction_date DESC
LIMIT 100;

-- Create a view for transfer history with account details
CREATE VIEW IF NOT EXISTS transfer_history AS
SELECT 
    tr.transfer_id,
    tr.amount,
    tr.description,
    tr.status,
    tr.transfer_date,
    fa.account_number as from_account,
    ta.account_number as to_account,
    fc.first_name || ' ' || fc.last_name as from_customer,
    tc.first_name || ' ' || tc.last_name as to_customer
FROM transfers tr
JOIN accounts fa ON tr.from_account_id = fa.account_id
JOIN accounts ta ON tr.to_account_id = ta.account_id
JOIN customers fc ON fa.customer_id = fc.customer_id
JOIN customers tc ON ta.customer_id = tc.customer_id
ORDER BY tr.transfer_date DESC;