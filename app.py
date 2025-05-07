import sys
import random
import string
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                            QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget,
                            QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
                            QDateEdit, QFormLayout, QGroupBox, QHeaderView, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon, QIntValidator, QDoubleValidator
import sqlite3

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('time_banks.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.insert_initial_data()
        
    def create_tables(self):
        # Create all tables with SQLite compatible syntax
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS branch(
            branch_id INTEGER PRIMARY KEY NOT NULL,
            branch_name TEXT,
            city TEXT,
            address TEXT
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS department(
            dep_id INTEGER PRIMARY KEY NOT NULL,
            dep_name TEXT
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer(
            cust_id INTEGER PRIMARY KEY NOT NULL,
            cust_name TEXT,
            dob TEXT,
            phone INTEGER,
            city TEXT,
            address TEXT,
            email TEXT
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee(
            emp_id INTEGER PRIMARY KEY NOT NULL,
            emp_name TEXT,
            gender TEXT CHECK(gender IN ('M', 'F')),
            dep_id INTEGER,
            branch_id INTEGER,
            job_title TEXT,
            salary REAL,
            dbo TEXT,
            phone INTEGER,
            city TEXT,
            address TEXT,
            email TEXT,
            username TEXT UNIQUE NOT NULL,
            passwords TEXT NOT NULL,
            FOREIGN KEY (dep_id) REFERENCES department(dep_id),
            FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts(
            account_no INTEGER PRIMARY KEY,
            cust_id INTEGER,
            balance REAL,
            opened_date TEXT DEFAULT CURRENT_TIMESTAMP,
            account_type TEXT,
            account_status TEXT DEFAULT 'Active' CHECK(account_status IN ('Active', 'Inactive', 'Closed')),
            interest_rate REAL DEFAULT 0.00,
            minimum_balance REAL DEFAULT 0.00,
            currency TEXT DEFAULT 'ETB',
            FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions(
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no INTEGER NOT NULL, 
            transaction_type TEXT CHECK(transaction_type IN ('Deposit', 'Withdrawal', 'Transfer')) NOT NULL,
            transaction_amount REAL NOT NULL, 
            transaction_date TEXT DEFAULT CURRENT_TIMESTAMP, 
            transaction_description TEXT,
            transaction_status TEXT DEFAULT 'Pending' CHECK(transaction_status IN ('Pending', 'Completed', 'Failed')), 
            FOREIGN KEY (account_no) REFERENCES accounts(account_no)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_branch(
            emp_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            PRIMARY KEY (emp_id, branch_id),
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id),
            FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan(
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_id INTEGER NOT NULL,
            account_no INTEGER NOT NULL,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Paid', 'Defaulted')),
            FOREIGN KEY (cust_id) REFERENCES customer(cust_id),
            FOREIGN KEY (account_no) REFERENCES accounts(account_no)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_repayment(
            repayment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            repayment_date TEXT NOT NULL,
            amount_paid REAL NOT NULL,
            FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_log(
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            account_no INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('Deposit', 'Withdrawal', 'Transfer')) NOT NULL,
            transaction_amount REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_description TEXT,
            transaction_status TEXT DEFAULT 'Pending' CHECK(transaction_status IN ('Pending', 'Completed', 'Failed')),
            log_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
            FOREIGN KEY (account_no) REFERENCES accounts(account_no)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_actions(
            action_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            action_type TEXT CHECK(action_type IN ('Hire', 'Fire')) NOT NULL,
            action_date TEXT DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
        )''')
        
        # Create indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_no ON transactions (account_no)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions (transaction_date)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_cust_id ON accounts (cust_id)')
        
        self.conn.commit()
    
    def insert_initial_data(self):
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM branch")
        if self.cursor.fetchone()[0] == 0:
            # Insert branch data
            branches = [
                (1, 'Main Branch', 'Addis Ababa', '22 Bole Road'),
                (2, 'North Branch', 'Mekele', '15 Hawzen Street'),
                (3, 'East Branch', 'Dire Dawa', '8 Kebele Avenue'),
                (4, 'South Branch', 'Hawassa', '3 Lake View Road'),
                (5, 'West Branch', 'Bahir Dar', '12 Tana Circle')
            ]
            self.cursor.executemany("INSERT INTO branch VALUES (?, ?, ?, ?)", branches)
            
            # Insert department data
            departments = [
                (101, 'Accountant'),
                (102, 'Manager'),
                (103, 'Finance'),
                (104, 'Security'),
                (105, 'Cleaner'),
                (107, 'HR')
            ]
            self.cursor.executemany("INSERT INTO department VALUES (?, ?)", departments)
            
            # Create initial admin accounts for each department
            employees = [
                (1, 'Admin HR', 'M', 107, 1, 'HR', 15000, '1990-01-01', 123456789, 
                 'Addis Ababa', '22 Bole Road', 'hr@timebank.com', 'hr', '123456'),
                (2, 'Admin Accountant', 'F', 101, 1, 'Accountant', 20000, '1990-01-01', 
                 123456789, 'Addis Ababa', '22 Bole Road', 'accountant@timebank.com', 'accountant', '123456'),
                (3, 'Admin Manager', 'M', 102, 1, 'Manager', 30000, '1990-01-01', 
                 123456789, 'Addis Ababa', '22 Bole Road', 'manager@timebank.com', 'manager', '123456')
            ]
            self.cursor.executemany('''
                INSERT INTO employee VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', employees)
            
            self.conn.commit()

    def authenticate_user(self, username, password):
        self.cursor.execute('''
            SELECT emp_id, emp_name, dep_id, job_title FROM employee 
            WHERE username = ? AND passwords = ?
        ''', (username, password))
        return self.cursor.fetchone()
    
    def get_employee_details(self, emp_id):
        self.cursor.execute('''
            SELECT e.emp_id, e.emp_name, e.job_title, d.dep_name, b.branch_name 
            FROM employee e
            JOIN department d ON e.dep_id = d.dep_id
            JOIN branch b ON e.branch_id = b.branch_id
            WHERE e.emp_id = ?
        ''', (emp_id,))
        return self.cursor.fetchone()
    
    def get_all_employees(self):
        self.cursor.execute('''
            SELECT e.emp_id, e.emp_name, e.gender, d.dep_name, b.branch_name, e.job_title, e.salary
            FROM employee e
            JOIN department d ON e.dep_id = d.dep_id
            JOIN branch b ON e.branch_id = b.branch_id
        ''')
        return self.cursor.fetchall()
    
    def hire_employee(self, emp_data):
        # Generate random username and password
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        password = ''.join(random.choices(string.digits, k=6))
        
        # Determine salary based on job title
        job_title = emp_data['job_title']
        salary = {
            'HR': 15000,
            'Accountant': 20000,
            'Security': 5000,
            'Cleaner': 5000,
            'Manager': 30000,
            'Finance': 15000
        }.get(job_title, 5000)
        
        # Get next employee ID
        self.cursor.execute("SELECT MAX(emp_id) FROM employee")
        max_id = self.cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        # Insert employee
        self.cursor.execute('''
            INSERT INTO employee VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_id, emp_data['emp_name'], emp_data['gender'], emp_data['dep_id'],
            emp_data['branch_id'], job_title, salary, emp_data['dbo'], emp_data['phone'],
            emp_data['city'], emp_data['address'], emp_data['email'], username, password
        ))
        
        # Record the hiring action
        self.cursor.execute('''
            INSERT INTO employee_actions (emp_id, action_type, details)
            VALUES (?, ?, ?)
        ''', (new_id, 'Hire', f'Employee hired as {job_title}'))
        
        self.conn.commit()
        return new_id, username, password
    
    def fire_employee(self, emp_id):
        self.cursor.execute('''
            DELETE FROM employee WHERE emp_id = ?
        ''', (emp_id,))
        
        # Record the firing action
        self.cursor.execute('''
            INSERT INTO employee_actions (emp_id, action_type, details)
            VALUES (?, ?, ?)
        ''', (emp_id, 'Fire', 'Employee fired'))
        
        self.conn.commit()
    
    def get_all_customers(self):
        self.cursor.execute("SELECT * FROM customer")
        return self.cursor.fetchall()
    
    def create_customer(self, cust_data):
        # Get next customer ID
        self.cursor.execute("SELECT MAX(cust_id) FROM customer")
        max_id = self.cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        self.cursor.execute('''
            INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_id, cust_data['cust_name'], cust_data['dob'], cust_data['phone'],
            cust_data['city'], cust_data['address'], cust_data['email']
        ))
        
        self.conn.commit()
        return new_id
    
    def create_account(self, cust_id, account_type, initial_deposit):
        # Generate random 5-digit account number
        account_no = random.randint(10000, 99999)
        
        # Check if account number already exists
        while True:
            self.cursor.execute("SELECT COUNT(*) FROM accounts WHERE account_no = ?", (account_no,))
            if self.cursor.fetchone()[0] == 0:
                break
            account_no = random.randint(10000, 99999)
        
        self.cursor.execute('''
            INSERT INTO accounts (account_no, cust_id, balance, account_type)
            VALUES (?, ?, ?, ?)
        ''', (account_no, cust_id, initial_deposit, account_type))
        
        # Record initial deposit
        self.cursor.execute('''
            INSERT INTO transactions (account_no, transaction_type, transaction_amount, transaction_status)
            VALUES (?, ?, ?, ?)
        ''', (account_no, 'Deposit', initial_deposit, 'Completed'))
        
        self.conn.commit()
        return account_no
    
    def deposit(self, account_no, amount):
        self.cursor.execute('''
            UPDATE accounts SET balance = balance + ? WHERE account_no = ?
        ''', (amount, account_no))
        
        self.cursor.execute('''
            INSERT INTO transactions (account_no, transaction_type, transaction_amount, transaction_status)
            VALUES (?, ?, ?, ?)
        ''', (account_no, 'Deposit', amount, 'Completed'))
        
        self.conn.commit()
    
    def withdraw(self, account_no, amount):
        # Check if sufficient balance exists
        self.cursor.execute('''
            SELECT balance FROM accounts WHERE account_no = ?
        ''', (account_no,))
        balance = self.cursor.fetchone()[0]
        
        if balance < amount:
            return False
        
        self.cursor.execute('''
            UPDATE accounts SET balance = balance - ? WHERE account_no = ?
        ''', (amount, account_no))
        
        self.cursor.execute('''
            INSERT INTO transactions (account_no, transaction_type, transaction_amount, transaction_status)
            VALUES (?, ?, ?, ?)
        ''', (account_no, 'Withdrawal', amount, 'Completed'))
        
        self.conn.commit()
        return True
    
    def get_account_balance(self, account_no):
        self.cursor.execute('''
            SELECT balance FROM accounts WHERE account_no = ?
        ''', (account_no,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_account_transactions(self, account_no):
        self.cursor.execute('''
            SELECT transaction_id, transaction_type, transaction_amount, transaction_date
            FROM transactions WHERE account_no = ?
            ORDER BY transaction_date DESC
        ''', (account_no,))
        return self.cursor.fetchall()
    
    def get_bank_metrics(self):
        metrics = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM employee")
        metrics['total_employees'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT SUM(balance) FROM accounts")
        metrics['total_bank_balance'] = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT COUNT(*) FROM accounts")
        metrics['total_accounts'] = self.cursor.fetchone()[0]
        
        return metrics
    
    def get_departments(self):
        self.cursor.execute("SELECT * FROM department")
        return self.cursor.fetchall()
    
    def get_branches(self):
        self.cursor.execute("SELECT * FROM branch")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class LoginWindow(QWidget):
    def __init__(self, db_manager, main_window):
        super().__init__()
        self.db_manager = db_manager
        self.main_window = main_window
        self.current_user = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Time International Bank")
        header.setFont(QFont('Arial', 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Logo/Image placeholder
        logo = QLabel("🏦")
        logo.setFont(QFont('Arial', 50))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # Login Form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Login Button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(login_btn)
        
        # Footer
        footer = QLabel("© 2023 Time International Bank. All rights reserved.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray;")
        layout.addWidget(footer)
        
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        user_data = self.db_manager.authenticate_user(username, password)
        
        if user_data:
            emp_id, emp_name, dep_id, job_title = user_data
            self.current_user = {'emp_id': emp_id, 'emp_name': emp_name, 'dep_id': dep_id, 'job_title': job_title}
            
            # Create dashboards based on user role
            self.main_window.create_dashboards(self.current_user)
            
            # Determine which dashboard to show based on department
            if dep_id == 107:  # HR
                self.main_window.stacked_widget.setCurrentIndex(1)
                self.main_window.hr_dashboard.load_data()
            elif dep_id == 101:  # Accountant
                self.main_window.stacked_widget.setCurrentIndex(2)
                self.main_window.accountant_dashboard.load_data()
            elif dep_id == 102:  # Manager
                self.main_window.stacked_widget.setCurrentIndex(3)
                self.main_window.manager_dashboard.load_data()
            else:
                QMessageBox.warning(self, "Access Denied", "You don't have access to any dashboard")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")

class HRDashboard(QWidget):
    def __init__(self, db_manager, main_window, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.main_window = main_window
        self.current_user = current_user
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("HR Dashboard - Time International Bank")
        header.setFont(QFont('Arial', 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # User info
        user_info = QLabel(f"Welcome, {self.current_user['emp_name']} (ID: {self.current_user['emp_id']})")
        user_info.setAlignment(Qt.AlignRight)
        layout.addWidget(user_info)
        
        # Tabs
        tabs = QTabWidget()
        
        # Hire Employee Tab
        hire_tab = QWidget()
        hire_layout = QVBoxLayout()
        
        # Hire Form
        hire_form = QGroupBox("Hire New Employee")
        form_layout = QFormLayout()
        
        self.emp_name_input = QLineEdit()
        form_layout.addRow("Full Name:", self.emp_name_input)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['M', 'F'])
        form_layout.addRow("Gender:", self.gender_combo)
        
        # Department dropdown
        departments = self.db_manager.get_departments()
        self.dep_combo = QComboBox()
        for dep_id, dep_name in departments:
            self.dep_combo.addItem(dep_name, dep_id)
        form_layout.addRow("Department:", self.dep_combo)
        
        # Branch dropdown
        branches = self.db_manager.get_branches()
        self.branch_combo = QComboBox()
        for branch_id, branch_name, city, address in branches:
            self.branch_combo.addItem(f"{branch_name} - {city}", branch_id)
        form_layout.addRow("Branch:", self.branch_combo)
        
        # Job title dropdown with automatic salary
        self.job_combo = QComboBox()
        self.job_combo.addItems(['HR', 'Accountant', 'Security', 'Cleaner', 'Manager', 'Finance'])
        self.job_combo.currentTextChanged.connect(self.update_salary_display)
        form_layout.addRow("Job Title:", self.job_combo)
        
        self.salary_display = QLabel("Salary: 0 ETB")
        form_layout.addRow("Salary:", self.salary_display)
        
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setMaximumDate(QDate.currentDate())
        form_layout.addRow("Date of Birth:", self.dob_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setValidator(QIntValidator())
        form_layout.addRow("Phone:", self.phone_input)
        
        self.city_input = QLineEdit()
        form_layout.addRow("City:", self.city_input)
        
        self.address_input = QLineEdit()
        form_layout.addRow("Address:", self.address_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        hire_form.setLayout(form_layout)
        hire_layout.addWidget(hire_form)
        
        hire_btn = QPushButton("Hire Employee")
        hire_btn.clicked.connect(self.hire_employee)
        hire_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        hire_layout.addWidget(hire_btn)
        
        hire_tab.setLayout(hire_layout)
        
        # Fire Employee Tab
        fire_tab = QWidget()
        fire_layout = QVBoxLayout()
        
        # Employees Table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Department", "Branch", "Job Title", "Salary"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        fire_layout.addWidget(self.employees_table)
        
        fire_btn = QPushButton("Fire Selected Employee")
        fire_btn.clicked.connect(self.fire_employee)
        fire_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        fire_layout.addWidget(fire_btn)
        
        fire_tab.setLayout(fire_layout)
        
        tabs.addTab(hire_tab, "Hire Employee")
        tabs.addTab(fire_tab, "Fire Employee")
        
        layout.addWidget(tabs)
        
        # Logout Button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #607D8B; color: white; padding: 8px;")
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)
    
    def update_salary_display(self, job_title):
        salary = {
            'HR': 15000,
            'Accountant': 20000,
            'Security': 5000,
            'Cleaner': 5000,
            'Manager': 30000,
            'Finance': 15000
        }.get(job_title, 0)
        self.salary_display.setText(f"Salary: {salary} ETB")
    
    def load_data(self):
        employees = self.db_manager.get_all_employees()
        self.employees_table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            for col, data in enumerate(emp):
                item = QTableWidgetItem(str(data))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.employees_table.setItem(row, col, item)
    
    def hire_employee(self):
        emp_data = {
            'emp_name': self.emp_name_input.text(),
            'gender': self.gender_combo.currentText(),
            'dep_id': self.dep_combo.currentData(),
            'branch_id': self.branch_combo.currentData(),
            'job_title': self.job_combo.currentText(),
            'dbo': self.dob_input.date().toString("yyyy-MM-dd"),
            'phone': int(self.phone_input.text()) if self.phone_input.text() else 0,
            'city': self.city_input.text(),
            'address': self.address_input.text(),
            'email': self.email_input.text()
        }
        
        # Validate data
        if not emp_data['emp_name']:
            QMessageBox.warning(self, "Error", "Please enter employee name")
            return
        
        try:
            emp_id, username, password = self.db_manager.hire_employee(emp_data)
            
            # Show success message with credentials
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Employee Hired Successfully")
            msg.setText(f"Employee hired successfully!\n\nID: {emp_id}\nUsername: {username}\nPassword: {password}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            # Clear form
            self.emp_name_input.clear()
            self.phone_input.clear()
            self.city_input.clear()
            self.address_input.clear()
            self.email_input.clear()
            
            # Refresh employee list
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to hire employee: {str(e)}")
    
    def fire_employee(self):
        selected_row = self.employees_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select an employee to fire")
            return
        
        emp_id = int(self.employees_table.item(selected_row, 0).text())
        emp_name = self.employees_table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self, 'Confirm Fire',
            f"Are you sure you want to fire {emp_name} (ID: {emp_id})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.fire_employee(emp_id)
                QMessageBox.information(self, "Success", "Employee fired successfully")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to fire employee: {str(e)}")
    
    def logout(self):
        self.main_window.stacked_widget.setCurrentIndex(0)

class AccountantDashboard(QWidget):
    def __init__(self, db_manager, main_window, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.main_window = main_window
        self.current_user = current_user
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Accountant Dashboard - Time International Bank")
        header.setFont(QFont('Arial', 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # User info
        user_info = QLabel(f"Welcome, {self.current_user['emp_name']} (ID: {self.current_user['emp_id']})")
        user_info.setAlignment(Qt.AlignRight)
        layout.addWidget(user_info)
        
        # Tabs
        tabs = QTabWidget()
        
        # Create Account Tab
        create_account_tab = QWidget()
        create_account_layout = QVBoxLayout()
        
        # Customer Form
        customer_form = QGroupBox("Customer Information")
        form_layout = QFormLayout()
        
        self.cust_name_input = QLineEdit()
        form_layout.addRow("Full Name:", self.cust_name_input)
        
        self.cust_dob_input = QDateEdit()
        self.cust_dob_input.setCalendarPopup(True)
        self.cust_dob_input.setMaximumDate(QDate.currentDate())
        form_layout.addRow("Date of Birth:", self.cust_dob_input)
        
        self.cust_phone_input = QLineEdit()
        self.cust_phone_input.setValidator(QIntValidator())
        form_layout.addRow("Phone:", self.cust_phone_input)
        
        self.cust_city_input = QLineEdit()
        form_layout.addRow("City:", self.cust_city_input)
        
        self.cust_address_input = QLineEdit()
        form_layout.addRow("Address:", self.cust_address_input)
        
        self.cust_email_input = QLineEdit()
        form_layout.addRow("Email:", self.cust_email_input)
        
        customer_form.setLayout(form_layout)
        create_account_layout.addWidget(customer_form)
        
        # Account Form
        account_form = QGroupBox("Account Information")
        account_form_layout = QFormLayout()
        
        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems(['Savings', 'Checking', 'Business'])
        account_form_layout.addRow("Account Type:", self.account_type_combo)
        
        self.initial_deposit_input = QLineEdit()
        self.initial_deposit_input.setValidator(QDoubleValidator())
        self.initial_deposit_input.setText("0")
        account_form_layout.addRow("Initial Deposit (ETB):", self.initial_deposit_input)
        
        account_form.setLayout(account_form_layout)
        create_account_layout.addWidget(account_form)
        
        create_account_btn = QPushButton("Create Account")
        create_account_btn.clicked.connect(self.create_account)
        create_account_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        create_account_layout.addWidget(create_account_btn)
        
        create_account_tab.setLayout(create_account_layout)
        
        # Transaction Tab
        transaction_tab = QWidget()
        transaction_layout = QVBoxLayout()
        
        # Account Selection
        account_group = QGroupBox("Account Selection")
        account_form = QFormLayout()
        
        self.account_no_input = QLineEdit()
        self.account_no_input.setValidator(QIntValidator())
        account_form.addRow("Account Number:", self.account_no_input)
        
        self.check_balance_btn = QPushButton("Check Balance")
        self.check_balance_btn.clicked.connect(self.check_balance)
        account_form.addRow(self.check_balance_btn)
        
        self.balance_display = QLabel("Balance: 0 ETB")
        account_form.addRow("Current Balance:", self.balance_display)
        
        account_group.setLayout(account_form)
        transaction_layout.addWidget(account_group)
        
        # Transaction Form
        trans_group = QGroupBox("Transaction")
        trans_form = QFormLayout()
        
        self.trans_type_combo = QComboBox()
        self.trans_type_combo.addItems(['Deposit', 'Withdrawal'])
        trans_form.addRow("Transaction Type:", self.trans_type_combo)
        
        self.trans_amount_input = QLineEdit()
        self.trans_amount_input.setValidator(QDoubleValidator())
        trans_form.addRow("Amount (ETB):", self.trans_amount_input)
        
        trans_group.setLayout(trans_form)
        transaction_layout.addWidget(trans_group)
        
        trans_btn = QPushButton("Process Transaction")
        trans_btn.clicked.connect(self.process_transaction)
        trans_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        transaction_layout.addWidget(trans_btn)
        
        # Transaction History
        self.trans_history_table = QTableWidget()
        self.trans_history_table.setColumnCount(4)
        self.trans_history_table.setHorizontalHeaderLabels([
            "ID", "Type", "Amount", "Date"
        ])
        self.trans_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        transaction_layout.addWidget(QLabel("Transaction History:"))
        transaction_layout.addWidget(self.trans_history_table)
        
        transaction_tab.setLayout(transaction_layout)
        
        tabs.addTab(create_account_tab, "Create Account")
        tabs.addTab(transaction_tab, "Transactions")
        
        layout.addWidget(tabs)
        
        # Logout Button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #607D8B; color: white; padding: 8px;")
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)
    
    def load_data(self):
        pass  # No initial data to load
    
    def create_account(self):
        cust_data = {
            'cust_name': self.cust_name_input.text(),
            'dob': self.cust_dob_input.date().toString("yyyy-MM-dd"),
            'phone': int(self.cust_phone_input.text()) if self.cust_phone_input.text() else 0,
            'city': self.cust_city_input.text(),
            'address': self.cust_address_input.text(),
            'email': self.cust_email_input.text()
        }
        
        # Validate data
        if not cust_data['cust_name']:
            QMessageBox.warning(self, "Error", "Please enter customer name")
            return
        
        try:
            # Create customer
            cust_id = self.db_manager.create_customer(cust_data)
            
            # Create account
            account_type = self.account_type_combo.currentText()
            initial_deposit = float(self.initial_deposit_input.text())
            
            account_no = self.db_manager.create_account(cust_id, account_type, initial_deposit)
            
            # Show success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Account Created Successfully")
            msg.setText(f"Account created successfully!\n\nCustomer ID: {cust_id}\nAccount Number: {account_no}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            # Clear form
            self.cust_name_input.clear()
            self.cust_phone_input.clear()
            self.cust_city_input.clear()
            self.cust_address_input.clear()
            self.cust_email_input.clear()
            self.initial_deposit_input.setText("0")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create account: {str(e)}")
    
    def check_balance(self):
        account_no = self.account_no_input.text()
        if not account_no:
            QMessageBox.warning(self, "Error", "Please enter an account number")
            return
        
        try:
            balance = self.db_manager.get_account_balance(int(account_no))
            if balance is not None:
                self.balance_display.setText(f"Balance: {balance} ETB")
                
                # Load transaction history
                transactions = self.db_manager.get_account_transactions(int(account_no))
                self.trans_history_table.setRowCount(len(transactions))
                
                for row, trans in enumerate(transactions):
                    for col, data in enumerate(trans):
                        item = QTableWidgetItem(str(data))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        self.trans_history_table.setItem(row, col, item)
            else:
                QMessageBox.warning(self, "Error", "Account not found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check balance: {str(e)}")
    
    def process_transaction(self):
        account_no = self.account_no_input.text()
        if not account_no:
            QMessageBox.warning(self, "Error", "Please enter an account number")
            return
        
        try:
            account_no = int(account_no)
            trans_type = self.trans_type_combo.currentText()
            amount = float(self.trans_amount_input.text())
            
            if amount <= 0:
                QMessageBox.warning(self, "Error", "Amount must be positive")
                return
            
            if trans_type == 'Deposit':
                self.db_manager.deposit(account_no, amount)
                QMessageBox.information(self, "Success", "Deposit successful")
            elif trans_type == 'Withdrawal':
                if self.db_manager.withdraw(account_no, amount):
                    QMessageBox.information(self, "Success", "Withdrawal successful")
                else:
                    QMessageBox.warning(self, "Error", "Insufficient funds")
            
            # Update balance display and transaction history
            self.check_balance()
            self.trans_amount_input.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Transaction failed: {str(e)}")
    
    def logout(self):
        self.main_window.stacked_widget.setCurrentIndex(0)

class ManagerDashboard(QWidget):
    def __init__(self, db_manager, main_window, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.main_window = main_window
        self.current_user = current_user
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Manager Dashboard - Time International Bank")
        header.setFont(QFont('Arial', 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # User info
        user_info = QLabel(f"Welcome, {self.current_user['emp_name']} (ID: {self.current_user['emp_id']})")
        user_info.setAlignment(Qt.AlignRight)
        layout.addWidget(user_info)
        
        # Metrics Group
        metrics_group = QGroupBox("Bank Metrics")
        metrics_layout = QVBoxLayout()
        
        self.metrics_label = QLabel()
        self.metrics_label.setFont(QFont('Arial', 12))
        metrics_layout.addWidget(self.metrics_label)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Employees Table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Department", "Branch", "Job Title", "Salary"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.employees_table)
        
        # Logout Button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #607D8B; color: white; padding: 8px;")
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)
    
    def load_data(self):
        # Load metrics
        metrics = self.db_manager.get_bank_metrics()
        metrics_text = (
            f"Total Employees: {metrics['total_employees']}\n"
            f"Total Accounts: {metrics['total_accounts']}\n"
            f"Total Bank Balance: {metrics['total_bank_balance']} ETB"
        )
        self.metrics_label.setText(metrics_text)
        
        # Load employees
        employees = self.db_manager.get_all_employees()
        self.employees_table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            for col, data in enumerate(emp):
                item = QTableWidgetItem(str(data))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.employees_table.setItem(row, col, item)
    
    def logout(self):
        self.main_window.stacked_widget.setCurrentIndex(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time International Bank Management System")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create login window
        self.login_window = LoginWindow(self.db_manager, self)
        self.stacked_widget.addWidget(self.login_window)
        
        # Initialize dashboard placeholders
        self.hr_dashboard = None
        self.accountant_dashboard = None
        self.manager_dashboard = None
        
        self.setCentralWidget(self.stacked_widget)
    
    def create_dashboards(self, current_user):
        # Remove existing dashboards if they exist
        if self.hr_dashboard:
            self.stacked_widget.removeWidget(self.hr_dashboard)
        if self.accountant_dashboard:
            self.stacked_widget.removeWidget(self.accountant_dashboard)
        if self.manager_dashboard:
            self.stacked_widget.removeWidget(self.manager_dashboard)
        
        # Create new dashboards
        self.hr_dashboard = HRDashboard(self.db_manager, self, current_user)
        self.accountant_dashboard = AccountantDashboard(self.db_manager, self, current_user)
        self.manager_dashboard = ManagerDashboard(self.db_manager, self, current_user)
        
        # Add them to stacked widget
        self.stacked_widget.addWidget(self.hr_dashboard)
        self.stacked_widget.addWidget(self.accountant_dashboard)
        self.stacked_widget.addWidget(self.manager_dashboard)
    
    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())