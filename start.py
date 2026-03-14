#!/usr/bin/env python3
"""
Online Banking System - Startup Script
Launches the web application and API server
"""

import os
import sys
import subprocess
import time
import signal
from threading import Thread

def run_web_app():
    """Run the web application"""
    print("Starting Web Application on http://localhost:5000")
    try:
        subprocess.run([sys.executable, "src/web_app.py"], check=True)
    except KeyboardInterrupt:
        print("\nWeb application stopped")
    except Exception as e:
        print(f"Error running web application: {e}")

def run_api_server():
    """Run the API server"""
    print("Starting API Server on http://localhost:5001")
    try:
        subprocess.run([sys.executable, "src/api_server.py"], check=True)
    except KeyboardInterrupt:
        print("\nAPI server stopped")
    except Exception as e:
        print(f"Error running API server: {e}")

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import flask
        import flask_restful
        import jwt
        print("+ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"- Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def initialize_database():
    """Initialize the database if it doesn't exist"""
    if not os.path.exists("banking_system.db"):
        print("Initializing database...")
        try:
            subprocess.run([sys.executable, "src/init_db.py"], check=True)
            print("+ Database initialized successfully")
        except Exception as e:
            print(f"- Error initializing database: {e}")
            return False
    else:
        print("+ Database already exists")
    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("  ONLINE BANKING SYSTEM - STARTUP")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    print("\nChoose startup option:")
    print("1. Web Application only (http://localhost:5000)")
    print("2. API Server only (http://localhost:5001)")
    print("3. Both Web App and API Server")
    print("4. Command Line Interface")
    print("5. Load Sample Data")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    if choice == "1":
        run_web_app()
    elif choice == "2":
        run_api_server()
    elif choice == "3":
        print("\nStarting both Web Application and API Server...")
        print("Web App: http://localhost:5000")
        print("API Server: http://localhost:5001")
        print("Press Ctrl+C to stop both servers")
        
        # Start both servers in separate threads
        web_thread = Thread(target=run_web_app)
        api_thread = Thread(target=run_api_server)
        
        web_thread.daemon = True
        api_thread.daemon = True
        
        web_thread.start()
        time.sleep(2)  # Give web app time to start
        api_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            sys.exit(0)
    elif choice == "4":
        print("Starting Command Line Interface...")
        subprocess.run([sys.executable, "src/main.py"])
    elif choice == "5":
        print("Loading sample data...")
        subprocess.run([sys.executable, "tests/load_sample_data.py"])
    elif choice == "0":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye!")
        sys.exit(0)
