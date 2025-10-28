"""
Course Form Module

This module provides a PyQt5-based form that allows adding a new course to the offered courses.
It interacts with the DataManager class to add database records for courses.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from src.core.modules import Course
from src.storage.data_manager import DataManager


class CourseForm(QWidget):
    """
    A GUI for adding a new course to the list of offered courses.

    This form allows the user to input a course ID and a course name, and add the course to the list of offered courses.

    :param dm: Datamanager instance used for database interactions.
    :type dm: DataManager

    :param parent: Optional parent widget.
    :type parent: QWidget, optional

    :ivar dm: Reference to the data manager.
    :vartype dm: DataManager

    :ivar id_input: Input field for entering the new course ID.
    :vartype id_input: QLineEdit

    :ivar name_input: Input field for entering the new course name.
    :vartype name_input: QLineEdit

    :ivar added_course: Signal emitted after data changes (course added).
    :vartype added_course: pyqtSignal
    """

    added_course = pyqtSignal(Course)
    """Signal emitted when a new course is added."""

    def __init__(self, dm: DataManager, parent=None):
        """Initialize the CourseForm layout, widgets, and signals."""
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()

        # Course ID input
        layout.addWidget(QLabel("Course ID"))
        self.id_input = QLineEdit()
        layout.addWidget(self.id_input)

        # Course Name input
        layout.addWidget(QLabel("Course Name"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Add Course button
        add_course_button = QPushButton("Add Course")
        add_course_button.clicked.connect(self.add_course)
        layout.addWidget(add_course_button)

        self.setLayout(layout)

    def add_course(self):
        """
        Add a new course with the given ID and name to the database.

        This method performs input validation and prevents adding two courses with the same ID
        to the database. It updates the courses list in both memory and database after a course
        is added. It refreshes the courses table to reflect the change, clears the input fields,
        and provides user feedback via a message box.

        :raises ValueError: If course ID or name fields are empty, or if a course with the same ID
            already exists in the database.
        :return: None
        """
        try:
            # Input validation
            course_id = self.id_input.text().strip()
            course_name = self.name_input.text().strip()

            if not course_id or not course_name:
                raise ValueError("Both Course ID and Course Name must be filled.")

            # Prevent duplicate IDs directly from database
            cursor = self.dm.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM courses WHERE course_id = ?", (course_id,))
            exists = cursor.fetchone()[0] > 0
            if exists:
                raise ValueError(f"Course ID '{course_id}' already exists in the database.")
            else:
                # Create a new Course object
                new_course = Course(
                    course_id=course_id,
                    course_name=course_name,
                    enrolled_students=[],
                    course_instructor=None
                )

            # Save to database (which also updates snapshot)
            self.dm.add_course_to_db(new_course)

            # Emit signal for tables to refresh
            self.added_course.emit(new_course)

            # Clear input fields
            self.id_input.clear()
            self.name_input.clear()

            QMessageBox.information(
                self,
                "Success",
                f"Course '{new_course.course_name}' added successfully!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
