import tkinter as tk
from tkinter import ttk

from src.core.modules import Course
from src.storage.data_manager import DataManager
from tkinter import messagebox

class CourseForm(ttk.Frame):
    def __init__(self, master, dm:DataManager, course_table = None, **kwargs): # master is the main window, dm to store the new inputs. kwargs is for styling
        
        self.dm = dm
        self.course_table = course_table
        super().__init__(master, **kwargs) #initializing the frame
        #labels and entry fields
        # Course Name
        ttk.Label(self, text="Course Name").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="ew", pady=4)
        # Course ID 
        ttk.Label(self, text="Course ID").grid(row=3, column=0, sticky="w", pady=4)
        self.course_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.course_id_var, width=30).grid(row=3, column=1, sticky="ew", pady=4)

        # Submit button for course form
        submit_btn = ttk.Button(self, text="Add Course", command=self.add_course)
        submit_btn.grid(row=4, column=0, columnspan=2, pady=10)
        #command expects a collable that takes no parameters, tkinter will call this command when the submit button is pressed 
        self.columnconfigure(1, weight = 1)  

    def add_course(self):
        try:
            course = Course(
                course_id=self.course_id_var.get(),
                course_name=self.name_var.get(),
                course_instructor=None,
                enrolled_students=[],
            )

            # Persist to DB and refresh snapshot
            self.dm.add_course_to_db(course)

            # Refresh table
            if self.course_table:
                self.course_table.load_data()

            # Clear inputs
            self.name_var.set("")
            self.course_id_var.set("")
            messagebox.showinfo("Success", f"Course {course.course_name} added successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
 
