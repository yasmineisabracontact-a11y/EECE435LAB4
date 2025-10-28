import tkinter as tk
from tkinter import ttk

from src.storage.data_manager import DataManager
from src.core.modules import Student
from tkinter import messagebox

class StudentForm(ttk.Frame): #hold the student form user interface
    def __init__(self, master, dm:DataManager, student_table = None, **kwargs): # master is the main window, dm to store the new inputs. kwargs is for styling
        self.dm = dm
        self.student_table = student_table
        super().__init__(master, **kwargs) #initializing the frame


        #labels and entry fields
        # Student Name
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

        # Student ID 
        ttk.Label(self, text="Student ID").grid(row=3, column=0, sticky="w", pady=4)
        self.student_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.student_id_var, width=30).grid(row=3, column=1, sticky="ew", pady=4)

        # Submit button for student form
        submit_btn = ttk.Button(self, text="Add Student", command=self.add_student)
        submit_btn.grid(row=4, column=0, columnspan=2, pady=10)
        #command expects a collable that takes no parameters, tkinter will call this command when the submit button is pressed 
        self.columnconfigure(1, weight = 1)

        #method for the add button click
        
    def add_student(self):
        try:
            student = Student(
                name=self.name_var.get(),
                email=self.email_var.get(),
                age=int(self.age_var.get()),
                student_id=self.student_id_var.get(),
                registered_courses=[],
            )

            # Persist to DB and refresh in-memory snapshot
            self.dm.add_student_to_db(student)

            # Refresh the table from the updated snapshot
            if self.student_table:
                self.student_table.load_data()

            # Clear inputs
            self.name_var.set("")
            self.email_var.set("")
            self.age_var.set("")
            self.student_id_var.set("")

            messagebox.showinfo("Success", f"Student {student.name} added successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


        
        
