"""
Database Initialization Script
Run this script to create/reset the database
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connection import DatabaseConnection


def init_database(force: bool = False):
    """
    Initialize the database
    
    Args:
        force: If True, delete existing database and recreate
    """
    db_path = DatabaseConnection._db_path
    
    if force and os.path.exists(db_path):
        print(f"Deleting existing database: {db_path}")
        os.remove(db_path)
    
    print("Initializing database...")
    db = DatabaseConnection()
    
    # Force schema initialization
    if not os.path.exists(db_path) or force:
        db._initialize_schema()
    
    print(f"Database initialized successfully at: {db_path}")
    print("\nDatabase tables created:")
    print("  - customers")
    print("  - accounts")
    print("  - transactions")
    print("  - transfers")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize the banking system database")
    parser.add_argument('--force', action='store_true', 
                       help='Delete existing database and recreate')
    
    args = parser.parse_args()
    
    if args.force:
        confirm = input("This will delete all existing data. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled")
            sys.exit(0)
    
    init_database(force=args.force)
