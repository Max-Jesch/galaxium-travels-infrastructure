#!/usr/bin/env python3
"""
Test runner script for Galaxium Travels Booking API
Provides easy access to different testing options
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [option]")
        print("\nOptions:")
        print("  all          - Run all tests with coverage")
        print("  fast         - Run tests without coverage (faster)")
        print("  user         - Run only user management tests")
        print("  booking      - Run only booking system tests")
        print("  flight       - Run only flight management tests")
        print("  coverage     - Run tests and generate coverage report")
        print("  lint         - Run linting checks")
        print("  help         - Show this help message")
        return
    
    option = sys.argv[1].lower()
    
    if option == "help":
        print("Usage: python run_tests.py [option]")
        print("\nOptions:")
        print("  all          - Run all tests with coverage")
        print("  fast         - Run tests without coverage (faster)")
        print("  user         - Run only user management tests")
        print("  booking      - Run only booking system tests")
        print("  flight       - Run only flight management tests")
        print("  coverage     - Run tests and generate coverage report")
        print("  lint         - Run linting checks")
        print("  help         - Show this help message")
        return
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if option == "all":
        print("Running all tests with coverage...")
        success = run_command("python -m pytest tests/ -v --cov=app --cov=models --cov=db --cov-report=term-missing --cov-report=html:htmlcov")
    
    elif option == "fast":
        print("Running tests without coverage (faster)...")
        success = run_command("python -m pytest tests/ -v")
    
    elif option == "user":
        print("Running user management tests...")
        success = run_command("python -m pytest tests/test_user_management.py -v")
    
    elif option == "booking":
        print("Running booking system tests...")
        success = run_command("python -m pytest tests/test_booking_system.py -v")
    
    elif option == "flight":
        print("Running flight management tests...")
        success = run_command("python -m pytest tests/test_flight_management.py -v")
    
    elif option == "coverage":
        print("Running tests and generating coverage report...")
        success = run_command("python -m pytest tests/ --cov=app --cov=models --cov=db --cov-report=html:htmlcov --cov-report=term-missing")
        if success:
            print("\nCoverage report generated in htmlcov/ directory")
            print("Open htmlcov/index.html in your browser to view the report")
    
    elif option == "lint":
        print("Running linting checks...")
        # You can add flake8, black, or other linting tools here
        print("Linting tools not configured yet. Consider adding flake8 or black.")
        success = True
    
    else:
        print(f"Unknown option: {option}")
        print("Use 'python run_tests.py help' for available options")
        return
    
    if success:
        print(f"\n✅ {option} completed successfully!")
    else:
        print(f"\n❌ {option} failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
