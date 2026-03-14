# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Setup and Installation
```powershell
# Install dependencies
pip install -r requirements.txt

# Initialize database (creates banking_system.db)
python src/init_db.py

# Reset database (deletes existing data)
python src/init_db.py --force

# Load sample data for testing
python tests/load_sample_data.py
```

### Running the Application
```powershell
# Run the interactive CLI application
python src/main.py
```

### Testing
There is no formal test framework configured. To test functionality:
- Use the interactive CLI (`python src/main.py`)
- Run sample data loader to verify database operations
- Manually verify operations through the application menus

## Architecture Overview

### Core Design Pattern: Singleton Database Connection
The system uses a **Singleton pattern** for database management (`db_connection.py`). The `DatabaseConnection` class ensures a single database instance throughout the application lifecycle and provides context manager support for automatic transaction handling.

### Key Architectural Concepts

**Transaction Atomicity**
All financial operations (deposits, withdrawals, transfers) use database transactions to ensure ACID compliance:
- Operations use the `with db.get_connection()` context manager
- Automatic commit on success, rollback on failure
- Foreign key constraints enabled via `PRAGMA foreign_keys = ON`

**Transfer Operations**
Transfers are the most complex transaction type, involving:
1. Two account balance updates (debit + credit)
2. One transfer record
3. Two transaction records (one per account)
All five operations must succeed or fail together atomically.

**Balance Tracking**
Each transaction records `balance_after` to maintain an audit trail of account states over time. This allows historical balance reconstruction without recalculating from the beginning.

### Module Responsibilities

**`db_connection.py`**
- Singleton database connection manager
- Context manager for automatic transaction handling
- Schema initialization from `sql/schema.sql`
- Three main methods: `execute_query()`, `execute_update()`, `execute_insert()`

**`account_manager.py`**
- Customer CRUD operations
- Account creation and management
- Account number generation (format: XXXX-XXXX-XXXX)
- Balance inquiries
- Account closure (requires zero balance)

**`transaction_manager.py`**
- Deposits and withdrawals with balance validation
- Inter-account transfers with atomicity guarantees
- Transaction history retrieval
- Account statement generation

**`main.py`**
- CLI interface with menu-driven navigation
- Integrates account_manager and transaction_manager
- Optional tabulate library for formatted output

### Database Schema

**Four Core Tables:**
1. `customers` - Customer personal information (email is unique)
2. `accounts` - Account details with balance, type (SAVINGS/CHECKING/BUSINESS), status (ACTIVE/CLOSED/FROZEN)
3. `transactions` - All deposits/withdrawals with audit trail
4. `transfers` - Transfer records between accounts

**Key Constraints:**
- Balances must be >= 0 (CHECK constraint)
- Account types limited to: SAVINGS, CHECKING, BUSINESS
- Account status limited to: ACTIVE, INACTIVE, CLOSED, FROZEN
- Transfers cannot be to/from the same account
- Cascading deletes from customers → accounts → transactions/transfers

**Performance Indexes:**
Indexes on email, account_number, customer_id, account_id, and date fields for optimized queries.

## Important Technical Details

### Account Number Format
Generated as random 12-digit format: `XXXX-XXXX-XXXX` (see `generate_account_number()`)

### Database File Location
Default: `banking_system.db` in the current working directory. Can be changed via `DatabaseConnection.set_db_path()`

### Context Manager Pattern
Always use the context manager for database operations:
```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(...)
    # Automatic commit/rollback
```

### Account Status Validation
All transaction operations check if accounts are ACTIVE before proceeding. CLOSED, FROZEN, or INACTIVE accounts cannot perform transactions.

### Error Handling
- Application-level validation raises `ValueError` for business logic violations
- Database-level errors raise generic `Exception`
- All errors are caught and displayed to users with descriptive messages

## Code Modification Guidelines

### Adding New Transaction Types
1. Update schema.sql CHECK constraint for `transaction_type`
2. Add method in `TransactionManager` class
3. Update CLI menu in `main.py`
4. Ensure atomic balance updates using context manager

### Adding New Account Types
1. Update schema.sql CHECK constraint for `account_type`
2. Update validation list in `AccountManager.create_account()`
3. Update CLI menu display in `main.py`

### Modifying Database Schema
1. Update `sql/schema.sql`
2. Run `python src/init_db.py --force` to recreate database
3. Update corresponding manager classes
4. Reload sample data if needed

### Windows-Specific Considerations
- Database file path uses Windows conventions (backslashes handled by Python)
- Line endings are CRLF (`\r\n`)
- PowerShell is the default shell for commands
