"""
Student Table Module

This module provides a PyQt5-based interface for viewing, searching, editing,
deleting, and exporting student records. It interacts with the DataManager
to load and update data in the database.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QTableWidget,
    QDialogButtonBox, QTableWidgetItem, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout
)
from PyQt5.QtCore import pyqtSignal
from src.storage.data_manager import DataManager
import csv


class StudentTable(QWidget):
    """
    A GUI for displaying available student information and editing or deleting any of these records.

    This table provides the user with a tabular representation of available student IDs
    and corresponding names, emails, and ages, and allows them to edit or delete any of the available students.

    :param dm: DataManager instance for database interaction.
    :type dm: DataManager
    :param parent: Optional parent widget.
    :type parent: QWidget, optional"""

    data_updated = pyqtSignal()

    def __init__(self, dm: DataManager, parent=None):
        """Initialize the StudentTable layout, widgets, and signals."""
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Students"))

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, Name, Email, or Registered Courses")
        self.search_input.textChanged.connect(self.search_bar)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Export button
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(export_button)

        # Load students data from db and place in student list
        self.load_students_data()

    def load_students_data(self):
        """
        Load all student records, display their IDs, names, emails, ages,
        and list of registered courses, and provide the option to edit or delete any of the records.

        This method loads the students, instructors, and courses data from the database.
        It cleans and rebuilds the relationships between students–courses and instructors–courses.
        It also defines the table structure with columns for each attribute (ID, Name, Email, Age, Registered Courses)
        and adds buttons for editing and deleting records.

        :return: None
        :rtype: None
        """
        students = self.dm.load_students_from_db()
        instructors = self.dm.load_instructors_from_db()
        courses = self.dm.load_courses_from_db()

        # Rebuild relationships with clearing to avoid duplicates
        if hasattr(self.dm, 'rebuild_relationships_clean'):
            self.dm.rebuild_relationships_clean(students, instructors, courses)
        else:
            self.dm.rebuild_relationships(students, instructors, courses)

        self.students = students

        self.table.setRowCount(len(self.students))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Student ID", "Name", "Age", "Email", "Registered Courses", "Actions"]
        )

        for row, student in enumerate(self.students):
            registered_courses_names = (
                ", ".join(course.course_name for course in student.registered_courses)
                if student.registered_courses else "None"
            )

            # Edit and Delete buttons
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            # Connect buttons
            edit_button.clicked.connect(lambda _, r=row: self.edit_record(r))
            delete_button.clicked.connect(lambda _, r=row: self.delete_record(r))

            # Button layout
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Add to table
            self.table.setItem(row, 0, QTableWidgetItem(student.student_id))
            self.table.setItem(row, 1, QTableWidgetItem(student.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(student.age)))
            self.table.setItem(row, 3, QTableWidgetItem(student.email))
            self.table.setItem(row, 4, QTableWidgetItem(registered_courses_names))
            self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)

    def edit_record(self, row):
        """
        Edit a specific student's ID, name, email, or age.

        This method references the student by ID, opens an edit dialog, and updates the ID, name, age, or email
        in both memory and database. It also propagates the change in name to the list of enrolled students
        of this student's registered courses. Once changes are committed, it reloads the student data,
        refreshes relationships, emits a data update signal, and provides user feedback via a message box.

        :param row: Index of the student record in the students table.
        :type row: int
        :return: None
        :rtype: None
        """
        student = self.students[row]
        dialog = EditStudentDialog(student, self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            dialog.save_changes()
            self.dm.update_student_in_db(student)
            for course in student.registered_courses:
                if student in course.enrolled_students:
                    course.enrolled_students.remove(student)
                    course.register_student(student)
                    self.dm.update_course_in_db(course)
            self.load_students_data()
            self.data_updated.emit()
            QMessageBox.information(self, "Success", f"Student '{student.name}' updated successfully.")

    def delete_record(self, row):
        """
        Delete a specific student record.

        This method identifies the student by ID, removes their name from the list of enrolled students
        of all courses in which this student is registered. It then deletes the student record from both
        memory and database. Once changes are committed, it reloads the student data, refreshes relationships,
        emits a data update signal, and provides user feedback via a message box.

        :param row: Index of the student record in the table.
        :type row: int
        :return: None
        :rtype: None
        """
        student = self.students[row]
        try:
            for course in student.registered_courses:
                if student in course.enrolled_students:
                    course.enrolled_students.remove(student)
                    self.dm.update_course_in_db(course)
            self.dm.delete_student_from_db(student.student_id)
            self.dm.load_students_from_db()
            self.load_students_data()
            self.data_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def search_bar(self):
        """
        Search for the student by ID, name, email, age, or registered course names.

        This method allows the user to input a filtering query and displays students accordingly.
        It hides non-matching rows and rebuilds the table to only display the records that have
        an ID, name, email, age, or registered course name matching the user's input text.

        :return: None
        :rtype: None
        """
        search_query = self.search_input.text().strip().lower()
        students = self.dm.load_students_from_db()

        if not search_query:
            self.load_students_data()
            return

        filtered = []
        for student in students:
            if (
                search_query in student.student_id.lower()
                or search_query in student.name.lower()
                or search_query in student.email.lower()
            ):
                filtered.append(student)
                continue

            for course in student.registered_courses:
                if (
                    search_query in course.course_name.lower()
                    or search_query in course.course_id.lower()
                ):
                    filtered.append(student)
                    break

        self.table.setRowCount(0)
        self.table.setRowCount(len(filtered))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Student ID", "Name", "Age", "Email", "Registered Courses", "Actions"]
        )

        for row, student in enumerate(filtered):
            registered_courses_names = (
                ", ".join(course.course_name for course in student.registered_courses)
                if student.registered_courses else "None"
            )

            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            edit_button.clicked.connect(lambda _, r=row: self.edit_record(r))
            delete_button.clicked.connect(lambda _, r=row: self.delete_record(r))

            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            self.table.setItem(row, 0, QTableWidgetItem(student.student_id))
            self.table.setItem(row, 1, QTableWidgetItem(student.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(student.age)))
            self.table.setItem(row, 3, QTableWidgetItem(student.email))
            self.table.setItem(row, 4, QTableWidgetItem(registered_courses_names))
            self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)

    def export_to_csv(self):
        """
        Export all student records to a CSV file.

        This method loads all students data from the database and writes them into a timestamped CSV file.
        Each student record includes the ID, name, age, email, and list of registered courses.
        Once the data is exported, a success message is provided to the user via a message box;
        otherwise, an error message is displayed.

        :return: None
        :rtype: None
        """
        try:
            students = self.dm.load_students_from_db()
            with open("students.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Student ID", "Name", "Age", "Email", "Registered Courses"])
                for student in students:
                    registered = ", ".join(course.course_name for course in student.registered_courses)
                    writer.writerow([student.student_id, student.name, student.age, student.email, registered])
            QMessageBox.information(self, "Export Successful", "Students exported to students.csv successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export students: {e}")


class EditStudentDialog(QDialog):
    """
    A dialog window for editing an existing student's ID, name, email, and age.

    :param student: The student object being edited.
    :type student: Student
    :param parent: Optional parent widget.
    :type parent: QWidget, optional"""



    def __init__(self, student, parent=None):
        """Initialize the Edit Student dialog layout and input fields."""
        super().__init__(parent)
        self.setWindowTitle("Edit Student")
        self.student = student

        layout = QFormLayout()

        self.id_input = QLineEdit(student.student_id)
        self.name_input = QLineEdit(student.name)
        self.age_input = QLineEdit(str(student.age))
        self.email_input = QLineEdit(student.email)

        layout.addRow("Student ID:", self.id_input)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Age:", self.age_input)
        layout.addRow("Email:", self.email_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def save_changes(self):
        """
        Save the edited student ID, name, email, and age.

        This method retrieves the updated student ID, name, email, and age from the editing dialog
        and assigns them to the corresponding attributes of the student object.
        It performs basic validation by stripping whitespace, and raises an exception
        if an error occurs during the update.

        :raises Exception: If an error occurs while applying the changes to the selected student.
        :return: None
        :rtype: None
        """
        self.student.student_id = self.id_input.text().strip()
        self.student.name = self.name_input.text().strip()
        self.student.age = int(self.age_input.text().strip())
        self.student.email = self.email_input.text().strip()
