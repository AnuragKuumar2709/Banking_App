# Online Banking System

A comprehensive database management system for online banking operations, handling customer accounts, transactions, balances, and transfers.

## Features

- **Customer Management**: Register and manage customer information
- **Account Management**: Create and manage different types of bank accounts
- **Transaction Processing**: Handle deposits, withdrawals with full audit trail
- **Fund Transfers**: Transfer funds between accounts with transaction integrity
- **Balance Inquiry**: Real-time balance checking and account statements
- **Transaction History**: Complete transaction logs with timestamps

## Database Schema

The system uses the following core tables:
- `customers`: Customer personal information
- `accounts`: Bank account details linked to customers
- `transactions`: All banking transactions (deposits, withdrawals)
- `transfers`: Transfer records between accounts

## Technology Stack

- **Language**: Python 3.x
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Database Driver**: sqlite3 (built-in) / psycopg2

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python src/init_db.py
```

3. (Optional) Load sample data:
```bash
python tests/load_sample_data.py
```

## Usage

Run the main application:
```bash
python src/main.py
```

## Project Structure

```
Banking_app/
├── src/                    # Source code
│   ├── db_connection.py    # Database connectivity
│   ├── account_manager.py  # Account operations
│   ├── transaction_manager.py  # Transaction operations
│   ├── init_db.py          # Database initialization
│   └── main.py             # Main application
├── sql/                    # SQL scripts
│   └── schema.sql          # Database schema
├── tests/                  # Test scripts
│   └── load_sample_data.py # Sample data loader
├── docs/                   # Documentation
└── README.md
```

## Database Features

- ACID compliance for all transactions
- Foreign key constraints for referential integrity
- Indexes for optimized queries
- Triggers for audit logging
- Check constraints for business rules

## License

MIT License
