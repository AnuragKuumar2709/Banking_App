# Online Banking System - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation Guide](#installation-guide)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [Web Interface Guide](#web-interface-guide)
7. [Reporting and Analytics](#reporting-and-analytics)
8. [Security Features](#security-features)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)

## Overview

The Online Banking System is a comprehensive database management system designed for managing customer accounts, transactions, balances, and transfers. It provides both a modern web interface and a robust REST API for banking operations.

### Key Features
- **Customer Management**: Complete customer lifecycle management
- **Account Management**: Multiple account types (Savings, Checking, Business)
- **Transaction Processing**: Deposits, withdrawals, and transfers with full audit trail
- **Real-time Balance Tracking**: Live balance updates and history
- **Web Interface**: Modern, responsive web application
- **REST API**: Comprehensive API for external integrations
- **Reporting & Analytics**: Advanced reporting and business intelligence
- **Security**: Authentication, authorization, and audit logging

### Technology Stack
- **Backend**: Python 3.x
- **Web Framework**: Flask
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: JWT tokens
- **API**: RESTful API with Flask-RESTful

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   REST API      │    │   CLI Interface │
│   (Flask)       │    │   (Flask-RESTful)│    │   (main.py)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Business Logic Layer   │
                    │  ┌─────────────────────┐  │
                    │  │  Account Manager    │  │
                    │  │  Transaction Manager│  │
                    │  │  Banking Analytics  │  │
                    │  │  Report Generator   │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Database Layer        │
                    │  ┌─────────────────────┐  │
                    │  │  SQLite Database    │  │
                    │  │  - Customers        │  │
                    │  │  - Accounts         │  │
                    │  │  - Transactions     │  │
                    │  │  - Transfers        │  │
                    │  │  - Audit Log       │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Installation Guide

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd Banking_app

# Or download and extract the project files
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
python src/init_db.py
```

### Step 4: Load Sample Data (Optional)
```bash
python tests/load_sample_data.py
```

### Step 5: Run the Application

#### Web Interface
```bash
python src/web_app.py
```
Access at: http://localhost:5000

#### REST API Server
```bash
python src/api_server.py
```
Access at: http://localhost:5001

#### Command Line Interface
```bash
python src/main.py
```

## Database Schema

### Core Tables

#### Customers Table
```sql
CREATE TABLE customers (
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
```

#### Accounts Table
```sql
CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK(account_type IN ('SAVINGS', 'CHECKING', 'BUSINESS')),
    balance DECIMAL(15, 2) DEFAULT 0.00 CHECK(balance >= 0),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'INACTIVE', 'CLOSED', 'FROZEN')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
```

#### Transactions Table
```sql
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK(transaction_type IN ('DEPOSIT', 'WITHDRAWAL')),
    amount DECIMAL(15, 2) NOT NULL CHECK(amount > 0),
    balance_after DECIMAL(15, 2) NOT NULL,
    description TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);
```

#### Transfers Table
```sql
CREATE TABLE transfers (
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
```

#### Audit Log Table
```sql
CREATE TABLE audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    operation VARCHAR(20) NOT NULL CHECK(operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values TEXT,
    new_values TEXT,
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Views

#### Customer Account Summary
```sql
CREATE VIEW customer_account_summary AS
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
```

#### Transaction Summary
```sql
CREATE VIEW transaction_summary AS
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
```

## API Documentation

### Authentication
All API endpoints require JWT authentication except for login and registration.

**Login to get token:**
```bash
POST /api/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "user"
}
```

**Use token in requests:**
```bash
Authorization: Bearer <your-jwt-token>
```

### Customer Endpoints

#### Get Customer Information
```bash
GET /api/customers/{customer_id}
Authorization: Bearer <token>
```

#### Create New Customer
```bash
POST /api/customers
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "address": "123 Main St",
    "date_of_birth": "1990-01-01"
}
```

### Account Endpoints

#### Get Customer Accounts
```bash
GET /api/accounts
Authorization: Bearer <token>
```

#### Get Specific Account
```bash
GET /api/accounts/{account_id}
Authorization: Bearer <token>
```

#### Create New Account
```bash
POST /api/accounts
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_type": "SAVINGS",
    "initial_balance": 1000.00
}
```

### Transaction Endpoints

#### Get Transaction History
```bash
GET /api/transactions/{account_id}?limit=10&start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <token>
```

#### Create Transaction
```bash
POST /api/transactions
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_id": 1,
    "transaction_type": "DEPOSIT",
    "amount": 500.00,
    "description": "Salary deposit"
}
```

### Transfer Endpoints

#### Get Transfer History
```bash
GET /api/transfers/{account_id}?limit=10
Authorization: Bearer <token>
```

#### Create Transfer
```bash
POST /api/transfers
Authorization: Bearer <token>
Content-Type: application/json

{
    "from_account_id": 1,
    "to_account_number": "1234-5678-9012",
    "amount": 200.00,
    "description": "Payment to friend"
}
```

### Balance Endpoints

#### Get Account Balance
```bash
GET /api/balance/{account_id}
Authorization: Bearer <token>
```

### Statement Endpoints

#### Get Account Statement
```bash
GET /api/statement/{account_id}?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <token>
```

### API Documentation Endpoint
```bash
GET /api/docs
```

## Web Interface Guide

### Getting Started

1. **Access the Web Interface**: Navigate to http://localhost:5000
2. **Register**: Create a new account or use existing credentials
3. **Login**: Use your email and password to access the dashboard

### Dashboard Features

- **Account Overview**: View all your accounts and balances
- **Quick Actions**: Access common banking operations
- **Recent Transactions**: See your latest transaction history
- **Account Summary**: Total balance across all accounts

### Account Management

#### Creating Accounts
1. Navigate to "My Accounts"
2. Click "New Account"
3. Select account type (Savings, Checking, Business)
4. Set initial deposit amount
5. Confirm account creation

#### Viewing Account Details
1. Click on any account card
2. View detailed transaction history
3. See transfer history
4. Access account performance metrics

### Transactions

#### Making Deposits
1. Go to "Transactions" page
2. Fill in deposit form:
   - Select account
   - Enter amount
   - Add description (optional)
3. Click "Deposit"

#### Making Withdrawals
1. Go to "Transactions" page
2. Fill in withdrawal form:
   - Select account
   - Enter amount
   - Add description (optional)
3. Click "Withdraw"

#### Transferring Money
1. Go to "Transactions" page
2. Fill in transfer form:
   - Select source account
   - Enter destination account number
   - Enter amount
   - Add description (optional)
3. Click "Transfer"

### User Interface Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional interface using Bootstrap 5
- **Real-time Updates**: Balance and transaction updates
- **Quick Actions**: Fast access to common operations
- **Search and Filter**: Easy navigation through data

## Reporting and Analytics

### Available Reports

#### Customer Summary Report
```python
from src.reporting import BankingAnalytics

analytics = BankingAnalytics()
summary = analytics.get_customer_summary(customer_id)
```

#### Monthly Transaction Report
```python
monthly_report = analytics.get_monthly_transaction_report(account_id, months=12)
```

#### Account Performance Metrics
```python
metrics = analytics.get_account_performance_metrics(account_id)
```

#### Bank-wide Statistics
```python
stats = analytics.get_bank_wide_statistics()
```

#### Transaction Trends
```python
trends = analytics.get_transaction_trends(days=30)
```

#### Customer Segmentation
```python
segmentation = analytics.get_customer_segmentation()
```

### Report Types

1. **Customer Reports**
   - Customer summary
   - Account overview
   - Transaction history
   - Performance metrics

2. **Account Reports**
   - Balance statements
   - Transaction summaries
   - Performance analysis
   - Risk assessment

3. **Bank-wide Reports**
   - Overall statistics
   - Transaction trends
   - Customer segmentation
   - Risk analysis

4. **Operational Reports**
   - Monthly reports
   - Risk assessment
   - Audit trails
   - Performance dashboards

## Security Features

### Authentication
- JWT token-based authentication
- Session management for web interface
- Password validation and encryption

### Authorization
- Role-based access control
- Account ownership verification
- API endpoint protection

### Data Protection
- SQL injection prevention
- Input validation and sanitization
- Secure database connections

### Audit Logging
- Complete audit trail of all operations
- User activity tracking
- Data change monitoring

### Security Best Practices
- HTTPS enforcement (in production)
- Secure password policies
- Regular security updates
- Database backup and recovery

## Deployment Guide

### Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python src/init_db.py

# Run web application
python src/web_app.py

# Run API server
python src/api_server.py
```

### Production Environment

#### Using Gunicorn (Recommended)
```bash
# Install Gunicorn
pip install gunicorn

# Run web application
gunicorn -w 4 -b 0.0.0.0:5000 src.web_app:app

# Run API server
gunicorn -w 4 -b 0.0.0.0:5001 src.api_server:app
```

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python src/init_db.py

EXPOSE 5000 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.web_app:app"]
```

#### Environment Variables
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///banking_system.db"
export FLASK_ENV="production"
```

### Database Migration (SQLite to PostgreSQL)
```python
# Update db_connection.py to use PostgreSQL
import psycopg2
from psycopg2.extras import RealDictCursor

# Update connection parameters
DATABASE_URL = "postgresql://user:password@localhost/banking_db"
```

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database file permissions
ls -la banking_system.db

# Recreate database
rm banking_system.db
python src/init_db.py
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python src/web_app.py --port 5002
```

### Performance Optimization

#### Database Optimization
- Regular VACUUM operations
- Index optimization
- Query performance monitoring

#### Application Optimization
- Connection pooling
- Caching strategies
- Load balancing

### Backup and Recovery

#### Database Backup
```bash
# SQLite backup
cp banking_system.db banking_system_backup.db

# SQL dump
sqlite3 banking_system.db .dump > backup.sql
```

#### Data Recovery
```bash
# Restore from backup
cp banking_system_backup.db banking_system.db

# Restore from SQL dump
sqlite3 banking_system.db < backup.sql
```

## Support and Maintenance

### Regular Maintenance Tasks
1. Database backup
2. Log file rotation
3. Security updates
4. Performance monitoring
5. User access review

### Monitoring
- Application logs
- Database performance
- User activity
- Error tracking
- System resources

### Updates and Upgrades
1. Test in development environment
2. Backup production data
3. Apply updates
4. Verify functionality
5. Monitor for issues

---

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Contact

For support and questions, please contact the development team or create an issue in the repository.
