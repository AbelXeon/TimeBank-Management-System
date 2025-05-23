import sys
import os
import random
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QFormLayout, QTabWidget, QStackedWidget, QHeaderView,
                             QDialog, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Database setup
DB_NAME = "time_bank.db"


def initialize_database():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
        CREATE TABLE branch(
            branch_id INTEGER PRIMARY KEY NOT NULL,
            branch_name TEXT,
            city TEXT,
            address TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE department(
            dep_id INTEGER PRIMARY KEY NOT NULL,
            dep_name TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE customer(
            cust_id INTEGER PRIMARY KEY NOT NULL,
            cust_name TEXT,
            dob TEXT,
            phone INTEGER,
            city TEXT,
            address TEXT,
            email TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE employee(
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
        )
        """)

        cursor.execute("""
        CREATE TABLE accounts (
            account_no INTEGER PRIMARY KEY,
            cust_id INTEGER,
            balance REAL,
            opened_date TEXT DEFAULT CURRENT_TIMESTAMP,
            account_type TEXT,
            account_status TEXT CHECK(account_status IN ('Active', 'Inactive', 'Closed')) DEFAULT 'Active',
            interest_rate REAL DEFAULT 0.00,
            minimum_balance REAL DEFAULT 0.00,
            currency TEXT DEFAULT 'ETB',
            FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no INTEGER NOT NULL, 
            transaction_type TEXT CHECK(transaction_type IN ('Deposit', 'Withdrawal', 'Transfer')) NOT NULL,
            transaction_amount REAL NOT NULL, 
            transaction_date TEXT DEFAULT CURRENT_TIMESTAMP, 
            transaction_description TEXT,
            transaction_status TEXT CHECK(transaction_status IN ('Pending', 'Completed', 'Failed')) DEFAULT 'Pending', 
            FOREIGN KEY (account_no) REFERENCES accounts (account_no)
        )
        """)

        cursor.execute("""
        CREATE TABLE employee_branch (
            emp_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            PRIMARY KEY (emp_id, branch_id),
            FOREIGN KEY (emp_id) REFERENCES employee (emp_id),
            FOREIGN KEY (branch_id) REFERENCES branch (branch_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE loan (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_id INTEGER NOT NULL,
            account_no INTEGER NOT NULL,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT CHECK(status IN ('Active', 'Paid', 'Defaulted')) DEFAULT 'Active',
            FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
            FOREIGN KEY (account_no) REFERENCES accounts (account_no)
        )
        """)

        cursor.execute("""
        CREATE TABLE loan_repayment (
            repayment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            repayment_date TEXT NOT NULL,
            amount_paid REAL NOT NULL,
            FOREIGN KEY (loan_id) REFERENCES loan (loan_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE transaction_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            account_no INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('Deposit', 'Withdrawal', 'Transfer')) NOT NULL,
            transaction_amount REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_description TEXT,
            transaction_status TEXT CHECK(transaction_status IN ('Pending', 'Completed', 'Failed')) DEFAULT 'Pending',
            log_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),
            FOREIGN KEY (account_no) REFERENCES accounts (account_no)
        )
        """)

        cursor.execute("""
        CREATE TABLE employee_actions (
            action_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            action_type TEXT CHECK(action_type IN ('Hire', 'Fire')) NOT NULL,
            action_date TEXT DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (emp_id) REFERENCES employee (emp_id)
        )
        """)

        # Insert initial data
        branches = [
            (1, 'Main Branch', 'Addis Ababa', '22 Bole Road'),
            (2, 'North Branch', 'Mekele', '15 Hawzen Street'),
            (3, 'East Branch', 'Dire Dawa', '8 Kebele Avenue'),
            (4, 'South Branch', 'Hawassa', '3 Lake View Road'),
            (5, 'West Branch', 'Bahir Dar', '12 Tana Circle')
        ]
        cursor.executemany("INSERT INTO branch VALUES (?, ?, ?, ?)", branches)

        departments = [
            (101, 'Accountant'),
            (102, 'Manager'),
            (103, 'Finance'),
            (104, 'Security'),
            (105, 'Cleaner'),
            (107, 'HR')
        ]
        cursor.executemany("INSERT INTO department VALUES (?, ?)", departments)

        # Create initial admin accounts
        initial_employees = [
            (1001, 'Admin Manager', 'M', 102, 1, 'Manager', 30000, '1980-01-01', 911223344, 'Addis Ababa',
             '22 Bole Road', 'manager@timebank.com', 'manager', '123456'),
            (1002, 'Admin HR', 'F', 107, 1, 'HR', 15000, '1985-05-15', 922334455, 'Addis Ababa', '22 Bole Road',
             'hr@timebank.com', 'hr', '123456'),
            (1003, 'Admin Accountant', 'M', 101, 1, 'Accountant', 20000, '1982-03-10', 933445566, 'Addis Ababa',
             '22 Bole Road', 'accountant@timebank.com', 'accountant', '123456')
        ]
        cursor.executemany("""
        INSERT INTO employee (emp_id, emp_name, gender, dep_id, branch_id, job_title, salary, dbo, phone, city, address, email, username, passwords)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_employees)

        conn.commit()
        conn.close()


initialize_database()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time International Bank - Login")
        self.setFixedSize(400, 300)

        # Set window icon
        self.setWindowIcon(QIcon(":bank.png"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Title
        title_label = QLabel("Time International Bank")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 30px;")
        layout.addWidget(title_label)

        # Logo (placeholder)
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":bank.png").scaled(80, 80, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ddd;")
        form_layout.addRow("Username:", self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ddd;")
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        login_button.clicked.connect(self.authenticate)
        layout.addWidget(login_button)

        # Spacer
        layout.addStretch()

        # Footer
        footer_label = QLabel("© 2023 Time International Bank. All rights reserved.")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        layout.addWidget(footer_label)

        # Initialize main window reference
        self.main_window = None

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT emp_id, emp_name, dep_id, job_title FROM employee 
        WHERE username = ? AND passwords = ?
        """, (username, password))

        result = cursor.fetchone()
        conn.close()

        if result:
            emp_id, emp_name, dep_id, job_title = result

            # Determine dashboard based on department
            if dep_id == 107:  # HR
                self.main_window = HRDashboard(emp_id, emp_name)
            elif dep_id == 101:  # Accountant
                self.main_window = AccountantDashboard(emp_id, emp_name)
            elif dep_id == 102:  # Manager
                self.main_window = ManagerDashboard(emp_id, emp_name)
            else:
                QMessageBox.warning(self, "Access Denied", "Your role doesn't have access to any dashboard")
                return

            self.main_window.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")


class DashboardTemplate(QMainWindow):
    def __init__(self, emp_id, emp_name, title):
        super().__init__()
        self.emp_id = emp_id
        self.emp_name = emp_name
        self.setWindowTitle(f"Time International Bank - {title}")
        self.setMinimumSize(1000, 700)

        # Set window icon
        self.setWindowIcon(QIcon(":bank.png"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50; padding: 15px;")
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        # Bank logo and name
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":bank.png").scaled(40, 40, Qt.KeepAspectRatio))
        header_layout.addWidget(logo_label)

        bank_name = QLabel("Time International Bank")
        bank_name.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header_layout.addWidget(bank_name)

        header_layout.addStretch()

        # User info
        user_info = QLabel(f"{self.emp_name} (ID: {self.emp_id})")
        user_info.setStyleSheet("font-size: 14px; color: white;")
        header_layout.addWidget(user_info)

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)

        main_layout.addWidget(header)

        # Content area
        self.content_area = QWidget()
        main_layout.addWidget(self.content_area)

        # Footer
        footer = QLabel("© 2023 Time International Bank. All rights reserved.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 10px; color: #7f8c8d; padding: 10px;")
        main_layout.addWidget(footer)

    def logout(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


class HRDashboard(DashboardTemplate):
    def __init__(self, emp_id, emp_name):
        super().__init__(emp_id, emp_name, "HR Dashboard")

        # Content layout
        content_layout = QVBoxLayout()
        self.content_area.setLayout(content_layout)

        # Tabs
        tabs = QTabWidget()
        content_layout.addWidget(tabs)

        # Hire Employee Tab
        hire_tab = QWidget()
        hire_layout = QVBoxLayout()
        hire_tab.setLayout(hire_layout)

        # Hire form
        hire_form = QGroupBox("Hire New Employee")
        hire_form_layout = QFormLayout()
        hire_form.setLayout(hire_form_layout)

        self.emp_name_input = QLineEdit()
        self.emp_name_input.setPlaceholderText("Full Name")
        hire_form_layout.addRow("Full Name:", self.emp_name_input)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["M", "F"])
        hire_form_layout.addRow("Gender:", self.gender_combo)

        self.branch_combo = QComboBox()
        self.populate_branches()
        hire_form_layout.addRow("Branch:", self.branch_combo)

        self.job_title_combo = QComboBox()
        self.job_title_combo.addItems(["HR", "Accountant", "Manager", "Finance", "Security", "Cleaner"])
        self.job_title_combo.currentTextChanged.connect(self.update_salary)
        hire_form_layout.addRow("Job Title:", self.job_title_combo)

        self.salary_input = QLineEdit()
        self.salary_input.setReadOnly(True)
        hire_form_layout.addRow("Salary:", self.salary_input)

        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate().addYears(-20))
        hire_form_layout.addRow("Date of Birth:", self.dob_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        hire_form_layout.addRow("Phone:", self.phone_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City")
        hire_form_layout.addRow("City:", self.city_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")
        hire_form_layout.addRow("Address:", self.address_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        hire_form_layout.addRow("Email:", self.email_input)

        hire_button = QPushButton("Hire Employee")
        hire_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        hire_button.clicked.connect(self.hire_employee)
        hire_form_layout.addRow(hire_button)

        hire_layout.addWidget(hire_form)

        # Fire Employee Tab
        fire_tab = QWidget()
        fire_layout = QVBoxLayout()
        fire_tab.setLayout(fire_layout)

        # Fire form
        fire_form = QGroupBox("Fire Employee")
        fire_form_layout = QFormLayout()
        fire_form.setLayout(fire_form_layout)

        self.emp_id_input = QLineEdit()
        self.emp_id_input.setPlaceholderText("Employee ID")
        fire_form_layout.addRow("Employee ID:", self.emp_id_input)

        fire_button = QPushButton("Fire Employee")
        fire_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        fire_button.clicked.connect(self.fire_employee)
        fire_form_layout.addRow(fire_button)

        fire_layout.addWidget(fire_form)

        # Employee List Tab
        list_tab = QWidget()
        list_layout = QVBoxLayout()
        list_tab.setLayout(list_layout)

        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(8)
        self.employee_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Job Title", "Salary", "Branch", "Phone", "Email", "Status"])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.employee_table.setEditTriggers(QTableWidget.NoEditTriggers)

        list_layout.addWidget(self.employee_table)

        refresh_button = QPushButton("Refresh List")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_button.clicked.connect(self.populate_employee_table)
        list_layout.addWidget(refresh_button)

        # Add tabs
        tabs.addTab(hire_tab, "Hire Employee")
        tabs.addTab(fire_tab, "Fire Employee")
        tabs.addTab(list_tab, "Employee List")

        # Populate initial data
        self.populate_employee_table()

    def populate_branches(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT branch_id, branch_name FROM branch")
        branches = cursor.fetchall()
        conn.close()

        self.branch_combo.clear()
        for branch_id, branch_name in branches:
            self.branch_combo.addItem(branch_name, branch_id)

    def update_salary(self, job_title):
        salaries = {
            "HR": 15000,
            "Accountant": 20000,
            "Manager": 30000,
            "Finance": 15000,
            "Security": 5000,
            "Cleaner": 5000
        }
        self.salary_input.setText(f"{salaries.get(job_title, 0):,.2f}")

    def hire_employee(self):
        # Get all input values
        emp_name = self.emp_name_input.text()
        gender = self.gender_combo.currentText()
        branch_id = self.branch_combo.currentData()
        job_title = self.job_title_combo.currentText()
        salary = float(self.salary_input.text().replace(",", ""))
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        phone = self.phone_input.text()
        city = self.city_input.text()
        address = self.address_input.text()
        email = self.email_input.text()

        if not emp_name or not phone or not city or not address or not email:
            QMessageBox.warning(self, "Error", "Please fill all required fields")
            return

        # Determine department based on job title
        dep_id = {
            "HR": 107,
            "Accountant": 101,
            "Manager": 102,
            "Finance": 103,
            "Security": 104,
            "Cleaner": 105
        }.get(job_title, 101)

        # Generate random employee ID
        emp_id = random.randint(1000, 9999)

        # Generate random username and password
        username = f"{emp_name.split()[0].lower()}{random.randint(100, 999)}"
        password = str(random.randint(100000, 999999))

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Insert employee
            cursor.execute("""
            INSERT INTO employee (emp_id, emp_name, gender, dep_id, branch_id, job_title, salary, dbo, phone, city, address, email, username, passwords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (emp_id, emp_name, gender, dep_id, branch_id, job_title, salary, dob, phone, city, address, email,
                  username, password))

            # Insert into employee_branch
            cursor.execute("INSERT INTO employee_branch (emp_id, branch_id) VALUES (?, ?)", (emp_id, branch_id))

            # Log the action
            cursor.execute("""
            INSERT INTO employee_actions (emp_id, action_type, details)
            VALUES (?, ?, ?)
            """, (self.emp_id, "Hire", f"Hired {emp_name} as {job_title}"))

            conn.commit()

            # Show success message with credentials
            QMessageBox.information(
                self, "Employee Hired",
                f"Employee hired successfully!\n\nID: {emp_id}\nUsername: {username}\nPassword: {password}\n\nPlease provide these credentials to the employee."
            )

            # Clear form
            self.emp_name_input.clear()
            self.phone_input.clear()
            self.city_input.clear()
            self.address_input.clear()
            self.email_input.clear()

            # Refresh employee table
            self.populate_employee_table()

        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"Failed to hire employee: {str(e)}")
        finally:
            conn.close()

    def fire_employee(self):
        emp_id = self.emp_id_input.text()

        if not emp_id:
            QMessageBox.warning(self, "Error", "Please enter an employee ID")
            return

        try:
            emp_id = int(emp_id)
        except ValueError:
            QMessageBox.warning(self, "Error", "Employee ID must be a number")
            return

        # Confirm firing
        reply = QMessageBox.question(
            self, "Confirm Fire",
            f"Are you sure you want to fire employee ID {emp_id}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Get employee name before firing
            cursor.execute("SELECT emp_name FROM employee WHERE emp_id = ?", (emp_id,))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "Error", "Employee not found")
                return

            emp_name = result[0]

            # Fire employee (set job_title to NULL)
            cursor.execute("UPDATE employee SET job_title = NULL WHERE emp_id = ?", (emp_id,))

            # Log the action
            cursor.execute("""
            INSERT INTO employee_actions (emp_id, action_type, details)
            VALUES (?, ?, ?)
            """, (self.emp_id, "Fire", f"Fired {emp_name} (ID: {emp_id})"))

            conn.commit()

            QMessageBox.information(self, "Success", f"Employee {emp_name} (ID: {emp_id}) has been fired")

            # Clear input and refresh table
            self.emp_id_input.clear()
            self.populate_employee_table()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fire employee: {str(e)}")
        finally:
            conn.close()

    def populate_employee_table(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT e.emp_id, e.emp_name, e.job_title, e.salary, b.branch_name, e.phone, e.email, 
               CASE WHEN e.job_title IS NULL THEN 'Fired' ELSE 'Active' END as status
        FROM employee e
        LEFT JOIN branch b ON e.branch_id = b.branch_id
        ORDER BY e.emp_id
        """)

        employees = cursor.fetchall()
        conn.close()

        self.employee_table.setRowCount(len(employees))

        for row_idx, employee in enumerate(employees):
            for col_idx, value in enumerate(employee):
                if col_idx == 3:  # Salary column
                    item = QTableWidgetItem(f"{value:,.2f}")
                else:
                    item = QTableWidgetItem(str(value))

                item.setTextAlignment(Qt.AlignCenter)
                self.employee_table.setItem(row_idx, col_idx, item)


class AccountantDashboard(DashboardTemplate):
    def __init__(self, emp_id, emp_name):
        super().__init__(emp_id, emp_name, "Accountant Dashboard")

        # Content layout
        content_layout = QVBoxLayout()
        self.content_area.setLayout(content_layout)

        # Tabs
        tabs = QTabWidget()
        content_layout.addWidget(tabs)

        # Create Account Tab
        create_account_tab = QWidget()
        create_account_layout = QVBoxLayout()
        create_account_tab.setLayout(create_account_layout)

        # Create account form
        create_account_form = QGroupBox("Create New Account")
        form_layout = QFormLayout()
        create_account_form.setLayout(form_layout)

        self.cust_name_input = QLineEdit()
        self.cust_name_input.setPlaceholderText("Full Name")
        form_layout.addRow("Customer Name:", self.cust_name_input)

        self.cust_dob_input = QDateEdit()
        self.cust_dob_input.setCalendarPopup(True)
        self.cust_dob_input.setDate(QDate.currentDate().addYears(-20))
        form_layout.addRow("Date of Birth:", self.cust_dob_input)

        self.cust_phone_input = QLineEdit()
        self.cust_phone_input.setPlaceholderText("Phone Number")
        form_layout.addRow("Phone:", self.cust_phone_input)

        self.cust_city_input = QLineEdit()
        self.cust_city_input.setPlaceholderText("City")
        form_layout.addRow("City:", self.cust_city_input)

        self.cust_address_input = QLineEdit()
        self.cust_address_input.setPlaceholderText("Address")
        form_layout.addRow("Address:", self.cust_address_input)

        self.cust_email_input = QLineEdit()
        self.cust_email_input.setPlaceholderText("Email")
        form_layout.addRow("Email:", self.cust_email_input)

        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems(["Savings", "Checking", "Business"])
        form_layout.addRow("Account Type:", self.account_type_combo)

        self.initial_deposit_input = QLineEdit()
        self.initial_deposit_input.setPlaceholderText("0.00")
        form_layout.addRow("Initial Deposit:", self.initial_deposit_input)

        create_button = QPushButton("Create Account")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        create_button.clicked.connect(self.create_account)
        form_layout.addRow(create_button)

        create_account_layout.addWidget(create_account_form)

        # Transaction Tab
        transaction_tab = QWidget()
        transaction_layout = QVBoxLayout()
        transaction_tab.setLayout(transaction_layout)

        # Transaction form
        transaction_form = QGroupBox("Account Transactions")
        transaction_form_layout = QFormLayout()
        transaction_form.setLayout(transaction_form_layout)

        self.account_no_input = QLineEdit()
        self.account_no_input.setPlaceholderText("Account Number")
        transaction_form_layout.addRow("Account Number:", self.account_no_input)

        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems(["Deposit", "Withdrawal"])
        transaction_form_layout.addRow("Transaction Type:", self.transaction_type_combo)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        transaction_form_layout.addRow("Amount:", self.amount_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description (optional)")
        transaction_form_layout.addRow("Description:", self.description_input)

        transaction_button = QPushButton("Process Transaction")
        transaction_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        transaction_button.clicked.connect(self.process_transaction)
        transaction_form_layout.addRow(transaction_button)

        transaction_layout.addWidget(transaction_form)

        # Account Info Tab
        info_tab = QWidget()
        info_layout = QVBoxLayout()
        info_tab.setLayout(info_layout)

        # Account info form
        info_form = QGroupBox("Account Information")
        info_form_layout = QFormLayout()
        info_form.setLayout(info_form_layout)

        self.search_account_input = QLineEdit()
        self.search_account_input.setPlaceholderText("Account Number or Customer Name")
        info_form_layout.addRow("Search:", self.search_account_input)

        search_button = QPushButton("Search")
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_button.clicked.connect(self.search_account)
        info_form_layout.addRow(search_button)

        self.account_info_text = QTextEdit()
        self.account_info_text.setReadOnly(True)
        info_form_layout.addRow(self.account_info_text)

        self.transaction_history_table = QTableWidget()
        self.transaction_history_table.setColumnCount(5)
        self.transaction_history_table.setHorizontalHeaderLabels(["Date", "Type", "Amount", "Description", "Status"])
        self.transaction_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_history_table.setEditTriggers(QTableWidget.NoEditTriggers)

        info_form_layout.addRow(self.transaction_history_table)

        info_layout.addWidget(info_form)

        # Add tabs
        tabs.addTab(create_account_tab, "Create Account")
        tabs.addTab(transaction_tab, "Transactions")
        tabs.addTab(info_tab, "Account Info")

    def create_account(self):
        # Get customer details
        cust_name = self.cust_name_input.text()
        dob = self.cust_dob_input.date().toString("yyyy-MM-dd")
        phone = self.cust_phone_input.text()
        city = self.cust_city_input.text()
        address = self.cust_address_input.text()
        email = self.cust_email_input.text()
        account_type = self.account_type_combo.currentText()

        try:
            initial_deposit = float(self.initial_deposit_input.text())
        except ValueError:
            initial_deposit = 0.0

        if not cust_name or not phone or not city or not address or not email:
            QMessageBox.warning(self, "Error", "Please fill all required customer fields")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Generate customer ID
            cust_id = random.randint(10000, 99999)

            # Insert customer
            cursor.execute("""
            INSERT INTO customer (cust_id, cust_name, dob, phone, city, address, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cust_id, cust_name, dob, phone, city, address, email))

            # Generate account number
            account_no = random.randint(10000, 99999)

            # Insert account
            cursor.execute("""
            INSERT INTO accounts (account_no, cust_id, balance, account_type)
            VALUES (?, ?, ?, ?)
            """, (account_no, cust_id, initial_deposit, account_type))

            # If initial deposit > 0, create transaction
            if initial_deposit > 0:
                cursor.execute("""
                INSERT INTO transactions (account_no, transaction_type, transaction_amount, transaction_description, transaction_status)
                VALUES (?, ?, ?, ?, ?)
                """, (account_no, "Deposit", initial_deposit, "Initial deposit", "Completed"))

            conn.commit()

            QMessageBox.information(
                self, "Account Created",
                f"Account created successfully!\n\nCustomer ID: {cust_id}\nAccount Number: {account_no}\nAccount Type: {account_type}\nInitial Balance: {initial_deposit:,.2f}"
            )

            # Clear form
            self.cust_name_input.clear()
            self.cust_phone_input.clear()
            self.cust_city_input.clear()
            self.cust_address_input.clear()
            self.cust_email_input.clear()
            self.initial_deposit_input.clear()

        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"Failed to create account: {str(e)}")
        finally:
            conn.close()

    def process_transaction(self):
        account_no = self.account_no_input.text()
        transaction_type = self.transaction_type_combo.currentText()
        description = self.description_input.text()

        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount")
            return

        if not account_no:
            QMessageBox.warning(self, "Error", "Please enter an account number")
            return

        if amount <= 0:
            QMessageBox.warning(self, "Error", "Amount must be greater than 0")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Check if account exists
            cursor.execute("SELECT balance, account_status FROM accounts WHERE account_no = ?", (account_no,))
            account = cursor.fetchone()

            if not account:
                QMessageBox.warning(self, "Error", "Account not found")
                return

            balance, status = account

            if status != "Active":
                QMessageBox.warning(self, "Error", f"Account is {status}")
                return

            # Process transaction
            if transaction_type == "Withdrawal":
                if balance < amount:
                    QMessageBox.warning(self, "Error", "Insufficient funds")
                    return

                new_balance = balance - amount
            else:  # Deposit
                new_balance = balance + amount

            # Update account balance
            cursor.execute("UPDATE accounts SET balance = ? WHERE account_no = ?", (new_balance, account_no))

            # Record transaction
            cursor.execute("""
            INSERT INTO transactions (account_no, transaction_type, transaction_amount, transaction_description, transaction_status)
            VALUES (?, ?, ?, ?, ?)
            """, (account_no, transaction_type, amount, description, "Completed"))

            conn.commit()

            QMessageBox.information(
                self, "Transaction Successful",
                f"Transaction processed successfully!\n\nAccount: {account_no}\nType: {transaction_type}\nAmount: {amount:,.2f}\nNew Balance: {new_balance:,.2f}"
            )

            # Clear form
            self.amount_input.clear()
            self.description_input.clear()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process transaction: {str(e)}")
        finally:
            conn.close()

    def search_account(self):
        search_term = self.search_account_input.text()

        if not search_term:
            QMessageBox.warning(self, "Error", "Please enter search term")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Try to search by account number first
            if search_term.isdigit():
                cursor.execute("""
                SELECT a.account_no, c.cust_name, a.balance, a.account_type, a.opened_date, a.account_status
                FROM accounts a
                JOIN customer c ON a.cust_id = c.cust_id
                WHERE a.account_no = ?
                """, (int(search_term),))
            else:
                # Search by customer name
                cursor.execute("""
                SELECT a.account_no, c.cust_name, a.balance, a.account_type, a.opened_date, a.account_status
                FROM accounts a
                JOIN customer c ON a.cust_id = c.cust_id
                WHERE c.cust_name LIKE ?
                LIMIT 1
                """, (f"%{search_term}%",))

            account = cursor.fetchone()

            if not account:
                QMessageBox.warning(self, "Not Found", "No matching account found")
                return

            account_no, cust_name, balance, account_type, opened_date, status = account

            # Display account info
            info_text = f"""
            <b>Account Number:</b> {account_no}<br>
            <b>Customer Name:</b> {cust_name}<br>
            <b>Account Type:</b> {account_type}<br>
            <b>Status:</b> {status}<br>
            <b>Balance:</b> {balance:,.2f}<br>
            <b>Opened Date:</b> {opened_date}<br>
            """

            self.account_info_text.setHtml(info_text)

            # Load transaction history
            cursor.execute("""
            SELECT transaction_date, transaction_type, transaction_amount, transaction_description, transaction_status
            FROM transactions
            WHERE account_no = ?
            ORDER BY transaction_date DESC
            LIMIT 10
            """, (account_no,))

            transactions = cursor.fetchall()

            self.transaction_history_table.setRowCount(len(transactions))

            for row_idx, transaction in enumerate(transactions):
                for col_idx, value in enumerate(transaction):
                    if col_idx == 2:  # Amount column
                        item = QTableWidgetItem(f"{value:,.2f}")
                    else:
                        item = QTableWidgetItem(str(value))

                    item.setTextAlignment(Qt.AlignCenter)
                    self.transaction_history_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Search failed: {str(e)}")
        finally:
            conn.close()


class ManagerDashboard(DashboardTemplate):
    def __init__(self, emp_id, emp_name):
        super().__init__(emp_id, emp_name, "Manager Dashboard")

        # Content layout
        content_layout = QVBoxLayout()
        self.content_area.setLayout(content_layout)

        # Metrics display
        metrics_group = QGroupBox("Bank Metrics")
        metrics_layout = QVBoxLayout()
        metrics_group.setLayout(metrics_layout)

        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        metrics_layout.addWidget(self.metrics_text)

        refresh_button = QPushButton("Refresh Metrics")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_button.clicked.connect(self.update_metrics)
        metrics_layout.addWidget(refresh_button)

        content_layout.addWidget(metrics_group)

        # Recent transactions
        transactions_group = QGroupBox("Recent Transactions")
        transactions_layout = QVBoxLayout()
        transactions_group.setLayout(transactions_layout)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(
            ["Date", "Account", "Type", "Amount", "Description", "Status"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)

        transactions_layout.addWidget(self.transactions_table)

        content_layout.addWidget(transactions_group)

        # Employee actions
        actions_group = QGroupBox("Recent Employee Actions")
        actions_layout = QVBoxLayout()
        actions_group.setLayout(actions_layout)

        self.actions_table = QTableWidget()
        self.actions_table.setColumnCount(5)
        self.actions_table.setHorizontalHeaderLabels(["Date", "Employee ID", "Action", "Performed By", "Details"])
        self.actions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.actions_table.setEditTriggers(QTableWidget.NoEditTriggers)

        actions_layout.addWidget(self.actions_table)

        content_layout.addWidget(actions_group)

        # Load initial data
        self.update_metrics()
        self.update_recent_transactions()
        self.update_recent_actions()

    def update_metrics(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            # Get total employees
            cursor.execute("SELECT COUNT(*) FROM employee WHERE job_title IS NOT NULL")
            total_employees = cursor.fetchone()[0]

            # Get total accounts
            cursor.execute("SELECT COUNT(*) FROM accounts")
            total_accounts = cursor.fetchone()[0]

            # Get total balance
            cursor.execute("SELECT SUM(balance) FROM accounts")
            total_balance = cursor.fetchone()[0] or 0

            # Get employees by department
            cursor.execute("""
            SELECT d.dep_name, COUNT(e.emp_id) 
            FROM employee e
            JOIN department d ON e.dep_id = d.dep_id
            WHERE e.job_title IS NOT NULL
            GROUP BY d.dep_name
            """)
            dept_counts = cursor.fetchall()

            # Format metrics text
            metrics_text = f"""
            <h3>Bank Overview</h3>
            <p><b>Total Employees:</b> {total_employees:,}</p>
            <p><b>Total Accounts:</b> {total_accounts:,}</p>
            <p><b>Total Bank Balance:</b> {total_balance:,.2f}</p>

            <h3>Employees by Department</h3>
            """

            for dept, count in dept_counts:
                metrics_text += f"<p><b>{dept}:</b> {count:,}</p>"

            self.metrics_text.setHtml(metrics_text)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load metrics: {str(e)}")
        finally:
            conn.close()

    def update_recent_transactions(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT t.transaction_date, t.account_no, t.transaction_type, t.transaction_amount, 
                   t.transaction_description, t.transaction_status
            FROM transactions t
            ORDER BY t.transaction_date DESC
            LIMIT 10
            """)

            transactions = cursor.fetchall()

            self.transactions_table.setRowCount(len(transactions))

            for row_idx, transaction in enumerate(transactions):
                for col_idx, value in enumerate(transaction):
                    if col_idx == 3:  # Amount column
                        item = QTableWidgetItem(f"{value:,.2f}")
                    else:
                        item = QTableWidgetItem(str(value))

                    item.setTextAlignment(Qt.AlignCenter)
                    self.transactions_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load transactions: {str(e)}")
        finally:
            conn.close()

    def update_recent_actions(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT a.action_date, a.emp_id, a.action_type, e.emp_name, a.details
            FROM employee_actions a
            JOIN employee e ON a.emp_id = e.emp_id
            ORDER BY a.action_date DESC
            LIMIT 10
            """)

            actions = cursor.fetchall()

            self.actions_table.setRowCount(len(actions))

            for row_idx, action in enumerate(actions):
                for col_idx, value in enumerate(action):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.actions_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load employee actions: {str(e)}")
        finally:
            conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Set application font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    # Create and show login window
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())


    
