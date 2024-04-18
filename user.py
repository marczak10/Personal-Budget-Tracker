import os
import sqlite3
from datetime import datetime
import pandas as pd
from tabulate import tabulate
import calendar


class User:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.user_folder = os.path.join('database_folder', username)  
        if not os.path.exists(self.user_folder):
            os.makedirs(self.user_folder)
        self.transaction_db = os.path.join(self.user_folder, f"{username}_transaction.db")
        self.recurring_db = os.path.join(self.user_folder, f"{username}_recurring.db")
        self.login_db = os.path.join(self.user_folder, f"{username}_login.db")

        self._create_db(self.transaction_db)
        self._create_db(self.recurring_db)
        self._create_db(self.login_db)
        
        
        self.balance = self._get_balance()
        
        

    def _create_db(self, db_name):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        
        c.execute('CREATE TABLE IF NOT EXISTS transactions (Amount REAL, Date TEXT, Description TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS recurring_transactions (Amount REAL, Date TEXT, Description TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS login (date TEXT)')
        conn.commit()
        
        conn.close()
        
    def login_date(self):
        conn = sqlite3.connect(self.login_db)
        c = conn.cursor()
        
        login_db = pd.read_sql_query("SELECT * FROM login", conn)
        if not datetime.today().strftime("%Y-%m-%d") in login_db["date"].values:
            c.execute("INSERT INTO login VALUES (?)", (datetime.today().strftime("%Y-%m-%d"),))
            conn.commit()
            conn.close()

    def _get_balance(self):
        conn = sqlite3.connect(self.transaction_db)
        c = conn.cursor()
        
        transaction_db = pd.read_sql_query("SELECT * FROM transactions", conn)
        balance = transaction_db['Amount'].sum()
        
        conn.close()
        
        return balance
    
    def get_input_amount(self):
        while True:
            try:
                input_amount = input("Amount: ")
                if "," in input_amount:
                    cleaned_amount = input_amount.replace(",", ".").strip()
                    income_amount = float(cleaned_amount)
                else:
                    income_amount = float(input_amount)
                decimal_portion = str(income_amount).split(".")[1]
                if income_amount <= 0 or not (0 <= int(decimal_portion) <= 99):
                    raise ValueError("Invalid input")
                break
            except ValueError:
                print("Invalid input")
        while True:
            try:
                income_date = input("Date (YYYY-MM-DD): ")
                datetime.strptime(income_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format")
        while True:
            try:
                income_description = input("Descripition: ")
                if not income_description:
                    raise ValueError("You must add a descripiton")
                break
            except ValueError:
                print("You must add a description")
            
        return income_amount, income_date, income_description
        
    def get_input_date(self):
        while True:
            try:
                date = input("Enter the date (YYYY-MM): ")
                datetime.strptime(date, "%Y-%m")
                break
            except ValueError:
                print("Invalid input")
                
        return date
    
    def check_recurring_transactions(self):
        conn = sqlite3.connect(self.recurring_db)
        c = conn.cursor()
        conn2 = sqlite3.connect(self.login_db)
        c2 = conn2.cursor()
        conn3 = sqlite3.connect(self.transaction_db)
        c3 = conn3.cursor()

        
        recurring_db = pd.read_sql_query("SELECT * FROM recurring_transactions", conn)
        login_db = pd.read_sql_query("SELECT * FROM login", conn2)
        transaction_db = pd.read_sql_query("SELECT * FROM transactions", conn3)
        
        try:
            last_login = login_db["date"].values[-2]
            todays_login = login_db["date"].values[-1]
        except IndexError:
            last_login = login_db["date"].values[-1]
            todays_login = login_db["date"].values[-1]
        
        dates = pd.date_range(last_login, todays_login, freq="D")
        
        for date in dates:
            for index, row in recurring_db.iterrows():
                if date.strftime("%m-%d") == row["Date"]:
                    transaction_exists = ((transaction_db['Amount'] == row["Amount"]) & 
                                  (transaction_db['Date'] == date.strftime("%Y-%m-%d")) & 
                                  (transaction_db['Description'] == row["Description"])).any()
                    
                    if not transaction_exists:
                        c3.execute("INSERT INTO transactions VALUES (?, ?, ?)", (row["Amount"], date.strftime("%Y-%m-%d"), row["Description"]))
                        conn3.commit()
        conn.close()
        conn2.close()
        conn3.close()       
                    
    def add_income(self):
        amount, date, description = User.get_input_amount(self)
        today_date = datetime.today().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.transaction_db)
        c = conn.cursor()
        
        c.execute("INSERT INTO transactions VALUES (?, ?, ?)", (amount, date, description))
        conn.commit()
                
        conn.close()
            
        self.balance = self._get_balance()
        
    def add_expense(self):
        amount, date, description = User.get_input_amount(self)
        
        conn = sqlite3.connect(self.transaction_db)
        c = conn.cursor()
        
        c.execute("INSERT INTO transactions VALUES (?, ?, ?)", (-amount, date, description))
        conn.commit()
            
        conn.close()
        
        self.balance = self._get_balance()
        
    def view_balance(self):
        table = [[f"Your current balance", f"{self.balance:.2f} zl"]]
        print(f"\n{tabulate(table, tablefmt='rounded_outline')}")
        
    def view_balance_end_of_month(self):
        date = User.get_input_date(self)
        date = f"{date}-{calendar.monthrange(int(date.split('-')[0]), int(date.split('-')[1]))[1]}"
        
        conn = sqlite3.connect(self.transaction_db)
        c = conn.cursor()
        
        transaction_db = pd.read_sql_query("SELECT * FROM transactions", conn)
        transaction_db = transaction_db[transaction_db["Date"] <= date]
        balance = transaction_db["Amount"].sum()

        table = [[f"Your balance at the end of {date}", f"{balance:.2f} zl"]]
        print(f"\n{tabulate(table, tablefmt='rounded_outline')}")
        
        conn.close()
        
    def view_summary_month(self):
        date = User.get_input_date(self)
        
        year, month = date.split("-")
        
        conn = sqlite3.connect(self.transaction_db)   
        c = conn.cursor()
        
        transaction_db = pd.read_sql_query("SELECT * FROM transactions", conn)
        transaction_db['Date'] = pd.to_datetime(transaction_db['Date'])    
        monthly_transactions = transaction_db[(transaction_db["Date"].dt.year == int(year)) & (transaction_db["Date"].dt.month == int(month))]
        balance = monthly_transactions["Amount"].sum()

        transactions_month_before = transaction_db[
            transaction_db["Date"] <= (pd.to_datetime(date) - pd.DateOffset(months=1))
        ]

        balance_end_of_month = transactions_month_before["Amount"].sum()

        table = [
            [f"Your balance at the start of {date}", f"{balance_end_of_month:.2f} zl"],
            [f"Your balance in {date}", f"{balance:.2f} zl"],
        ]

        monthly_transactions.index += 1
        table2 = monthly_transactions[["Date", "Amount", "Description"]]
        table2["Date"] = table2["Date"].dt.strftime("%Y-%m-%d")

        print(f"\n{tabulate(table, tablefmt='rounded_outline')}")
        print(f"\n{tabulate(table2, headers=['Date', 'Amount', 'Description'], tablefmt='rounded_outline')}")
        
        conn.close()
        
    def view_summary_period(self):
        while True:
            try:
                date1 = input("Enter the start date (YYYY-MM-DD): ")
                datetime.strptime(date1, "%Y-%m-%d")
                
                date2 = input("Enter the end date (YYYY-MM-DD): ")
                datetime.strptime(date2, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format")
        
        conn = sqlite3.connect(self.transaction_db)
        c = conn.cursor()
        
        transaction_db = pd.read_sql_query("SELECT * FROM transactions", conn)
        transaction_db['Date'] = pd.to_datetime(transaction_db['Date'])
        transactions_period = transaction_db[(transaction_db["Date"] >= date1) & (transaction_db["Date"] <= date2)]
        
        balance = transactions_period["Amount"].sum()
        transactions_period.index += 1
        
        table = [[f"Your balance in the period {date1} - {date2}", f"{balance:.2f} zl"]]
        table2 = transactions_period[["Date", "Amount", "Description"]]
        table2["Date"] = table2["Date"].dt.strftime("%Y-%m-%d")
        
        print(f"\n{tabulate(table, tablefmt='rounded_outline')}")
        print(f"\n{tabulate(table2, headers=['Date', 'Amount', 'Description'], tablefmt='rounded_outline')}")
        
        conn.close()