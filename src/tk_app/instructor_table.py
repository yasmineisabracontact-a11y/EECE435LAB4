import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from src.storage.data_manager import DataManager

class InstructorTable(ttk.Frame):
    def __init__(self, master, dm, course_table  = None,  **kwargs):
        self.dm = dm
        self.course_table = course_table
        super().__init__(master, **kwargs)
        # Search Bar
        ttk.Label(self, text="Search").grid(row=0, column=0, sticky="w", pady=4)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky="ew", pady=4)

        search_btn = ttk.Button(self, text="Search for Instructor", command=self.search_records)
        search_btn.grid(row=0, column=2, padx=6)
        self.columnconfigure(1, weight=1)

        # Treeview
        instructor_columns = ("ID", "Name", "Age", "Email", "Assigned Courses")
        self.tree = ttk.Treeview(self, columns=instructor_columns, show="headings")
        for attribute in instructor_columns:
            self.tree.heading(attribute, text=attribute)
            self.tree.column(attribute, width=120, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=10)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Buttons for editing and deleting
        edit_btn = ttk.Button(self, text="Edit", command=self.edit_instructor)
        edit_btn.grid(row=2, column=0, pady=5)

        delete_btn = ttk.Button(self, text="Delete", command=self.delete_instructor)
        delete_btn.grid(row=2, column=1, pady=5)

    # helper to select an instructor
    def select_instructor(self):
        selected = self.tree.selection()
        if not selected:
            return None
        instructor_id = self.tree.item(selected[0])["values"][0]  # first column = ID
        for i in getattr(self, 'instructors', []):
            if i.instructor_id == instructor_id:
                return i
        return None

    # method to edit instructor
    def edit_instructor(self):
        instructor = self.select_instructor()
        if not instructor:
            messagebox.showerror("Error", "Please select an instructor to edit")
            return

        popup = tk.Toplevel(self)
        popup.title("Edit Instructor")
        popup.geometry("400x200")

        # Pre-fill with current values
        name_var = tk.StringVar(value=instructor.name)
        email_var = tk.StringVar(value=instructor.email)
        age_var = tk.StringVar(value=str(instructor.age))

        ttk.Label(popup, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(popup, text="Email:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=email_var, width=30).grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(popup, text="Age:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=age_var, width=30).grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        def save_changes():
            try:
                instructor.name = name_var.get()
                instructor.email = email_var.get()
                instructor.age = int(age_var.get())
                # Persist instructor to DB
                self.dm.update_instructor_in_db(instructor)
                # Ensure assigned courses remain linked to this instructor in DB
                for course in instructor.assigned_courses:
                    course.course_instructor = instructor
                    self.dm.update_course_in_db(course)
                # Refresh tables
                self.load_data()
                if self.course_table:
                    self.course_table.load_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))



        ttk.Button(popup, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2)

    # method to delete instructor
    def delete_instructor(self):
        instructor = self.select_instructor()
        if not instructor:
            messagebox.showerror("Error", "Please select an instructor to delete")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {instructor.name}?")
        if confirm:
            try:
                # Unassign instructor from all courses and persist to DB
                for course in list(instructor.assigned_courses):
                    course.course_instructor = None
                    self.dm.update_course_in_db(course)
                instructor.assigned_courses.clear()
                # Delete instructor from DB
                self.dm.delete_instructor_from_db(instructor.instructor_id)
                # Refresh tables
                self.load_data()
                if self.course_table:
                    self.course_table.load_data()
                messagebox.showinfo("Deleted", f"Instructor {instructor.name} has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
       
           
    def search_records(self):
        query = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not query:
            self.load_data()
            return

        for instructor in getattr(self, 'instructors', []):
            if query in instructor.name.lower():
                self.insert_instructor(instructor)
                continue
            if query in instructor.instructor_id.lower():
                self.insert_instructor(instructor)
                continue
            if query in instructor.email.lower():
                self.insert_instructor(instructor)
                continue
            for c in instructor.assigned_courses:
                if query in c.course_name.lower():
                    self.insert_instructor(instructor)
                    break

    def insert_instructor(self, instructor):
        courses = [c.course_name for c in instructor.assigned_courses]
        courses_str = ", ".join(courses)
        self.tree.insert("", "end", values=(
            instructor.instructor_id,
            instructor.name,
            instructor.age,
            instructor.email,
            courses_str
        ))

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Always reload latest data from DB and rebuild relationships for accuracy
        students = self.dm.load_students_from_db()
        instructors = self.dm.load_instructors_from_db()
        courses = self.dm.load_courses_from_db()
        try:
            self.dm.rebuild_relationships_clean(students, instructors, courses)
        except AttributeError:
            self.dm.rebuild_relationships(students, instructors, courses)
        # Cache
        self.instructors = instructors
        for instructor in self.instructors:
            self.insert_instructor(instructor)
