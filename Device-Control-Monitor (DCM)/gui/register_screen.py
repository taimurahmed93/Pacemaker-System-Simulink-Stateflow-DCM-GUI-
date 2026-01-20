import tkinter as tk
from tkinter import messagebox
from gui.login_screen import register_user  


# -----------------------------------------------------------------------------
# main class for the register screen frame
# -----------------------------------------------------------------------------
class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Center container
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")

        # Title Label
        tk.Label(
            container,
            text="Register New User",
            font=("Arial", 18, "bold"),
        ).pack(pady=30)

        # Username and Password entries
        tk.Label(container, text="Username:").pack()
        self.username_entry = tk.Entry(container, bg="#f5f5f5", fg="black", insertbackground="black", width=25)
        self.username_entry.pack(pady=5)

        tk.Label(container, text="Password:").pack()
        self.password_entry = tk.Entry(container, show="*", bg="#f5f5f5", insertbackground="black", fg="black", width=25)
        self.password_entry.pack(pady=5)

        # Register and Back buttons
        tk.Button(container, text="Register", command=self.register, width=15, bg="#f5f5f5").pack(pady=10)
        tk.Button(container, text="Back", command=self.go_back, width=15, bg="#f5f5f5").pack()

    # -----------------------------------------------------------------------------
    # Helper functions - for registering a new user and going back to the home screen
    # -----------------------------------------------------------------------------
    def go_back(self):
        self.controller.show_frame("Login")  # take user back to the login home screen

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # -------------------------------------------------------------------------
        # Simple input validation
        # -------------------------------------------------------------------------
        if len(username) == 0 or len(password) == 0:
            messagebox.showerror("Invalid Input", "Username and password cannot be empty.")
            return
        
        if len(username) < 3 or len(password) < 3:
            messagebox.showerror("Invalid Input", "Username and password must be at least 3 characters long.")
            return

        # -------------------------------------------------------------------------
        # Attempt to register user if input passes validation
        # -------------------------------------------------------------------------
        success, message = register_user(
            self.controller.data["users"], username, password, self.controller.data_path
        )

        if success:
            messagebox.showinfo("Success", message)
            self.controller.show_frame("Login")
        else:
            messagebox.showerror("Error", message)
