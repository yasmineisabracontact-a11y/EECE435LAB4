import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.storage.data_manager import DataManager

class CourseAssignmentForm(ttk.Frame):
    def __init__(self, master, dm: DataManager, course_table = None, instructor_table = None, **kwargs):
        
        self.dm = dm
        self.course_table = course_table
        self.instructor_table = instructor_table
        super().__init__(master, **kwargs)
        # Instructor ID
        
        ttk.Label(self, text="Instructor ID").grid(row=0, column=0, sticky="w", pady=4)
        self.instructor_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.instructor_id_var, width=30).grid(row=0, column=1, sticky="ew", pady=4)

        # Course dropdown
        ttk.Label(self, text="Assign to Course").grid(row=1, column=0, sticky="w", pady=4)
        self.course_var = tk.StringVar()
        self.course_dropdown = ttk.Combobox(self, textvariable=self.course_var, state="readonly")
        self.course_dropdown.grid(row=1, column=1, sticky="ew", pady=4)


        # mapping 
        self.course_map = {}
        for course in self.dm.courses_data:
            self.course_map[course.course_name] = course
        self.course_dropdown["values"] = list(self.course_map.keys())
        self.course_dropdown.set("Select a Course")

        # Assign button
        assign_btn = ttk.Button(self, text="Assign Course", command=self.assign_course)
        assign_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)
        self.course_dropdown.bind("<Button-1>", self.update_courses)

    def update_courses(self, event=None):
            self.course_map = {c.course_name: c for c in self.dm.courses_data}
            self.course_dropdown["values"] = list(self.course_map.keys())

    def assign_course(self):
        try:         
            # Resolve selected course from mapping
            input_course_name = self.course_var.get()
            matched_course = self.course_map.get(input_course_name)
            if matched_course is None:
                raise ValueError("Course not found")

            # Instructor ID from input
            input_instructor_id = self.instructor_id_var.get().strip()
            if not input_instructor_id:
                raise ValueError("Please enter an Instructor ID")

            # Atomic DB update (keeps both sides in sync and refreshes snapshot)
            self.dm.assign_instructor_to_course(input_instructor_id, matched_course.course_id)

            # Refresh the tables using the updated snapshot
            if self.instructor_table:
                self.instructor_table.load_data()
            if self.course_table:
                self.course_table.load_data()

            messagebox.showinfo("Success", f"Instructor {input_instructor_id} assigned to {matched_course.course_name}")
            self.instructor_id_var.set("")
            self.course_dropdown.set("Select a Course")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
