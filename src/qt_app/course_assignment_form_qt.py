"""
Course Assignment Form Module

This module provides PyQt5-based form that allows assigning courses to instructors.
It interacts with the DataManager class to read and update database records for instructors and courses in the StarSchool System.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit
from PyQt5.QtCore import pyqtSignal
from src.storage.data_manager import DataManager
from src.core.modules import Instructor, Course


class CourseAssignmentForm(QWidget):
    """
    A GUI for assigning a course to an instructor.

    This form allows the user to input an instructor ID, select a course from a dropdown menu,
    and assign that course to the chosen instructor.

    :param dm: Data manager instance used for database interactions.
    :type dm: DataManager

    :param parent: Optional parent widget.
    :type parent: QWidget, optional
    """

    data_updated = pyqtSignal()
    """Signal to notify other components that data changed."""

    def __init__(self, dm: DataManager, parent=None):
        """Initialize the CourseAssignmentForm layout, widgets, and signals."""
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()

        # Instructor ID input
        layout.addWidget(QLabel("Instructor ID"))
        self.instructor_id = QLineEdit()
        layout.addWidget(self.instructor_id)

        # Course dropdown (loaded dynamically)
        layout.addWidget(QLabel("Courses"))
        self.courses_dropdown = QComboBox()
        self.load_courses_into_dropdown()
        layout.addWidget(self.courses_dropdown)

        # Assign button
        assign_button = QPushButton("Assign Course")
        assign_button.clicked.connect(self.assign_course)
        layout.addWidget(assign_button)

        self.setLayout(layout)

    def load_courses_into_dropdown(self):
        """
        Load available courses from the database into the dropdown menu.

        This method clears the dropdown list and repopulates it with all course names
        retrieved from the database.

        :return: None
        """
        self.courses_dropdown.clear()
        for course in self.dm.load_courses_from_db():
            self.courses_dropdown.addItem(course.course_name)

    def assign_course(self):
        """
        Assign the selected course from the dropdown to the instructor with the given ID.

        This method performs input validation, finds the matching instructor and course in
        the database according to user input, updates the relationships between instructors
        and courses in both memory and in the database, and provides user feedback via message boxes.

        :raises ValueError: If instructor ID or course is invalid, or if course is already assigned.
        :return: None
        """
        try:
            input_instructor_id = self.instructor_id.text().strip()
            input_course_name = self.courses_dropdown.currentText()

            # Validate input
            if not input_instructor_id or not input_course_name:
                raise ValueError("Please enter a valid Instructor ID and select a Course.")

            # Find instructor by ID
            matched_instructor = None
            for instructor in self.dm.load_instructors_from_db():
                if instructor.instructor_id == input_instructor_id:
                    matched_instructor = instructor
                    break

            if not matched_instructor:
                raise ValueError(f"No instructor found with ID '{input_instructor_id}'.")

            # Find course by name
            matched_course = None
            for course in self.dm.load_courses_from_db():
                if course.course_name == input_course_name:
                    matched_course = course
                    break

            if not matched_course:
                raise ValueError(f"Course '{input_course_name}' not found in database.")

            # Check if course already has an instructor
            if matched_course.course_instructor is not None:
                raise ValueError(
                    f"Course '{matched_course.course_name}' is already assigned to "
                    f"{matched_course.course_instructor.name}."
                )

            # Update in-memory relationships
            matched_instructor.assign_course(matched_course)
            matched_course.course_instructor = matched_instructor

            # Update in database
            self.dm.update_instructor_in_db(matched_instructor)
            self.dm.update_course_in_db(matched_course)

            # Notify user
            QMessageBox.information(
                self,
                "Success",
                f"Course '{matched_course.course_name}' assigned to instructor "
                f"'{matched_instructor.name}' successfully."
            )

            # Emit signal to refresh tables
            self.data_updated.emit()

            # Clear input fields
            self.instructor_id.clear()
            if self.courses_dropdown.count() > 0:
                self.courses_dropdown.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
