#GUI HELPERS
import tkinter as tk
from tkinter import messagebox

# Helper functions to create labeled entries and buttons
def create_labeled_entry(parent, label_text, row, entry_dict, read_only=False, dropdown_values=None):
    # Create label and entry, store entry in the provided dictionary
    label = tk.Label(parent, text=label_text)
    label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
    
    if dropdown_values:
        # Create a dropdown (combobox)
        var = tk.StringVar()
        import tkinter.ttk as ttk
        dropdown = ttk.Combobox(parent, textvariable=var, values=dropdown_values, state="readonly")
        dropdown.grid(row=row, column=1, padx=5, pady=5)
        entry_dict[label_text] = dropdown   # store combobox instead of entry
        return dropdown
    
    entry = tk.Entry(parent, bg="#f8f8f8", fg="black", insertbackground="black")
    entry.grid(row=row, column=1, padx=5, pady=5)
    
    # Set entry to read-only if specified
    if read_only:
        entry.config(state="disabled")
    entry_dict[label_text] = entry

# Create footer buttons
def create_footer_buttons(parent, dashboard):
    # Create buttons and link them to dashboard methods
    tk.Button(parent, text="New Patient", command=dashboard.clear_fields).grid(row=0, column=0, padx=5)
    tk.Button(parent, text="Save Patient", command=dashboard.save_patient).grid(row=0, column=1, padx=5)
    tk.Button(parent, text="Remove Patient", command=dashboard.remove_patient).grid(row=0, column=2, padx=5)
    tk.Button(parent, text="Clock", command=dashboard.show_clock).grid(row=0, column=3, padx=5)
    tk.Button(parent, text="About", command=dashboard.show_about).grid(row=0, column=4, padx=5)
    tk.Button(parent, text="Logout", command=lambda: dashboard.controller.show_frame("Login"), fg="black").grid(row=0, column=5, padx=5)

# Refresh patient dropdown menu
def refresh_patient_dropdown(dashboard):
    menu = dashboard.patient_dropdown["menu"]
    menu.delete(0, "end")
    
    # placeholder if no patients exist
    if not dashboard.patients:
        dashboard.patient_var.set("No patients found")
        return
    
    # populate dropdown with patient names
    for p in dashboard.patients:
        name = p.get("name", "Unnamed")
        menu.add_command(label=name, command=lambda n=name: dashboard.load_selected_patient(n))
        
    # set the currently loaded patient in the dropdown, and load their data once selected
    if dashboard.patient:
        dashboard.patient_var.set(dashboard.patient.get("name", ""))
    else:
        first_name = dashboard.patients[0].get("name", "")
        dashboard.patient_var.set(first_name)
        dashboard.load_selected_patient(first_name)
