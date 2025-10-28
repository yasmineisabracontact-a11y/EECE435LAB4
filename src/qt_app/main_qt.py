# import sys
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
#     QMessageBox, QLabel
# )
# from src.qt_app.student_form_qt import StudentForm
# from src.qt_app.course_form_qt import CourseForm
# from src.qt_app.instructor_form_qt import InstructorForm
# from src.qt_app.course_registration_form_qt import CourseRegistrationForm
# from src.qt_app.course_assignment_form_qt import CourseAssignmentForm
# from src.storage.data_manager import DataManager
# from .course_table_qt import CourseTable
# from .student_table_qt import StudentTable
# from .instructor_table_qt import InstructorTable


# class MainWindow(QMainWindow):
#     def __init__(self, dm: DataManager):
#         self.dm = dm
#         super().__init__()

#         # Attempt to preload from DB
#         try:
#             self.dm.load_instructors_from_db()
#             self.dm.load_students_from_db()
#             self.dm.load_courses_from_db()
#             self.dm.rebuild_relationships(
#                 self.dm.students_data, self.dm.instructors_data, self.dm.courses_data
#             )
#         except Exception:
#             QMessageBox.warning(self, "Warning", "Failed to load data from DB.")

#         self.setWindowTitle("School Management System")
#         self.setGeometry(100, 100, 800, 600)

#         tabs = QTabWidget()
#         self.setCentralWidget(tabs)

#         # --- Initialize Tables ---
#         self.student_table = StudentTable(self.dm)
#         self.instructor_table = InstructorTable(self.dm)
#         self.course_table = CourseTable(self.dm)

#         # Cross-links for refreshing
#         self.course_table.student_table = self.student_table
#         self.course_table.instructor_table = self.instructor_table
#         self.student_table.course_table = self.course_table
#         self.instructor_table.course_table = self.course_table

#         # --- Student Tab ---
#         students_tab = QWidget()
#         tabs.addTab(students_tab, "Students")
#         students_layout = QVBoxLayout()
#         students_tab.setLayout(students_layout)
#         self.student_form = StudentForm(self.dm)
#         students_layout.addWidget(self.student_form)

#         self.student_form.added_student.connect(
#             lambda s: (
#                 QMessageBox.information(self, "Student Added", f"Student {s.name} added successfully!"),
#                 self.student_table.load_students_data()
#             )
#         )

#         # --- Instructor Tab ---
#         instructors_tab = QWidget()
#         tabs.addTab(instructors_tab, "Instructors")
#         instructor_layout = QVBoxLayout()
#         instructors_tab.setLayout(instructor_layout)
#         self.instructor_form = InstructorForm(self.dm)
#         instructor_layout.addWidget(self.instructor_form)

#         self.instructor_form.added_instructor.connect(
#             lambda i: (
#                 QMessageBox.information(self, "Instructor Added", f"Instructor {i.name} added successfully!"),
#                 self.instructor_table.load_instructor_data()
#             )
#         )

#         # --- Courses Tab ---
#         courses_tab = QWidget()
#         tabs.addTab(courses_tab, "Courses")
#         course_layout = QVBoxLayout()
#         courses_tab.setLayout(course_layout)
#         self.course_form = CourseForm(self.dm)
#         course_layout.addWidget(self.course_form)

#         self.course_form.added_course.connect(
#             lambda c: (
#                 QMessageBox.information(self, "Course Added", f"Course {c.course_name} added successfully!"),
#                 self.course_table.load_course_data()
#             )
#         )

#         # --- Tables Tabs ---
#         students_table_tab = QWidget()
#         tabs.addTab(students_table_tab, "Students Records")
#         students_table_layout = QVBoxLayout()
#         students_table_tab.setLayout(students_table_layout)
#         students_table_layout.addWidget(self.student_table)

#         instructors_table_tab = QWidget()
#         tabs.addTab(instructors_table_tab, "Instructors Records")
#         instructors_table_layout = QVBoxLayout()
#         instructors_table_tab.setLayout(instructors_table_layout)
#         instructors_table_layout.addWidget(self.instructor_table)

