# Project Report: Online Banking Application

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Objectives](#2-objectives)
3. [Technology Stack](#3-technology-stack)
4. [Database Schema](#4-database-schema)
   - 4.1 Tables
5. [Core Features & Functionality](#5-core-features--functionality)
6. [User Authentication (Session Management)](#6-user-authentication-session-management)
7. [Main Dashboard](#7-main-dashboard)
8. [Conclusion](#8-conclusion)

---

## 1. Introduction

The Online Banking Application is a comprehensive database management system designed to facilitate modern banking operations. This system provides a secure, efficient, and user-friendly platform for managing customer accounts, processing financial transactions, handling fund transfers, and maintaining accurate balance records.

The application addresses the critical needs of modern banking by implementing robust database management principles, ensuring data integrity through ACID compliance, and providing multiple interfaces (Web, API, and CLI) for different user scenarios. The system supports real-time transaction processing, comprehensive audit trails, and advanced reporting capabilities.

This project demonstrates the integration of frontend web technologies with backend database systems, implementing secure authentication mechanisms, and providing a scalable architecture that can be extended for production use.

---

## 2. Objectives

### Primary Objectives:

1. **Customer Management**
   - Create and maintain customer profiles with complete personal information
   - Support multiple customers with unique identification
   - Enable customer information updates and management

2. **Account Management**
   - Support multiple account types (Savings, Checking, Business)
   - Create and manage bank accounts linked to customers
   - Track account balances in real-time
   - Implement account status management (Active, Inactive, Closed, Frozen)

3. **Transaction Processing**
   - Process deposits and withdrawals with complete validation
   - Maintain transaction history with timestamps
   - Ensure atomicity and consistency of all transactions
   - Implement balance tracking and verification

4. **Fund Transfers**
   - Enable secure transfers between accounts
   - Support both internal and external account transfers
   - Maintain transfer records with status tracking
   - Implement validation to prevent invalid transfers

5. **Database Management**
   - Implement normalized database schema
   - Ensure referential integrity through foreign keys
   - Create indexes for optimized query performance
   - Implement audit logging for compliance

6. **User Interface**
   - Provide modern, responsive web interface
   - Create intuitive navigation and user experience
   - Support real-time data updates
   - Implement secure authentication system

---

## 3. Technology Stack

### Backend Technologies:

1. **Python 3.x**
   - Primary programming language
   - Object-oriented design patterns
   - Module-based architecture for maintainability

2. **SQLite Database**
   - Lightweight, serverless database
   - ACID-compliant transactions
   - Foreign key constraints enabled
   - Easy to deploy and maintain
   - Can be upgraded to PostgreSQL for production

3. **Flask Framework (v2.3.3)**
   - Web application framework
   - RESTful API support
   - Template rendering with Jinja2
   - Session management

4. **Flask-RESTful (v0.3.10)**
   - REST API implementation
   - Resource-based endpoints
   - Request parsing and validation

5. **Flask-Login (v0.6.3)**
   - User session management
   - Authentication handling
   - User state management

### Frontend Technologies:

1. **HTML5 & CSS3**
   - Semantic markup
   - Modern styling and layout

2. **Bootstrap 5**
   - Responsive design framework
   - Pre-built UI components
   - Mobile-first approach

3. **JavaScript**
   - Client-side interactivity
   - Dynamic content updates
   - Form validation

4. **Font Awesome Icons**
   - Professional iconography
   - Enhanced user interface

### Security:

1. **JWT (JSON Web Tokens)**
   - Secure API authentication
   - Token-based authorization

2. **Session Management**
   - Secure session handling
   - User authentication state

### Development Tools:

1. **sqlite3**
   - Database operations
   - Connection management

2. **Python-dotenv**
   - Environment variable management
   - Configuration management

---

## 4. Database Schema

### 4.1 Tables

The database schema consists of five primary tables designed to support all banking operations:

#### **Table 1: customers**

Stores customer personal information and profile data.

| Column Name      | Data Type        | Constraints                    | Description                    |
|------------------|------------------|--------------------------------|--------------------------------|
| customer_id      | INTEGER          | PRIMARY KEY, AUTOINCREMENT     | Unique customer identifier     |
| first_name       | VARCHAR(50)      | NOT NULL                       | Customer's first name          |
| last_name        | VARCHAR(50)      | NOT NULL                       | Customer's last name           |
| email            | VARCHAR(100)     | UNIQUE, NOT NULL               | Customer's email address        |
| phone            | VARCHAR(20)      | NULL                           | Customer's phone number        |
| address          | TEXT             | NULL                           | Customer's address             |
| date_of_birth    | DATE             | NULL                           | Customer's date of birth       |
| created_at       | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP      | Account creation timestamp     |
| updated_at       | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP      | Last update timestamp          |

**Relationships:**
- One-to-many relationship with `accounts` table

---

#### **Table 2: accounts**

Manages bank account information and balances.

| Column Name      | Data Type        | Constraints                    | Description                    |
|------------------|------------------|--------------------------------|--------------------------------|
| account_id       | INTEGER          | PRIMARY KEY, AUTOINCREMENT     | Unique account identifier      |
| customer_id      | INTEGER          | NOT NULL, FOREIGN KEY          | Reference to customer           |
| account_number   | VARCHAR(20)      | UNIQUE, NOT NULL               | Unique account number          |
| account_type     | VARCHAR(20)      | NOT NULL, CHECK constraint     | Type: SAVINGS/CHECKING/BUSINESS|
| balance          | DECIMAL(15,2)    | DEFAULT 0.00, CHECK >= 0       | Current account balance        |
| currency         | VARCHAR(3)       | DEFAULT 'INR'                  | Currency code (Indian Rupees)  |
| status           | VARCHAR(20)      | DEFAULT 'ACTIVE', CHECK        | Account status                 |
| created_at       | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP      | Account creation timestamp     |
| updated_at       | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP      | Last update timestamp          |

**Check Constraints:**
- `account_type` IN ('SAVINGS', 'CHECKING', 'BUSINESS')
- `status` IN ('ACTIVE', 'INACTIVE', 'CLOSED', 'FROZEN')
- `balance >= 0`

**Relationships:**
- Many-to-one relationship with `customers` table (ON DELETE CASCADE)
- One-to-many relationship with `transactions` table
- One-to-many relationship with `transfers` table (as source and destination)

---

#### **Table 3: transactions**

Records all deposit and withdrawal transactions.

| Column Name      | Data Type        | Constraints                    | Description                    |
|------------------|------------------|--------------------------------|--------------------------------|
| transaction_id   | INTEGER          | PRIMARY KEY, AUTOINCREMENT     | Unique transaction identifier  |
| account_id       | INTEGER          | NOT NULL, FOREIGN KEY          | Reference to account            |
| transaction_type | VARCHAR(20)     | NOT NULL, CHECK constraint    | Type: DEPOSIT/WITHDRAWAL       |
| amount           | DECIMAL(15,2)    | NOT NULL, CHECK > 0            | Transaction amount             |
| balance_after    | DECIMAL(15,2)    | NOT NULL                       | Balance after transaction      |
| description      | TEXT             | NULL                           | Transaction description         |
| transaction_date | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP      | Transaction timestamp          |

**Check Constraints:**
- `transaction_type` IN ('DEPOSIT', 'WITHDRAWAL')
- `amount > 0`

**Relationships:**
- Many-to-one relationship with `accounts` table (ON DELETE CASCADE)

---

#### **Table 4: transfers**

Tracks inter-account fund transfers.

| Column Name      | Data Type        | Constraints                    | Description                    |
|------------------|------------------|--------------------------------|--------------------------------|
| transfer_id      | INTEGER          | PRIMARY KEY, AUTOINCREMENT     | Unique transfer identifier     |
| from_account_id  | INTEGER          | NOT NULL, FOREIGN KEY          | Source account reference        |
| to_account_id    | INTEGER          | NOT NULL, FOREIGN KEY          | Destination account reference   |
| amount           | DECIMAL(15,2)    | NOT NULL, CHECK > 0            | Transfer amount                |
| description      | TEXT             | NULL                           | Transfer description            |
| status           | VARCHAR(20)      | DEFAULT 'COMPLETED', CHECK      | Transfer status                |
| transfer_date    | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP       | Transfer timestamp             |

**Check Constraints:**
- `status` IN ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED')
- `amount > 0`
- `from_account_id != to_account_id` (cannot transfer to self)

**Relationships:**
- Many-to-one relationship with `accounts` table (from_account_id)
- Many-to-one relationship with `accounts` table (to_account_id)

---

#### **Table 5: audit_log**

Maintains complete audit trail of all database changes.

| Column Name      | Data Type        | Constraints                    | Description                    |
|------------------|------------------|--------------------------------|--------------------------------|
| audit_id         | INTEGER          | PRIMARY KEY, AUTOINCREMENT     | Unique audit log identifier    |
| table_name       | VARCHAR(50)      | NOT NULL                       | Name of modified table         |
| record_id        | INTEGER          | NOT NULL                       | ID of modified record          |
| operation        | VARCHAR(20)      | NOT NULL, CHECK constraint    | Operation type                 |
| old_values       | TEXT             | NULL                           | Previous values (JSON)         |
| new_values       | TEXT             | NULL                           | New values (JSON)              |
| user_id          | INTEGER          | NULL                           | User who performed operation   |
| timestamp        | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP      | Operation timestamp            |

**Check Constraints:**
- `operation` IN ('INSERT', 'UPDATE', 'DELETE')

---

### Database Features

#### **Indexes:**

1. **Customer Indexes:**
   - `idx_customers_email` - Fast email lookup
   - `idx_customers_name` - Fast name searches

2. **Account Indexes:**
   - `idx_accounts_customer` - Fast customer account retrieval
   - `idx_accounts_number` - Fast account number lookup
   - `idx_accounts_type_status` - Filter by type and status

3. **Transaction Indexes:**
   - `idx_transactions_account` - Fast account transaction history
   - `idx_transactions_date` - Date-based queries
   - `idx_transactions_type_date` - Type and date filtering

4. **Transfer Indexes:**
   - `idx_transfers_from` - Source account transfers
   - `idx_transfers_to` - Destination account transfers
   - `idx_transfers_date` - Date-based queries
   - `idx_transfers_status_date` - Status and date filtering

#### **Triggers:**

1. **update_customer_timestamp** - Automatically updates `updated_at` when customer record is modified
2. **update_account_timestamp** - Automatically updates `updated_at` when account record is modified

#### **Views:**

1. **customer_account_summary** - Aggregated customer account information
2. **transaction_summary** - Account transaction statistics
3. **monthly_transaction_summary** - Monthly transaction aggregations
4. **account_balances** - Account balances with customer information
5. **recent_transactions** - Latest transactions with account details
6. **transfer_history** - Transfer records with account information

---

## 5. Core Features & Functionality

### 5.1 Customer Management Module

**Features:**
- Customer registration with validation
- Customer profile management
- Customer information updates
- Customer lookup and retrieval
- Email uniqueness enforcement

**Implementation:**
- `AccountManager.create_customer()` - Creates new customer
- `AccountManager.get_customer()` - Retrieves customer details
- `AccountManager.update_customer()` - Updates customer information
- `AccountManager.get_customer_accounts()` - Gets all accounts for a customer

**Validation:**
- Email must be unique
- Required fields: first_name, last_name, email
- Optional fields: phone, address, date_of_birth

---

### 5.2 Account Management Module

**Features:**
- Multiple account types support
- Unique account number generation
- Account creation with initial balance
- Account status management
- Account closure with zero balance requirement
- Real-time balance tracking

**Account Types:**
1. **SAVINGS** - For savings with interest earning potential
2. **CHECKING** - For daily transactions
3. **BUSINESS** - For business operations

**Implementation:**
- `AccountManager.create_account()` - Creates new account
- `AccountManager.get_account()` - Retrieves account details
- `AccountManager.get_balance()` - Gets current balance
- `AccountManager.close_account()` - Closes account (requires zero balance)

**Business Rules:**
- Account must have zero balance to close
- Balance cannot be negative
- Each customer can have multiple accounts
- Account numbers are unique system-wide

---

### 5.3 Transaction Processing Module

**Features:**
- Deposit processing with balance update
- Withdrawal processing with balance validation
- Transaction history maintenance
- Atomic transaction execution (ACID compliance)
- Balance after transaction tracking

**Implementation:**
- `TransactionManager.deposit()` - Processes deposits
- `TransactionManager.withdraw()` - Processes withdrawals
- `TransactionManager.get_transaction_history()` - Retrieves transaction history
- `TransactionManager.get_account_statement()` - Generates account statements

**Validation:**
- Amount must be positive
- Account must be active
- Sufficient balance check for withdrawals
- Transaction type validation

**Transaction Flow:**
1. Validate account and amount
2. Check account status
3. Begin database transaction
4. Update account balance
5. Record transaction entry
6. Commit transaction
7. Return transaction details

---

### 5.4 Fund Transfer Module

**Features:**
- Inter-account fund transfers
- Transfer validation and verification
- Dual transaction recording (withdrawal + deposit)
- Transfer status tracking
- Transfer history maintenance

**Implementation:**
- `TransactionManager.transfer()` - Processes transfers
- `TransactionManager.get_transfer_history()` - Retrieves transfer history

**Validation:**
- Source and destination accounts must exist
- Both accounts must be active
- Sufficient balance in source account
- Cannot transfer to same account
- Amount must be positive

**Transfer Flow:**
1. Validate both accounts
2. Check account statuses
3. Verify sufficient balance
4. Begin database transaction
5. Deduct from source account
6. Credit to destination account
7. Record transfer entry
8. Create transaction records for both accounts
9. Commit transaction
10. Return transfer details

---

### 5.5 Reporting & Analytics Module

**Features:**
- Customer summary reports
- Monthly transaction reports
- Account performance metrics
- Bank-wide statistics
- Transaction trend analysis
- Customer segmentation
- Risk assessment reports

**Implementation:**
- `BankingAnalytics.get_customer_summary()` - Customer analytics
- `BankingAnalytics.get_monthly_transaction_report()` - Monthly reports
- `BankingAnalytics.get_account_performance_metrics()` - Performance analysis
- `BankingAnalytics.get_bank_wide_statistics()` - System statistics
- `BankingAnalytics.get_transaction_trends()` - Trend analysis
- `BankingAnalytics.get_customer_segmentation()` - Customer categorization
- `ReportGenerator.generate_monthly_report()` - Monthly banking report
- `ReportGenerator.generate_risk_assessment_report()` - Risk analysis

---

### 5.6 Web Interface

**Pages:**
1. **Home Page** - Landing page with features overview
2. **Login Page** - User authentication
3. **Registration Page** - New user registration
4. **Dashboard** - Main user dashboard with account overview
5. **Accounts Page** - Account management interface
6. **Transactions Page** - Transaction processing interface
7. **Account Details Page** - Detailed account view with history
8. **Create Account Page** - New account creation form

**Features:**
- Responsive design (mobile, tablet, desktop)
- Real-time balance updates
- Modern UI with Bootstrap 5
- Intuitive navigation
- Flash messages for user feedback
- Form validation

---

### 5.7 REST API

**Endpoints:**

1. **Authentication:**
   - `POST /api/login` - User login and token generation

2. **Customers:**
   - `GET /api/customers/{id}` - Get customer information
   - `POST /api/customers` - Create new customer

3. **Accounts:**
   - `GET /api/accounts` - Get user accounts
   - `GET /api/accounts/{id}` - Get specific account
   - `POST /api/accounts` - Create new account

4. **Transactions:**
   - `GET /api/transactions/{account_id}` - Get transaction history
   - `POST /api/transactions` - Create transaction

5. **Transfers:**
   - `GET /api/transfers/{account_id}` - Get transfer history
   - `POST /api/transfers` - Create transfer

6. **Balance:**
   - `GET /api/balance/{account_id}` - Get account balance

7. **Statements:**
   - `GET /api/statement/{account_id}` - Get account statement

8. **Documentation:**
   - `GET /api/docs` - API documentation

**Authentication:**
- JWT token-based authentication
- Bearer token in Authorization header
- Token expiration: 24 hours

---

## 6. User Authentication (Session Management)

### 6.1 Authentication Mechanism

The system implements dual authentication approaches:

#### **Web Interface Authentication:**

- **Framework:** Flask-Login
- **Method:** Session-based authentication
- **Session Storage:** Server-side sessions
- **Features:**
  - User login with email and password
  - Session persistence across requests
  - Automatic session management
  - Secure logout functionality

**Login Process:**
1. User submits email and password
2. System validates credentials against database
3. User object created and stored in session
4. Session cookie set with secure flags
5. User redirected to dashboard

**Session Management:**
- Sessions managed by Flask-Login
- User object stored in session
- `@login_required` decorator for protected routes
- Automatic session expiration handling

#### **API Authentication:**

- **Framework:** JWT (JSON Web Tokens)
- **Method:** Token-based authentication
- **Token Format:** Bearer token
- **Features:**
  - Stateless authentication
  - Token expiration (24 hours)
  - Secure token generation
  - Token validation on each request

**API Authentication Flow:**
1. Client requests login with credentials
2. Server validates credentials
3. Server generates JWT token
4. Client stores token
5. Client includes token in Authorization header for subsequent requests
6. Server validates token on each API call

### 6.2 Security Features

1. **Password Handling:**
   - Password validation during registration
   - Secure password comparison
   - No plain text password storage in logs

2. **Session Security:**
   - Secure session cookies
   - HTTP-only cookies (prevents XSS)
   - CSRF protection ready

3. **Authorization:**
   - Account ownership verification
   - User can only access their own data
   - API endpoint protection

4. **Data Protection:**
   - SQL injection prevention (parameterized queries)
   - Input validation and sanitization
   - XSS protection in templates

### 6.3 Access Control

- **Public Routes:** Home, Login, Register
- **Protected Routes:** Dashboard, Accounts, Transactions
- **Account Verification:** Users can only access their own accounts
- **API Authorization:** Token validation for all API endpoints

---

## 7. Main Dashboard

### 7.1 Dashboard Overview

The main dashboard (`dashboard.html`) serves as the central hub for users after authentication. It provides a comprehensive view of the user's banking information and quick access to key features.

### 7.2 Dashboard Components

#### **1. Account Summary Section**

- **Total Balance Display:**
  - Shows aggregate balance across all accounts
  - Currency: Indian Rupees (₹)
  - Real-time balance calculation
  - Account count display

- **Quick Actions Panel:**
  - Direct link to transaction page
  - Link to view all accounts
  - Fast navigation to common tasks

#### **2. Account Cards Grid**

- **Individual Account Cards:**
  - Account type display (Savings, Checking, Business)
  - Account number
  - Current balance
  - Account status badge
  - Quick "View Details" button

- **Features:**
  - Responsive grid layout
  - Hover effects for interactivity
  - Color-coded status indicators
  - Direct navigation to account details

#### **3. Recent Transactions Table**

- **Transaction Information:**
  - Transaction date and time
  - Account number
  - Transaction type (Deposit/Withdrawal)
  - Transaction amount (color-coded)
  - Description
  - Balance after transaction

- **Features:**
  - Latest 10 transactions displayed
  - Sortable by date (newest first)
  - Color-coded transaction types
  - Link to full transaction history

#### **4. Navigation Sidebar**

- **Menu Items:**
  - Dashboard (active)
  - My Accounts
  - Transactions
  - Logout

- **User Information:**
  - Welcome message with user name
  - Application branding

### 7.3 Dashboard Functionality

**Data Loading:**
- Fetches all customer accounts on page load
- Retrieves recent transactions from all accounts
- Calculates total balance dynamically
- Aggregates transaction data

**User Experience:**
- Clean, modern interface
- Responsive design for all devices
- Fast page loading
- Intuitive navigation

**Real-time Updates:**
- Balance updates after transactions
- Transaction list refreshes
- Account status reflects changes immediately

### 7.4 Dashboard Features

1. **Account Overview:**
   - Visual representation of all accounts
   - Quick balance check
   - Account status at a glance

2. **Transaction History:**
   - Recent activity tracking
   - Quick access to full history
   - Transaction details preview

3. **Quick Actions:**
   - One-click access to common tasks
   - Streamlined user workflow
   - Reduced navigation steps

4. **Visual Indicators:**
   - Color-coded status badges
   - Transaction type indicators
   - Balance highlighting

---

## 8. Conclusion

### 8.1 Project Summary

The Online Banking Application successfully implements a comprehensive database management system for banking operations. The project demonstrates proficiency in database design, web application development, API design, and system architecture.

**Key Achievements:**

1. **Complete Banking System:**
   - Full customer and account management
   - Transaction processing with validation
   - Fund transfer capabilities
   - Real-time balance tracking

2. **Robust Database Design:**
   - Normalized schema with proper relationships
   - ACID compliance for data integrity
   - Indexes for performance optimization
   - Audit logging for compliance

3. **Multiple Interfaces:**
   - Modern web interface for end users
   - RESTful API for external integrations
   - Command-line interface for administration

4. **Security Implementation:**
   - JWT authentication for API
   - Session management for web interface
   - Input validation and SQL injection prevention
   - Account ownership verification

5. **Advanced Features:**
   - Comprehensive reporting and analytics
   - Transaction trend analysis
   - Customer segmentation
   - Risk assessment capabilities

### 8.2 Technical Highlights

- **Database Management:** Efficient SQLite database with proper schema design, indexes, triggers, and views
- **Backend Architecture:** Modular Python codebase with separation of concerns
- **Frontend Design:** Modern, responsive UI with Bootstrap 5
- **API Design:** RESTful API following industry standards
- **Security:** Multiple layers of authentication and authorization
- **Performance:** Optimized queries with proper indexing
- **Maintainability:** Well-documented code with clear structure

### 8.3 Business Value

The system provides:
- **Efficiency:** Automated transaction processing
- **Accuracy:** Real-time balance tracking and validation
- **Security:** Secure authentication and data protection
- **Scalability:** Architecture supports future expansion
- **Compliance:** Complete audit trail for regulatory requirements
- **User Experience:** Intuitive interface for banking operations

### 8.4 Future Enhancements

Potential improvements for production deployment:

1. **Security:**
   - Multi-factor authentication (MFA)
   - Password encryption (bcrypt/hashing)
   - HTTPS enforcement
   - Rate limiting for API

2. **Features:**
   - Loan management system
   - Investment tracking
   - Bill payment functionality
   - Mobile application
   - SMS/Email notifications

3. **Performance:**
   - Database connection pooling
   - Caching layer (Redis)
   - Load balancing
   - Database migration to PostgreSQL

4. **Analytics:**
   - Advanced reporting
   - Machine learning predictions
   - Fraud detection
   - Customer behavior analysis

### 8.5 Learning Outcomes

This project demonstrates:
- Database design principles and normalization
- ACID transaction properties
- Web application development with Flask
- REST API design and implementation
- Authentication and authorization mechanisms
- Frontend-backend integration
- Security best practices
- Software architecture patterns

### 8.6 Conclusion

The Online Banking Application represents a production-ready banking system that successfully combines robust database management with modern web technologies. The implementation showcases best practices in software development, database design, and system architecture.

The system is fully functional, well-documented, and ready for deployment or further enhancement. It provides a solid foundation for a real-world banking application while demonstrating comprehensive understanding of database management systems and web application development.

---

**Project Completion Date:** October 2025  
**Currency:** Indian Rupees (₹)  
**Database:** SQLite (banking_system.db)  
**Status:** Fully Operational

---

## Appendix

### Database Location

**Backend Data Storage:**
- **File:** `banking_system.db`
- **Location:** Project root directory (`D:\Banking_app\banking_system.db`)
- **Type:** SQLite database file
- **Schema:** Defined in `sql/schema.sql`
- **Initialization:** Automatic on first run via `src/db_connection.py`

### Project Structure

```
Banking_app/
├── src/                    # Source code
│   ├── web_app.py         # Flask web application
│   ├── api_server.py     # REST API server
│   ├── main.py           # CLI interface
│   ├── account_manager.py
│   ├── transaction_manager.py
│   ├── db_connection.py
│   └── reporting.py
├── templates/             # HTML templates
├── sql/                   # SQL scripts
│   └── schema.sql
├── tests/                 # Test scripts
├── docs/                  # Documentation
└── banking_system.db      # Database file
```

### Sample Data

The system includes sample data loader (`tests/load_sample_data.py`) that creates:
- 3 sample customers
- 5 sample accounts (various types)
- Multiple transactions and transfers
- Complete transaction history

---

**End of Report**
