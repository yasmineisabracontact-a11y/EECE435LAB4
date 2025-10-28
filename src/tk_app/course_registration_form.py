import tkinter as tk
from tkinter import ttk, messagebox
from src.storage.data_manager import DataManager

class CourseRegistrationForm(ttk.Frame):
    def __init__(self, master, dm: DataManager, student_table=None, course_table=None, **kwargs):
        self.dm = dm
        self.student_table = student_table
        self.course_table = course_table
        super().__init__(master, **kwargs)

        ttk.Label(self, text="Student ID").grid(row=0, column=0, sticky="w", pady=4)
        self.student_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.student_id_var, width=30).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Register for Course").grid(row=1, column=0, sticky="w", pady=4)
        self.course_var = tk.StringVar()
        self.course_dropdown = ttk.Combobox(self, textvariable=self.course_var, state="readonly")
        self.course_dropdown.grid(row=1, column=1, sticky="ew", pady=4)
        self.course_dropdown.bind("<Button-1>", self.update_courses)

        register_btn = ttk.Button(self, text="Register Course", command=self.register_course)
        register_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)

        # Initial mapping
        self.update_courses()

    def update_courses(self, event=None):
        """Refresh the dropdown list from the in-memory snapshot (kept in sync with DB)."""
        # Prefer the current snapshot so UI objects stay consistent with tables
        courses = self.dm.courses_data or self.dm.load_courses_from_db()
        self.course_map = {c.course_name: c for c in courses}
        self.course_dropdown["values"] = list(self.course_map.keys())
        if not self.course_var.get():
            self.course_dropdown.set("Select a Course")

    def register_course(self):
        try:
            student_id = self.student_id_var.get().strip()
            course_name = self.course_var.get().strip()

            if not student_id or course_name == "Select a Course":
                raise ValueError("Please enter a valid Student ID and select a Course.")

            # Resolve course from current snapshot
            matched_course = self.course_map.get(course_name)
            if matched_course is None:
                raise ValueError("Course not found.")

            # Use atomic DB operation that merges registrations and refreshes snapshot
            self.dm.register_student_in_course(student_id, matched_course.course_id)

            # Refresh tables from the updated snapshot
            if self.student_table:
                self.student_table.load_data()
            if self.course_table:
                self.course_table.load_data()

            messagebox.showinfo("Success", f"Student {student_id} registered in {matched_course.course_name} successfully.")

            # Clear input fields
            self.student_id_var.set("")
            self.course_dropdown.set("Select a Course")

        except Exception as e:
            messagebox.showerror("Error", str(e))
