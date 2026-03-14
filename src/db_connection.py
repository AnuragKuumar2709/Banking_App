"""
Database Connection Module
Handles database connectivity and initialization
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional


class DatabaseConnection:
    """Singleton class for managing database connections"""
    
    _instance: Optional['DatabaseConnection'] = None
    _db_path: str = "banking_system.db"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists and has proper schema"""
        db_exists = os.path.exists(self._db_path)
        if not db_exists:
            print(f"Creating new database: {self._db_path}")
            self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize database schema from SQL file"""
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema_sql)
                conn.commit()
            print("Database schema initialized successfully")
        else:
            print(f"Warning: Schema file not found at {schema_path}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Automatically handles commit/rollback and closing
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of Row objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()):
        """
        Execute an INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()):
        """
        Execute an INSERT query and return the last inserted row ID
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Last inserted row ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    @classmethod
    def set_db_path(cls, path: str):
        """Set custom database path"""
        cls._db_path = path
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (useful for testing)"""
        cls._instance = None


# Create global database instance
db = DatabaseConnection()