#         courses_table_tab = QWidget()
#         tabs.addTab(courses_table_tab, "Courses Records")
#         courses_table_layout = QVBoxLayout()
#         courses_table_tab.setLayout(courses_table_layout)
#         courses_table_layout.addWidget(self.course_table)

#         # --- Forms Tab ---
#         forms_tab = QWidget()
#         tabs.addTab(forms_tab, "Forms")
#         forms_layout = QVBoxLayout()
#         forms_layout.addSpacing(20)
#         forms_tab.setLayout(forms_layout)

#         # Register student to course
#         forms_layout.addWidget(QLabel("Register Student to Course"))
#         course_registration_form = CourseRegistrationForm(self.dm)
#         forms_layout.addWidget(course_registration_form)
#         course_registration_form.data_updated.connect(self.student_table.load_students_data)
#         course_registration_form.data_updated.connect(self.course_table.load_course_data)
#         self.course_form.added_course.connect(
#             lambda c: course_registration_form.courses_dropdown.addItem(c.course_name)
#         )

#         # Assign instructor to course
#         forms_layout.addWidget(QLabel("Assign Instructor to a Course"))
#         course_assignment_form = CourseAssignmentForm(self.dm)
#         forms_layout.addWidget(course_assignment_form)
#         course_assignment_form.data_updated.connect(self.instructor_table.load_instructor_data)
#         course_assignment_form.data_updated.connect(self.course_table.load_course_data)
#         self.course_form.added_course.connect(
#             lambda c: course_assignment_form.courses_dropdown.addItem(c.course_name)
#         )

#     def closeEvent(self, event):
#         """Ensure DB is safely committed and backed up on exit."""
#         try:
#             self.dm.refresh_snapshot()  # Save a JSON snapshot before exit
#             self.dm.conn.commit()       # Ensure last writes are saved
#             self.dm.backup_database()   # Backup DB with timestamp
#             self.dm.conn.close()
#             QMessageBox.information(self, "Exit", "All data saved and backup created successfully.")
#             event.accept()
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to save data: {e}")
#             event.ignore()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     dm = DataManager()
#     window = MainWindow(dm)
#     window.show()
#     sys.exit(app.exec_())



import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMessageBox, QLabel
)
from src.qt_app.student_form_qt import StudentForm
from src.qt_app.course_form_qt import CourseForm
from src.qt_app.instructor_form_qt import InstructorForm
from src.qt_app.course_registration_form_qt import CourseRegistrationForm
from src.qt_app.course_assignment_form_qt import CourseAssignmentForm
from src.storage.data_manager import DataManager
from .course_table_qt import CourseTable
from .student_table_qt import StudentTable
from .instructor_table_qt import InstructorTable


