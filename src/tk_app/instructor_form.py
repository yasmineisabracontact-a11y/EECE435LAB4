import tkinter as tk
from tkinter import ttk

from src.storage.data_manager import DataManager
from src.core.modules import Instructor
from src.core.modules import Course
from tkinter import messagebox

class InstructorForm(ttk.Frame):
    def __init__(self, master, dm: DataManager, instructor_table=None, course_table= None, **kwargs):
        self.dm = dm
        self.instructor_table = instructor_table
        super().__init__(master, **kwargs)  # now safe, kwargs no longer contains instructor_table

        #labels and entry fields
        # Instructor Name
        ttk.Label(self, text="Name").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="ew", pady=4)

        # Email
        ttk.Label(self, text="Email").grid(row=1, column=0, sticky="w", pady=4)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var, width=30).grid(row=1, column=1, sticky="ew", pady=4)

        # Age
        ttk.Label(self, text="Age").grid(row=2, column=0, sticky="w", pady=4)
        self.age_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.age_var, width=30).grid(row=2, column=1, sticky="ew", pady=4)

        # Instructor ID 
        ttk.Label(self, text="Instructor ID").grid(row=3, column=0, sticky="w", pady=4)
        self.instructor_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.instructor_id_var, width=30).grid(row=3, column=1, sticky="ew", pady=4)

        # Submit button for instructor form
        submit_btn = ttk.Button(self, text="Add Instructor", command=self.add_instructor)
        submit_btn.grid(row=4, column=0, columnspan=2, pady=10)
        #command expects a collable that takes no parameters, tkinter will call this command when the submit button is pressed 
        self.columnconfigure(1, weight = 1)    
    def add_instructor(self):
        try:
            instructor = Instructor(
                instructor_id=self.instructor_id_var.get(),
                name=self.name_var.get(),
                email=self.email_var.get(),
                age=int(self.age_var.get()),
                assigned_courses=[],
            )

            # Persist to DB and refresh snapshot
            self.dm.add_instructor_to_db(instructor)

            # Refresh table
            if self.instructor_table:
                self.instructor_table.load_data()

            # Clear inputs
            self.name_var.set("")
            self.email_var.set("")
            self.age_var.set("")
            self.instructor_id_var.set("")
            messagebox.showinfo("Success", f"Instructor {instructor.name} added successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
