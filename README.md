# Personal-Budget-Tracker

## Overview
The Personal Budget Tracker is a command-line application designed to help individuals manage their incomes and expenses effectively. It provides features to add income and expenses, view current balance, and generate summaries for specific months or periods.

## Features
- **User Registration and Login**: Secure registration and login functionality for personal use.
- **Income and Expense Tracking**: Allows users to record and categorize their income and expenses.
- **Balance Viewing**: Users can view their current balance at any time.
- **Historical Data Viewing**: The application provides the option to view balance and transactions for any specified month or period in the past.
- **Summary Reports**: Generate detailed reports for specific months or custom periods to track financial health over time.

## Requirements
- Python 3.x
- Libraries: `sqlite3`, `pandas`, `tabulate`, `bcrypt`, `pwinput`

## Installation
Clone the repository or download the files directly. Install the required Python libraries using the following command:

pip install pandas tabulate bcrypt pwinput

## Usage
To run the Personal Budget Tracker, navigate to the project directory and run:
python main.py

Follow the on-screen prompts to either log in or register a new account. Once logged in, you can use the menu options to manage your finances:

- **I**: Add an income
- **E**: Add an expense
- **B**: View current balance
- **V**: View the balance for the end of any specified past month
- **S**: View a summary for a specific month
- **P**: View a summary for a specific period
- **X**: Logout


