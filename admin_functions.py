import sqlite3
from datetime import datetime
from view_table import fetch_loans


def adapt_datetime(dt_obj):
    return dt_obj.strftime('%Y-%m-%d %H:%M:%S')


# Custom converter to convert string to datetime when retrieving from the database
def convert_datetime(text):
    return datetime.strptime(text.decode(), '%Y-%m-%d %H:%M:%S')


# Register the adapters and converters with SQLite
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)

conn = sqlite3.connect('bank_application.db')
cursor = conn.cursor()

Security_Question = [
    "What is your pet's name?",
    "What school did you go to?",
    "Where were you born?",
    "What is your last name?"
]
current_user_id = None


def generate_admin_id():
    cursor.execute("SELECT id FROM Admin ORDER BY id DESC LIMIT 1")
    last_admin = cursor.fetchone()

    if last_admin:
        last_id_num = int(last_admin[0][3:])  # Extract the numeric part from 'ADM0001'
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # If no admins exist, start with 1

    # Format the new ID as 'ADM0001', 'ADM0002', etc.
    new_admin_id = f"ADM{new_id_num:04d}"
    return new_admin_id


# done by admin
def add_admin(current_admin_id):
    """
    Allows a super admin to add a new admin.
    """
    # Check if the current admin is active and a super admin
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to add records. Admin status is inactive.")
        return

    if admin[0] != 'Super Admin':
        print("Only Super Admins can add other admins.")
        return

    # Proceed to add new admin
    admin_id = generate_admin_id()
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    role = input("Enter admin role (default is 'Admin'): ") or 'Admin'
    status = input("Enter admin status (active/inactive): ")

    while True:
        password = input("Enter your password: ")
        confirm_password = input("Confirm your password: ")
        if password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")

    # Insert data into Admin table
    cursor.execute('''
        INSERT INTO Admin (id, name, email, password, role, status, last_login, created_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (admin_id, name, email, password, role, status))

    conn.commit()
    print("Admin added successfully.")


# Function to add a User
def generate_user_id():
    cursor.execute("SELECT id FROM Users ORDER BY id DESC LIMIT 1")
    last_user = cursor.fetchone()

    if last_user:
        last_id_num = int(last_user[0][2:])  # Extract the numeric part from 'US0001'
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # If no users exist, start with 1

    # Format the new ID as 'US0001', 'US0002', etc.
    new_user_id = f"US{new_id_num:04d}"
    return new_user_id


# done by user
def add_user(current_admin_id):
    """
    Allows an active admin to add a new user.
    """
    # Check if the current admin is active
    cursor.execute("SELECT status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You do not have permission to add users. Admin status is inactive.")
        return

    # Proceed to add new user
    print("Enter user details in the prompt below")
    user_id = generate_user_id()
    name = input("Enter user name: ")
    email = input("Enter user email: ")
    contact_info = input("Enter user contact info: ")
    date_of_birth = input("Enter date of birth (YYYY-MM-DD, optional): ")
    account_status = 'inactive'  # User account starts as inactive until verified
    user_role = 'user'
    is_verified = 0
    preferred_language = 'en'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Security question selection
    print("\nChoose your preferred security question:")
    for index, question in enumerate(Security_Question, start=1):
        print(f"{index}. {question}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(Security_Question):
                security_question = Security_Question[choice]
                break
            else:
                print("Invalid choice, please select a valid number.")
        except ValueError:
            print("Please enter a number.")

    security_answer = input("Enter your security answer: ")

    # Password validation loop
    while True:
        password = input("Enter your password: ")
        confirm_password = input("Confirm your password: ")
        if password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")

    # Insert data into Users table
    cursor.execute('''
        INSERT INTO Users (id, name, email, contact_info, password, account_status, 
                           user_role, is_verified, preferred_language, date_of_birth, 
                           last_login, security_question, security_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, email, contact_info, password, account_status, user_role, is_verified,
          preferred_language, date_of_birth, date, security_question, security_answer))

    conn.commit()
    print("User added successfully. Account is inactive until verified.")


