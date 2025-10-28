"""
Student Form Module

This module provides a PyQt5-based form that allows adding a new student to the enrolled students in the school.
It interacts with the DataManager class to add database records for students.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from src.core.modules import Student
from src.storage.data_manager import DataManager


class StudentForm(QWidget):
    """
    A GUI for adding a new student to the list of students enrolled in the school.

    This form allows the user to input a student ID, name, email, and age,
    and add the student to the list of enrolled students.

    :param dm: DataManager instance used for database interactions.
    :type dm: DataManager
    :param parent: Optional parent widget.
    :type parent: QWidget, optional
    """

    added_student = pyqtSignal(Student)
    """Signal emitted when a new student is added."""

    def __init__(self, dm: DataManager, parent=None):
        """Initialize the StudentForm layout, widgets, and signals."""
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()

        # ID
        self.id_input = QLineEdit()
        layout.addWidget(QLabel("ID"))
        layout.addWidget(self.id_input)

        # Name
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name_input)

        # Email
        self.email_input = QLineEdit()
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_input)

        # Age
        self.age_input = QLineEdit()
        layout.addWidget(QLabel("Age"))
        layout.addWidget(self.age_input)

        # Button
        add_student_button = QPushButton("Add Student")
        add_student_button.clicked.connect(self.add_student)
        layout.addWidget(add_student_button)

        self.setLayout(layout)

    def add_student(self):
        """
        Add a new student with the given ID, name, email, and age to the database.

        This method performs input validation and prevents adding two students
        with the same ID to the database. It updates the student list in both
        memory and the database after a new student is added. It refreshes the
        student table, clears the input fields, and provides user feedback via
        a message box.

        :ivar dm: Reference to the data manager.
        :vartype dm: DataManager
        :ivar id_input: Input field for entering the new student ID.
        :vartype id_input: QLineEdit
        :ivar name_input: Input field for entering the new student name.
        :vartype name_input: QLineEdit
        :ivar email_input: Input field for entering the new student email.
        :vartype email_input: QLineEdit
        :ivar age_input: Input field for entering the new student age.
        :vartype age_input: QLineEdit
     

        :raises ValueError: If student ID, name, email, or age fields are empty,
            or if a student with the same ID already exists in the database.
        :return: None
        :rtype: None
        """
        try:
            # Input validation
            if not all([
                self.id_input.text().strip(),
                self.name_input.text().strip(),
                self.email_input.text().strip(),
                self.age_input.text().strip()
            ]):
                raise ValueError("All fields must be filled before adding a student.")

            if not self.age_input.text().strip().isdigit():
                raise ValueError("Age must be a valid number.")

            # Create Student object
            new_student = Student(
                student_id=self.id_input.text().strip(),
                name=self.name_input.text().strip(),
                email=self.email_input.text().strip(),
                age=int(self.age_input.text().strip()),
                registered_courses=[]
            )

            # Prevent duplicate IDs directly from database
            cursor = self.dm.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students WHERE student_id = ?", (new_student.student_id,))
            exists = cursor.fetchone()[0] > 0
            if exists:
                raise ValueError(f"Student ID '{new_student.student_id}' already exists in the database.")
            else:
                # Save to DataManager (syncs DB + snapshot)
                self.dm.add_student_to_db(new_student)

                # Emit signal to notify table
                self.added_student.emit(new_student)

            # Clear inputs
            self.id_input.clear()
            self.name_input.clear()
            self.email_input.clear()
            self.age_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