class MainWindow(QMainWindow):
    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm

        try:
            self.dm.load_instructors_from_db()
            self.dm.load_students_from_db()
            self.dm.load_courses_from_db()
            # Use deduped relationship rebuild when available
            if hasattr(self.dm, 'rebuild_relationships_clean'):
                self.dm.rebuild_relationships_clean(
                    self.dm.students_data, self.dm.instructors_data, self.dm.courses_data
                )
            else:
                self.dm.rebuild_relationships(
                    self.dm.students_data, self.dm.instructors_data, self.dm.courses_data
                )
        except Exception:
            QMessageBox.warning(self, "Warning", "Failed to load data from DB.")

        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 800, 600)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Tables
        self.student_table = StudentTable(self.dm)
        self.instructor_table = InstructorTable(self.dm)
        self.course_table = CourseTable(self.dm)

        self.course_table.student_table = self.student_table
        self.course_table.instructor_table = self.instructor_table
        self.student_table.course_table = self.course_table
        self.instructor_table.course_table = self.course_table

        # Cross-refresh: when one table changes data, update the others
        self.course_table.data_updated.connect(self.instructor_table.load_instructor_data)
        self.course_table.data_updated.connect(self.student_table.load_students_data)
        self.instructor_table.data_updated.connect(self.course_table.load_course_data)
        self.student_table.data_updated.connect(self.course_table.load_course_data)

        # Student Tab
        students_tab = QWidget()
        tabs.addTab(students_tab, "Students")
        students_layout = QVBoxLayout()
        students_tab.setLayout(students_layout)
        self.student_form = StudentForm(self.dm)
        students_layout.addWidget(self.student_form)

        self.student_form.added_student.connect(
            lambda s: (
                QMessageBox.information(self, "Student Added", f"Student {s.name} added successfully!"),
                self.student_table.load_students_data()
            )
        )

        # Instructor Tab
        instructors_tab = QWidget()
        tabs.addTab(instructors_tab, "Instructors")
        instructor_layout = QVBoxLayout()
        instructors_tab.setLayout(instructor_layout)
        self.instructor_form = InstructorForm(self.dm)
        instructor_layout.addWidget(self.instructor_form)

        self.instructor_form.added_instructor.connect(
            lambda i: (
                QMessageBox.information(self, "Instructor Added", f"Instructor {i.name} added successfully!"),
                self.instructor_table.load_instructor_data()
            )
        )

        # Course Tab
        courses_tab = QWidget()
        tabs.addTab(courses_tab, "Courses")
        course_layout = QVBoxLayout()
        courses_tab.setLayout(course_layout)
        self.course_form = CourseForm(self.dm)
        course_layout.addWidget(self.course_form)

        self.course_form.added_course.connect(
            lambda c: (
                QMessageBox.information(self, "Course Added", f"Course {c.course_name} added successfully!"),
                self.course_table.load_course_data()
            )
        )

        # Students Records
        students_table_tab = QWidget()
        tabs.addTab(students_table_tab, "Students Records")
        students_table_layout = QVBoxLayout()
        students_table_tab.setLayout(students_table_layout)
        students_table_layout.addWidget(self.student_table)

        # Instructors Records
        instructors_table_tab = QWidget()
        tabs.addTab(instructors_table_tab, "Instructors Records")
        instructors_table_layout = QVBoxLayout()
        instructors_table_tab.setLayout(instructors_table_layout)
        instructors_table_layout.addWidget(self.instructor_table)

        # Courses Records
        courses_table_tab = QWidget()
        tabs.addTab(courses_table_tab, "Courses Records")
        courses_table_layout = QVBoxLayout()
        courses_table_tab.setLayout(courses_table_layout)
        courses_table_layout.addWidget(self.course_table)

        # Forms Tab
        forms_tab = QWidget()
        tabs.addTab(forms_tab, "Forms")
        forms_layout = QVBoxLayout()
        forms_layout.addSpacing(20)
        forms_tab.setLayout(forms_layout)

        # Register student to course
        forms_layout.addWidget(QLabel("Register Student to Course"))
        course_registration_form = CourseRegistrationForm(self.dm)
        forms_layout.addWidget(course_registration_form)
        course_registration_form.data_updated.connect(self.student_table.load_students_data)
        course_registration_form.data_updated.connect(self.course_table.load_course_data)
        self.course_form.added_course.connect(
            lambda c: course_registration_form.courses_dropdown.addItem(f"{c.course_name} ({c.course_id})")
        )

        # Assign instructor to course
        forms_layout.addWidget(QLabel("Assign Instructor to a Course"))
        course_assignment_form = CourseAssignmentForm(self.dm)
        forms_layout.addWidget(course_assignment_form)
        course_assignment_form.data_updated.connect(self.instructor_table.load_instructor_data)
        course_assignment_form.data_updated.connect(self.course_table.load_course_data)
        self.course_form.added_course.connect(
            lambda c: course_assignment_form.courses_dropdown.addItem(f"{c.course_name}")
        )

    def closeEvent(self, event):
        try:
            self.dm.refresh_snapshot()
            self.dm.conn.commit()
            self.dm.backup_database()
            self.dm.conn.close()
            QMessageBox.information(self, "Exit", "All data saved and backup created successfully.")
            event.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dm = DataManager()
    window = MainWindow(dm)
    window.show()
    sys.exit(app.exec_())