def generate_account_id():
    cursor.execute("SELECT id FROM Bank_Accounts ORDER BY id DESC LIMIT 1")
    last_account = cursor.fetchone()

    if last_account:
        last_id_num = int(last_account[0][2:])  # Extract the numeric part from 'ADM0001'
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # If no admins exist, start with 1

    new_account_id = f"BA{new_id_num:04d}"
    return new_account_id


# done by admin
def create_bank_account(current_admin_id):
    """
    Allows an active admin to create a new bank account for a user.
    """
    # Check if the current admin is active
    cursor.execute("SELECT status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You do not have permission to add bank accounts. Admin status is inactive.")
        return

    # Proceed to create new bank account
    account_id = generate_account_id()
    user_id = input("Enter the user id for the account: ")
    account_type = input("Enter the type of account (e.g., Saving, Checking): ")
    admin_id = current_admin_id
    balance = input("Enter the initial deposit: ")
    credit_amount = input("Enter the initial credit given: ")
    account_status = 'inactive'  # Default status for newly created accounts
    date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert into the Bank_Accounts table without specifying recent_transaction
    cursor.execute('''
        INSERT INTO Bank_Accounts (id, account_holder, created_by, account_type, account_status, balance, 
                                   transaction_date, credit_amount, date_created)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
    ''', (account_id, user_id, admin_id, account_type, account_status, balance,
          credit_amount, date_created))

    conn.commit()
    print("Bank account created successfully.")


def delete_admin_record(current_admin_id):
    """
    Deletes a record from the Admin table based on the admin ID. Only Super Admins can delete admin records.
    """
    # Check if the current admin is active and a super admin
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to delete records. Admin status is inactive.")
        return

    if admin[0] != 'super':
        print("Only Super Admins can delete admin records.")
        return

    # Get admin ID to delete
    admin_id = input("Enter the Admin ID to delete: ")

    # Check if the admin record exists
    cursor.execute("SELECT id FROM Admin WHERE id = ?", (admin_id,))
    admin_record = cursor.fetchone()

    if not admin_record:
        print("Admin record not found.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete Admin ID {admin_id}? (yes/no): ").lower()
    if confirmation != 'yes':
        print("Operation cancelled.")
        return

    # Delete the admin record
    cursor.execute("DELETE FROM Admin WHERE id = ?", (admin_id,))
    conn.commit()

    print(f"Admin record with ID {admin_id} has been successfully deleted.")


