import tkinter as tk
from tkinter import ttk, messagebox
from src.core.modules import *
from src.storage.data_manager import DataManager

class CourseTable(ttk.Frame):
    def __init__(self, master, dm: DataManager, student_table=None, instructor_table=None, **kwargs):
        self.dm = dm
        self.student_table = student_table
        self.instructor_table = instructor_table
        super().__init__(master, **kwargs)

        ttk.Label(self, text="Search").grid(row=0, column=0, sticky="w", pady=4)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky="ew", pady=4)

        search_btn = ttk.Button(self, text="Search for Course", command=self.search_records)
        search_btn.grid(row=0, column=2, padx=6)
        self.columnconfigure(1, weight=1)

        course_columns = ("ID", "Name", "Course Instructor", "Enrolled Students")
        self.tree = ttk.Treeview(self, columns=course_columns, show="headings")
        for attribute in course_columns:
            self.tree.heading(attribute, text=attribute)
            self.tree.column(attribute, width=120, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=10)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        edit_btn = ttk.Button(self, text="Edit", command=self.edit_course)
        edit_btn.grid(row=2, column=0, pady=5)

        delete_btn = ttk.Button(self, text="Delete", command=self.delete_course)
        delete_btn.grid(row=2, column=1, pady=5)

    def select_course(self):
        selected = self.tree.selection()
        if not selected:
            return None
        course_id = self.tree.item(selected[0])["values"][0]
        for c in self.dm.courses_data:
            if c.course_id == course_id:
                return c
        return None

    def edit_course(self):
        course = self.select_course()
        if not course:
            messagebox.showerror("Error", "Please select a course to edit")
            return

        popup = tk.Toplevel(self)
        popup.title("Edit Course")
        popup.geometry("400x200")

        name_var = tk.StringVar(value=course.course_name)
        id_var = tk.StringVar(value=course.course_id)

        ttk.Label(popup, text="Course Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(popup, text="Course ID:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=id_var, width=30).grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        def save_changes():
            try:
                old_id = course.course_id
                new_name = name_var.get().strip()
                new_id = id_var.get().strip()

                course.course_name = new_name
                course.course_id = new_id

                if not course.course_name or not course.course_id:
                    raise ValueError("Both Course Name and Course ID are required.")

                # Update in DB; if ID changed, propagate to students/instructors
                if new_id != old_id and hasattr(self.dm, 'rename_course_id_in_db'):
                    self.dm.rename_course_id_in_db(old_id, new_id, new_name)
                else:
                    self.dm.update_course_in_db(course)

                # Reload data in-memory from DB for accuracy
                self.dm.courses_data = self.dm.load_courses_from_db()

                self.load_data()
                if self.student_table:
                    self.student_table.load_data()
                if self.instructor_table:
                    self.instructor_table.load_data()

                messagebox.showinfo("Success", f"Course '{course.course_name}' updated successfully.")
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(popup, text="Save", command=save_changes).grid(row=2, column=0, columnspan=2)

    def delete_course(self):
        course = self.select_course()
        if not course:
            messagebox.showerror("Error", "Please select a course to delete")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {course.course_name}?")
        if confirm:
            try:
                # Unassign instructor (and persist)
                if course.course_instructor:
                    instructor = course.course_instructor
                    if course in instructor.assigned_courses:
                        instructor.assigned_courses.remove(course)
                        self.dm.update_instructor_in_db(instructor)
                    course.course_instructor = None
                # Remove from students (and persist)
                for student in list(course.enrolled_students):
                    if course in student.registered_courses:
                        student.registered_courses.remove(course)
                        self.dm.update_student_in_db(student)
                # Remove course from DB
                self.dm.delete_course_from_db(course.course_id)
                # Reload from DB
                self.dm.courses_data = self.dm.load_courses_from_db()

                self.load_data()
                if self.student_table:
                    self.student_table.load_data()
                if self.instructor_table:
                    self.instructor_table.load_data()

                messagebox.showinfo("Deleted", f"Course '{course.course_name}' deleted successfully.")

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def search_records(self):
        query = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not query:
            self.load_data()
            return

        for course in self.dm.courses_data:
            if query in course.course_id.lower() or \
               query in course.course_name.lower() or \
               (course.course_instructor and query in course.course_instructor.name.lower()) or \
               any(query in s.name.lower() for s in course.enrolled_students):
                self.insert_course(course)

    def insert_course(self, course):
        students = [s.name for s in course.enrolled_students]
        students_str = ", ".join(students)
        instructor_name = course.course_instructor.name if course.course_instructor else "Unassigned"
        self.tree.insert("", "end", values=(
            course.course_id,
            course.course_name,
            instructor_name,
            students_str
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

        # Cache courses for selection helpers
        self.dm.courses_data = courses

        for course in courses:
            self.insert_course(course)
