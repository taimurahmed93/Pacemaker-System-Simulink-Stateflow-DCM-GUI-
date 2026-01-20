# ==============================================
# main.py for the DCM
# ==============================================

# Goal here is load the data from users.json
# initialize all the main frames needed (login, register, dashboard)
# be able to switch between which frame is visible to user
# have the mainloop running 

import tkinter as tk
import os
from helper.storage import load_json
from gui.login_screen import LoginFrame
from gui.register_screen import RegisterFrame
from gui.dashboard import Dashboard
from gui.egram_screen import EgramScreen


class DCMApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pacemaker DCM")
        self.root.geometry("400x550")
        self.active_user = None #start the program with no one logged in
        

        # Load data from the json file
        self.data_path = os.path.join("data", "users.json")
        self.data = load_json(self.data_path, {"users": []})

        # Container frame - essentially holding all frames as cards which can be cycled through
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize all GUI frames - for loop creates a new instance of each frame on startup
        # then places ontop of each other in the same spot using the grid function
        self.frames = {}
        for FrameClass in (LoginFrame, RegisterFrame, Dashboard, EgramScreen):
            name = FrameClass.__name__.replace("Frame", "")
            frame = FrameClass(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start at login screen
        self.show_frame("Login")

    def show_frame(self, name):   #function used to show which frame is visible
        frame = self.frames[name]
        frame.tkraise()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DCMApp()
    app.run()


