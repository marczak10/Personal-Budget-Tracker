# Importing modules
import sqlite3
from user import User
from pwinput import pwinput
from datetime import datetime
from tabulate import tabulate
import bcrypt
import pandas as pd
import os


def main():
    create_users_db()
 
    username, password = login_or_register_UI()
    
    user = User(username, password)
    
    user.login_date()
    
    UI(user)

def UI(user):
    while True:
        table = [
            ["I", "Add an income"],
            ["E", "Add an expense"],
            ["B", "View the current balance"],
            ["V", "View the balance for the end of any month in the past"],
            ["S", "View the summary of a specific month"],
            ["P", "View the summary of a specific period"],
            ["X", "Logout"],
        ]

        print(
            f"\n{tabulate(table, headers=['Key', 'Action'], tablefmt='rounded_outline')}"
        )

        user_input = input("What do you want to do?: ")

        if user_input == "X":
            exit()
        elif user_input == "I":
            user.add_income()
            continue
        elif user_input == "E":
            user.add_expense()
            continue
        elif user_input == "B":
            user.view_balance()
            continue
        elif user_input == "V":
            user.view_balance_end_of_month()
            continue
        elif user_input == "P":
            user.view_summary_period()
            continue
        elif user_input == "S":
            user.view_summary_month()
            continue

def login_or_register_UI():
    while True:
        table = [
            ["L", "Login"],
            ["R", "Register"],
            ["X", "Exit"],
        ]

        print(
            f"\n{tabulate(table, headers=['Key', 'Action'], tablefmt='rounded_outline')}"
        )

        user_input = input("What do you want to do?: ")

        if user_input == "X":
            exit()
        elif user_input == "L":
            username, password = login()
            return username, password
        elif user_input == "R":
            register()
            continue

def login_or_register_UI():
    while True:
        table = [
            ["L", "Login"],
            ["R", "Register"],
            ["X", "Exit"],
        ]

        print(
            f"\n{tabulate(table, headers=['Key', 'Action'], tablefmt='rounded_outline')}"
        )

        user_input = input("What do you want to do?: ")

        if user_input == "X":
            exit()
        elif user_input == "L":
            username, password = login()
            return username, password
        elif user_input == "R":
            register()
            continue

def register():
    c, conn = connect_to_users_db()
    users_db = pd.read_sql_query("SELECT * FROM users", conn)
    while True:
        try:
            username = input("Username: ")
            if not username:
                raise ValueError("You must add a username")
            if username in users_db["username"].values:
                raise ValueError("Username already exists")
            break
        except ValueError:
            print("You must add a username")
            continue
    while True:
        try:
            salt = bcrypt.gensalt()
            password = pwinput("Password: ").encode("utf-8")
            password = bcrypt.hashpw(password, salt)
            if not password:
                raise ValueError("You must add a password")
            password2 = pwinput("Repeat password: ").encode("utf-8")
            password2 = bcrypt.hashpw(password2, salt)
            if password != password2:
                raise ValueError("Passwords do not match")
            break
        except ValueError as e:
            print(e)
            continue
        
    

    c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
    conn.commit()
    
    table = [[f"User {username} registered successfully!"]]
    print(f"\n{tabulate(table, tablefmt='rounded_outline')}")
    
    conn.close()
    
def login():
    c, conn = connect_to_users_db()
    users_db = pd.read_sql_query("SELECT * FROM users", conn)
    while True:
        try:
            username = input("Username: ")
            if not username:
                raise ValueError("You must type in a username")
            break
        except ValueError:
            print("You must type in a username")
            continue
    while True:
        try:
            password = pwinput("Password: ").encode("utf-8")
            if not password:
                raise ValueError("You must type in a password")
            break
        except ValueError:
            print("You must type in a password")
            continue
        
    if username in users_db["username"].values:
        password_hash = users_db[users_db["username"] == username]["password"].values[0]
        if bcrypt.checkpw(password, password_hash):
            table = [[f"\nWelcome {username}!"]]
            print(f"\n{tabulate(table, tablefmt='rounded_outline')}")
        else:
            print(f"\nIncorrect password")
            login_or_register_UI()
    else:
        print(f"\nUsername does not exist")
        login_or_register_UI()
        
    conn.close()
    
    return username, password

def create_users_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    c.execute("CREATE TABLE IF NOT EXISTS users (username text, password text)")
    
    conn.commit()
    conn.close()

def connect_to_users_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    return c, conn   

if __name__ == "__main__":
    main()