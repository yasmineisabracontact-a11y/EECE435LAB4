"""
Instructor Form Module

This module provides a PyQt5-based form that allows adding a new instructor to the available instructors.
It interacts with the DataManager class to add database records for instructors.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from src.core.modules import Instructor
from src.storage.data_manager import DataManager


class InstructorForm(QWidget):
    """
    A GUI for adding a new instructor to the list of available instructors.

    This form allows the user to input an instructor ID, name, email, and age,
    and add the instructor to the list of available instructors.

    :param dm: DataManager instance used for database interactions.
    :type dm: DataManager

    :param parent: Optional parent widget.
    :type parent: QWidget, optional
    """

    added_instructor = pyqtSignal(Instructor)
    """Signal emitted when a new instructor is added."""

    def __init__(self, dm: DataManager, parent=None):
        """Initialize the InstructorForm layout, widgets, and signals."""
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
        add_instructor_button = QPushButton("Add Instructor")
        add_instructor_button.clicked.connect(self.add_instructor)
        layout.addWidget(add_instructor_button)

        self.setLayout(layout)

    def add_instructor(self):
        """
        Add a new instructor with the given ID, name, email, and age to the database.

        This method performs input validation and prevents adding two instructors with the same ID
        to the database. It updates the instructor list in both memory and database after a new
        instructor is added. It refreshes the instructor table to reflect the change, clears the
        input fields, and provides user feedback via a message box.

        :raises ValueError: If instructor ID, name, email, or age fields are empty,
            or if an instructor with the same ID already exists in the database.
        :return: None
        """
        try:
            # Input validation
            if not all([
                self.id_input.text().strip(),
                self.name_input.text().strip(),
                self.email_input.text().strip(),
                self.age_input.text().strip()
            ]):
                raise ValueError("All fields must be filled before adding an instructor.")

            if not self.age_input.text().strip().isdigit():
                raise ValueError("Age must be a valid number.")

            # Create Instructor object
            new_instructor = Instructor(
                instructor_id=self.id_input.text().strip(),
                name=self.name_input.text().strip(),
                email=self.email_input.text().strip(),
                age=int(self.age_input.text().strip()),
                assigned_courses=[]
            )

            # Prevent duplicate IDs directly from database
            cursor = self.dm.conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM instructors WHERE instructor_id = ?",
                (new_instructor.instructor_id,)
            )
            exists = cursor.fetchone()[0] > 0
            if exists:
                raise ValueError(
                    f"Instructor ID '{new_instructor.instructor_id}' already exists in the database."
                )
            else:
                # Save to DataManager (syncs DB + snapshot)
                self.dm.add_instructor_to_db(new_instructor)

                # Emit signal to notify table
                self.added_instructor.emit(new_instructor)

            # Clear inputs
            self.id_input.clear()
            self.name_input.clear()
            self.email_input.clear()
            self.age_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