def delete_user_record(current_admin_id):
    """
    Deletes a record from the Users table based on the user ID. Super and Management Admins can delete user records.
    """
    # Check if the current admin is active
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to delete records. Admin status is inactive.")
        return

    # Get user ID to delete
    user_id = input("Enter the User ID to delete: ")

    # Check if the user record exists
    cursor.execute("SELECT id FROM Users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        print("User record not found.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete User ID {user_id}? (yes/no): ").lower()
    if confirmation != 'yes':
        print("Operation cancelled.")
        return

    # Delete the user record
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    conn.commit()

    print(f"User record with ID {user_id} has been successfully deleted.")


def delete_bank_account(current_admin_id):
    """
    Deletes a record from the Bank_Accounts table based on the account ID.
    Super and Management Admins can delete bank account records.
    """
    # Check if the current admin is active
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to delete records. Admin status is inactive.")
        return

    # Get bank account ID to delete
    account_id = input("Enter the Bank Account ID to delete: ")

    # Check if the bank account record exists
    cursor.execute("SELECT id FROM Bank_Accounts WHERE id = ?", (account_id,))
    account = cursor.fetchone()

    if not account:
        print("Bank account record not found.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete Bank Account ID {account_id}? (yes/no): ").lower()
    if confirmation != 'yes':
        print("Operation cancelled.")
        return

    # Delete the bank account record
    cursor.execute("DELETE FROM Bank_Accounts WHERE id = ?", (account_id,))
    conn.commit()

    print(f"Bank account with ID {account_id} has been successfully deleted.")


def activate_accounts():
    # Ensure the admin performing the action is active and get their role
    cursor.execute("SELECT status, role FROM Admin WHERE id = ?", (current_user_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You are not authorized to perform this action or your account is inactive.")
        return

    role = input("Enter the type of account to activate (Admin/User/Bank Account): ").strip().lower()
    account_id = input(f"Enter the {role.capitalize()} ID to activate: ")

    if role == 'admin':
        # Check if the current admin has super privileges
        if admin[1] != 'super':
            print("Only super admins are allowed to activate other admin accounts.")
            return

        cursor.execute('SELECT status FROM Admin WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'active':
            confirmation = input(f"Are you sure you want to activate admin {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Admin
                    SET status = 'active'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Admin account {account_id} has been activated.")
            else:
                print("Action canceled.")
        else:
            print(f"Admin account {account_id} is already active or does not exist.")

    elif role == 'user':
        cursor.execute('SELECT account_status FROM Users WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'active':
            confirmation = input(f"Are you sure you want to activate user {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Users
                    SET account_status = 'active'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"User account {account_id} has been activated.")
            else:
                print("Action canceled.")
        else:
            print(f"User account {account_id} is already active or does not exist.")

    elif role == 'bank account' or role == 'bank':
        cursor.execute('SELECT account_status FROM Bank_Accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'active':
            confirmation = input(
                f"Are you sure you want to activate bank account {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Bank_Accounts
                    SET account_status = 'active'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Bank account {account_id} has been activated.")
            else:
                print("Action canceled.")
        else:
            print(f"Bank account {account_id} is already active or does not exist.")

    else:
        print("Invalid account type. Please enter 'Admin', 'User', or 'Bank Account'.")


def deactivate_accounts():
    # Ensure the admin performing the action is active and get their role
    cursor.execute("SELECT status, role FROM Admin WHERE id = ?", (current_user_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You are not authorized to perform this action or your account is inactive.")
        return

    role = input("Enter the type of account to deactivate (Admin/User/Bank Account): ").strip().lower()
    account_id = input(f"Enter the {role.capitalize()} ID to deactivate: ")

    if role == 'admin':
        # Check if the current admin has super privileges
        if admin[1] != 'super':
            print("Only super admins are allowed to deactivate other admin accounts.")
            return

        cursor.execute('SELECT status FROM Admin WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'inactive':
            confirmation = input(f"Are you sure you want to deactivate admin {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Admin
                    SET status = 'inactive'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Admin account {account_id} has been deactivated.")
            else:
                print("Action canceled.")
        else:
            print(f"Admin account {account_id} is already inactive or does not exist.")

    elif role == 'user':
        cursor.execute('SELECT account_status FROM Users WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'inactive':
            confirmation = input(f"Are you sure you want to deactivate user {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Users
                    SET account_status = 'inactive'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"User account {account_id} has been deactivated.")
            else:
                print("Action canceled.")
        else:
            print(f"User account {account_id} is already inactive or does not exist.")

    elif role == 'bank account' or role == 'bank':
        cursor.execute('SELECT account_status FROM Bank_Accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'inactive':
            confirmation = input(
                f"Are you sure you want to deactivate bank account {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Bank_Accounts
                    SET account_status = 'inactive'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Bank account {account_id} has been deactivated.")
            else:
                print("Action canceled.")
        else:
            print(f"Bank account {account_id} is already inactive or does not exist.")

    else:
        print("Invalid account type. Please enter 'Admin', 'User', or 'Bank Account'.")


def manage_password():
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_user_id,))
    user_role = cursor.fetchall()

    if user_role[0][1] != 'inactive':

        choice = input("Do you want to change or reset the password: ")
        if choice == 'reset':
            choice = input("Enter the user id of the account you want to reset: ")
            if user_role[0][0] == 'super':

                while True:
                    new_password = input("Enter your new password: ")
                    confirm_password = input("Re-enter your password: ")
                    print(choice)
                    if new_password != confirm_password:
                        print("Passwords do not match")
                    else:
                        if choice[:2] == 'US':
                            cursor.execute("""UPDATE Users SET password = ? Where id = ?"""
                                           , (new_password, choice,))
                            print("Password reset successfully")
                            break
                        elif choice[:2] == 'AD':
                            cursor.execute("""UPDATE Admin SET password = ? where id = ?"""
                                           , (new_password, choice))
                            print("Password reset successfully")
                            break
            elif user_role[0][0] == 'management':
                while True:
                    if choice[:2] == 'AD':
                        print("You dont have the authority to change another admins password")
                        break

                    elif choice[:2] == 'US':
                        while True:
                            new_password = input("Enter your new password: ")
                            confirm_password = input("Re-enter your password: ")
                            if new_password != confirm_password:
                                print("Passwords do not match")
                            else:
                                cursor.execute("""UPDATE Users SET password = ? Where id = ?"""
                                               , (new_password, choice,))
                                print("Password reset successfully")
                                break
        elif choice == 'change':
            user_account = input("Which account do you want to update (user/admin): ").capitalize()
            # Check if the user is super admin and account is 'admin'
            if user_role[0][0] == 'super' and user_account == 'Admin':
                user_id = input("Enter the user id of the admin account: ")
                cursor.execute("SELECT password FROM Admin WHERE id = ?", (user_id,))
                password = cursor.fetchone()
                if password:
                    # Prompt for the current password to validate
                    current_password = input("Enter the current password of the admin account: ")
                    if current_password == password[0]:
                        # Prompt for the new password
                        new_password = input("Enter the new password: ")
                        confirm_password = input("Re-enter the password: ")
                        # Check if the new password matches the confirmation
                        if confirm_password != new_password:
                            print("Password mismatch!")
                        else:
                            # Update the admin's password in the database
                            cursor.execute("UPDATE Admin SET password = ? WHERE id = ?", (new_password, user_id))
                            conn.commit()
                            print("Admin password changed successfully.")
                    else:
                        print("Current password is incorrect.")
                else:
                    print(f"Admin with id {user_id} not found.")
            # Check if the user is a super admin or management admin and the account is 'user'
            elif (user_role[0][0] == 'super' or user_role[0][0] == 'management') and user_account == 'User':
                user_id = input("Enter the user id of the user account: ")
                cursor.execute("SELECT password FROM Users WHERE id = ?", (user_id,))
                password = cursor.fetchone()
                if password:
                    # Prompt for the current password to validate
                    current_password = input("Enter the current password of the user account: ")
                    if current_password == password[0]:
                        # Prompt for the new password
                        new_password = input("Enter the new password: ")
                        confirm_password = input("Re-enter the password: ")
                        # Check if the new password matches the confirmation
                        if confirm_password != new_password:
                            print("Password mismatch!")
                        else:
                            # Update the user's password in the database
                            cursor.execute("UPDATE Users SET password = ? WHERE id = ?", (new_password, user_id))
                            conn.commit()
                            print("User password changed successfully.")
                    else:
                        print("Current password is incorrect.")
                else:
                    print(f"User with id {user_id} not found.")
            else:
                print("You do not have the permission to change this account.")
        else:
            print("Invalid Choice")
    else:
        print("you cant update password because your account is inactive")
    conn.commit()


def approve_or_reject_loan():
    """
    Allows the admin to approve or reject a loan.
    """
    fetch_loans()
    loan_id = input("Enter the loan ID to process: ")
    account = input("Enter the account to credit: ")

    cursor.execute('''
            SELECT loan_id, user_id, loan_amount, loan_status, loan_type, date_approved, loan_balance
            FROM Loans WHERE loan_id =?
        ''', loan_id)
    loan = cursor.fetchone()

    if not loan:
        print("Invalid loan ID. Please enter a valid loan ID.")
        return

    loan_id, account_id, loan_amount, loan_status, loan_type, date_approved, loan_balance = loan

    # Ensure that date_applied and date_approved are in the correct format

    if loan_status != "Pending":
        print(f"Loan {loan_id} has already been processed. Current status: {loan_status}")
        return

    print(f"Loan ID: {loan_id}, Account ID: {account_id}, Loan Amount: {loan_amount}, Status: {loan_status}")
    decision = input("Approve or Reject loan? (A/R): ").strip().upper()

    if decision == "A":
        # Approve the loan
        date_approved = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update loan status and loan balance
        cursor.execute('''
            UPDATE Loans
            SET loan_status = 'Approved', date_approved = ?, loan_balance = ?
            WHERE loan_id = ?
        ''', (date_approved, loan_balance, loan_id))

        # Add loan amount to the account balance
        cursor.execute('''UPDATE Bank_Accounts SET balance = balance + ? WHERE id = ?''',
                       (loan_amount, account))

        conn.commit()
        print(f"Loan {loan_id} approved. Amount {loan_amount} has been credited to account {account_id}.")
    elif decision == "R":
        # Reject the loan
        cursor.execute('''
            UPDATE Loans
            SET loan_status = 'Rejected'
            WHERE loan_id = ?
        ''', (loan_id,))

        conn.commit()
        print(f"Loan {loan_id} has been rejected.")
    else:
        print("Invalid input. Please enter 'A' to approve or 'R' to reject.")

    print(loan)


def check_credentials(table_name, user_id, password):
    cursor.execute(f"SELECT id, password FROM {table_name} WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    return user and user[1] == password  # Return True if credentials are valid


def login_menu():
    global current_user_id  # Use global variable to track the current user
    print("Welcome! Please log in.")
    while True:
        user_id = input("Enter your ID: ")
        current_user_id = user_id

        password = input("Enter your password: ")

        # Check if the user is an admin
        if check_credentials("Admin", user_id, password):
            print("\nLogin successful as Admin!")
            current_user_id = user_id  # Store the logged-in admin ID
            admin_menu()  # Redirect to admin menu
        # Check if the user is a normal user
        elif check_credentials("Users", user_id, password):
            print("\nLogin successful as User!")
            current_user_id = user_id  # Store the logged-in user ID
            # user_menu()  # Redirect to user menu
        else:
            print("\nInvalid ID or password. Please try again.")


def admin_menu():
    while True:
        print(f"\nWelcome to the User menu! Logged in as User ID: {current_user_id}")
        choice = input("""
                1. add accounts
                2. delete accounts
                3. activate accounts
                4. deactivate accounts
                5. update accounts
                6. change/reset passwords
                7. update exchange rates
                8. approve/reject loans                
                9. Exit
                Enter your choice: """)
        if choice == '1':
            choice = input("1. User account \n2. Admin account \n3. Bank account \n4. Exit: ")
            if choice == '1':
                add_user(current_user_id)
            elif choice == '2':
                add_admin(current_user_id)
            elif choice == '3':
                create_bank_account(current_user_id)
            elif choice == '4':
                break
            else:
                print("invalid entry!")
        elif choice == '2':
            choice = input("1. User account \n2. Admin account \n3. Bank account \n4. Exit: ")
            if choice == '1':
                delete_user_record(current_user_id)
            elif choice == '2':
                delete_admin_record(current_user_id)
            elif choice == '3':
                delete_bank_account(current_user_id)
            elif choice == '4':
                break
            else:
                print("invalid entry!")

        elif choice == '3':
            activate_accounts()

        elif choice == '4':
            deactivate_accounts()
        elif choice == '5':
            print("Updating accounts... ")
            print(current_user_id)

        elif choice == '6':
            '''role = input("Enter your role: ")
            target_role = input("Enter the account to update: ")
            target_id = input("Enter the user id of the account to update: ")
            choice = input("Do you want to reset or update the account? ")'''
            if choice == 'reset':
                reset = True
            else:
                reset = False

            manage_password()

        elif choice == '7':
            print("updating exchange rated")
        elif choice == '8':
            print("Loan application")
            approve_or_reject_loan()
        elif choice == '9':
            break
        else:
            print("invalid entry. Try again")


login_menu()
