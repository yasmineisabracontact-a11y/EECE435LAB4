import tkinter as tk
from tkinter import ttk, messagebox

from src.tk_app.student_form import StudentForm
from src.tk_app.course_registration_form import CourseRegistrationForm
from src.tk_app.instructor_form import InstructorForm
from src.tk_app.course_assignment_form import CourseAssignmentForm
from src.tk_app.course_form import CourseForm
from src.tk_app.student_table import StudentTable
from src.tk_app.instructor_table import InstructorTable
from src.tk_app.course_table import CourseTable
from src.storage.data_manager import DataManager


def main():
    root = tk.Tk()
    root.title("School Management System")
    root.geometry("1000x700")  # a bit larger for clarity

    # Data manager instance
    dm = DataManager()
    try:
        dm.students_data = dm.load_students_from_db()
        dm.courses_data = dm.load_courses_from_db()
        dm.instructors_data = dm.load_instructors_from_db()
        # Rebuild relationships so Student.registered_courses and
        # Instructor.assigned_courses reflect DB on startup
        try:
            dm.rebuild_relationships_clean(dm.students_data, dm.instructors_data, dm.courses_data)
        except AttributeError:
            dm.rebuild_relationships(dm.students_data, dm.instructors_data, dm.courses_data)
    except Exception as e:
        messagebox.showwarning("Warning", f"Failed to load data from DB:\n{e}")

    # Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # --- TABLES ---
    student_tab = StudentTable(notebook, dm)
    notebook.add(student_tab, text="Students Records")

    course_tab = CourseTable(notebook, dm)
    notebook.add(course_tab, text="Course Records")

    instructor_tab = InstructorTable(notebook, dm)
    notebook.add(instructor_tab, text="Instructors Records")

    # Linking relationships between tables
    course_tab.student_table = student_tab
    course_tab.instructor_table = instructor_tab
    student_tab.course_table = course_tab
    instructor_tab.course_table = course_tab

    # Initial load
    student_tab.load_data()
    course_tab.load_data()
    instructor_tab.load_data()

    # --- FORMS TAB ---
    forms_tab = ttk.Frame(notebook)
    notebook.add(forms_tab, text="Forms")

    # Student Form
    student_form = StudentForm(forms_tab, dm, student_table=student_tab)
    student_form.pack(padx=20, pady=10, fill="x")

    # Course Registration Form
    course_registration_form = CourseRegistrationForm(
        forms_tab, dm, student_table=student_tab, course_table=course_tab
    )
    course_registration_form.pack(padx=20, pady=10, fill="x")

    # Instructor Form
    instructor_form = InstructorForm(forms_tab, dm, instructor_table=instructor_tab)
    instructor_form.pack(padx=20, pady=10, fill="x")

    # Course Assignment Form
    course_assignment_form = CourseAssignmentForm(
        forms_tab, dm, instructor_table=instructor_tab, course_table=course_tab
    )
    course_assignment_form.pack(padx=20, pady=10, fill="x")

    # Course Form
    course_form = CourseForm(forms_tab, dm, course_table=course_tab)
    course_form.pack(padx=20, pady=10, fill="x")

    # Safe exit handler
    def on_closing():
        try:
            dm.save_data_to_file("starschool_data.json")
            dm.backup_database()

        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to save data:\n{e}")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start app
    root.mainloop()


if __name__ == "__main__":
    main()
