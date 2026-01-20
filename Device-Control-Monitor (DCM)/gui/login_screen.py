import tkinter as tk
from tkinter import messagebox
from helper.storage import save_json


# -----------------------------------------------------------------------------
# Helper functions - for registering a new user and validating an existing user
# -----------------------------------------------------------------------------
def register_user(users, username, password, data_path):
    # Check max user limit
    if len(users) >= 3:
        return False, "Maximum of 10 users allowed."

    # Check for duplicate usernames
    for u in users:
        if u["username"] == username:
            return False, "Sorry this username already exists."

    # Add new user
    new_user = {"username": username, "password": password}
    users.append(new_user)

    save_json(data_path, {"users": users})
    return True, "User registered successfully."


def validate_login(users, username, password):
    for u in users:
        if u["username"] == username and u["password"] == password:
            return True
    return False


# -----------------------------------------------------------------------------
# main class for the login screen frame
# -----------------------------------------------------------------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container for all widgets
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")

    
        tk.Label(
            container,
            text="Pacemaker DCM",
            font=("Arial", 20, "bold"),
        ).pack(pady=30)

        # Username entry
        tk.Label(container, text="Username:").pack()
        self.username_entry = tk.Entry(container, bg="#f5f5f5", fg="black", insertbackground="black", width=25)
        self.username_entry.pack(pady=5)

        # Password entry
        tk.Label(container, text="Password:").pack()
        self.password_entry = tk.Entry(container, show="*", bg="#f5f5f5", fg="black", insertbackground="black", width=25)
        self.password_entry.pack(pady=5)

        # Login and Register buttons
        tk.Button(container, text="Login", command=self.login, width=15, bg="#f5f5f5").pack(pady=10)
        tk.Button(container, text="Register", command=self.go_back, width=15, bg="#f5f5f5").pack()

    # -----------------------------------------------------------------------------
    # Helper function to go to register frame, and function to process login
    # -----------------------------------------------------------------------------
    def go_back(self):
        self.controller.show_frame("Register")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if validate_login(self.controller.data["users"], username, password):
            self.controller.active_user = username
            self.controller.show_frame("Dashboard")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
