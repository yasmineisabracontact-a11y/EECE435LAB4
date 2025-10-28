"""
Course Table Module 

This module provides a PyQt5-based table that allows the display of all available courses records.
It interacts with the DataManager class to import database records.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QTableWidget,
    QDialogButtonBox, QTableWidgetItem, QLabel, QLineEdit, QPushButton, QDialog, QFormLayout
)
from PyQt5.QtCore import pyqtSignal
from src.storage.data_manager import DataManager
import csv, datetime

class CourseTable(QWidget):
    """
    A GUI for displaying available courses information, and editing or deleting any of these records. 

    This table provides the user with a tabular representation of available courses IDs and corresponding names, and allows them to edit or delete any of the available courses.

    :param dm: DataManager instance for database interactions. 
    :type dm: DataManager
    :param parent: Optional parent widget 
    :type parent: QWidget, optional

    :ivar dm: Reference to the data manager
    :vartype dm: DataManager
    :ivar search_input: Search bar to filter the available courses by IDs, names, enrolled students or assigned instructors.
    :vartype search_input: QLineEdit
    :ivar table: Table to display courses records.
    :vartype table: QTableWidget
    :ivar data_updated: Signal emitted after course data is loaded and displayed.
    :vartype data_updated: pyqtSignal  
    """
    data_updated = pyqtSignal()
    def __init__(self, dm: DataManager, parent=None):
        """Initializes the CourseTable layout, widgets, and signals."""
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Courses"))

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, Name, Instructor, or Enrolled Students")
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

        # Load initial data
        self.load_course_data()

    # Load all courses
    def load_course_data(self):
        """
        Load all courses records, display their IDs, names, list of enrolled students, and assigned instructor, and provide the option to edit and delete any of the records.

        This method loads the students, instructors, and courses data from the database into corresponding lists, clears and rebuilds the relationships between students and courses (students registered in courses)/ courses and instructors(instructors assigned to courses).
        It defines the structure of the course table with a column for each attribute(ID, Name, Assigned Instructor, Enrolled Students, Status, Actions) and a row for each unique course. 
        It also adds two buttons for editing and deleting records.
        :return: None
        """
        students = self.dm.load_students_from_db()
        instructors = self.dm.load_instructors_from_db()
        courses = self.dm.load_courses_from_db()
        # Rebuild relationships with clearing to avoid duplicates and preserve links
        try:
            self.dm.rebuild_relationships_clean(students, instructors, courses)
        except AttributeError:
            self.dm.rebuild_relationships(students, instructors, courses)
        
        

        self.courses = courses

        self.table.setRowCount(len(self.courses))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Course ID", "Name", "Instructor", "Enrolled Students", "Status", "Actions"
        ])

        for row, course in enumerate(self.courses):
            instructor_name = (
                course.course_instructor.name if course.course_instructor else "—"
            )
            enrolled_students_names = (
                ", ".join(student.name for student in course.enrolled_students)
                if course.enrolled_students else "None"
            )

            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            # Use course_id binding instead of row index (safer)
            edit_button.clicked.connect(lambda _, cid=course.course_id: self.edit_record_by_id(cid))
            delete_button.clicked.connect(lambda _, cid=course.course_id: self.delete_record_by_id(cid))

            # Layout for action buttons
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Populate the table
            self.table.setItem(row, 0, QTableWidgetItem(course.course_id))
            self.table.setItem(row, 1, QTableWidgetItem(course.course_name))
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    course.course_instructor.name if course.course_instructor else "N/A"
                ),
            )
            self.table.setItem(row, 3, QTableWidgetItem(enrolled_students_names))
            self.table.setItem(row, 4, QTableWidgetItem("Active"))
            self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)
    # Edit a course
    def edit_record_by_id(self, course_id):
        """
        Populate the course edit dialog for a specific course, identified by ID.

        This method searches for the course to be edited by ID in the loaded courses list from the database, then calls the edit_record() method 
        to apply the editing and update the related database entries.

        :param course_id: ID of the course to be edited
        :type course_id: str

        :return: None
        """
        for idx, c in enumerate(self.courses):
            if c.course_id == course_id:
                self.edit_record(idx)
                break

    def edit_record(self, row):
        """
        Edit a specific course's ID or name.

        This method references the course by ID, updates its name and/or ID and propagates the change to the linked assigned instructor and enrolled students.
        Once the changes are committed to the database, it refreshes the student table and instructor table to reflect the change, reloads the course data into the table, 
        and provides user feedback via a message box.

        :return: None
        """
        course = self.courses[row]
        dialog = EditCourseDialog(course, self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            # Capture old ID before applying edits so we can fix references
            old_course_id = course.course_id
            dialog.save_changes()

            # If the ID changed, rename in DB and propagate; else just update name/instructor/enrolled
            try:
                if course.course_id != old_course_id:
                    # Rename the course ID and keep the name consistent
                    self.dm.rename_course_id_in_db(old_course_id, course.course_id, course.course_name)
                else:
                    self.dm.update_course_in_db(course)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return
            

            # If course instructor or enrolled students are linked, update them as well
            if course.course_instructor:
                # Ensure the course appears exactly once in the instructor's assigned list
                instructor = course.course_instructor
                instructor.assigned_courses = [
                    c for c in instructor.assigned_courses if c.course_id != old_course_id
                ]
                instructor.assigned_courses.append(course)
                self.dm.update_instructor_in_db(instructor)
            if course.enrolled_students:
                for student in course.enrolled_students:
                    student.registered_courses = [
                        c for c in student.registered_courses if c.course_id != old_course_id
                    ]
                    student.registered_courses.append(course)
                    self.dm.update_student_in_db(student)
            self.load_course_data()
            # Notify other views to refresh
            self.data_updated.emit()
            QMessageBox.information(self, "Success", f"Course '{course.course_name}' updated successfully.")

    # Delete a course
    def delete_record_by_id(self, course_id):
        """
        Delete a specific course, identified by ID.

        This method searches for the course to be deleted by ID in the loaded courses list from the database, then calls the delete_record() method 
        to remove that record and update the related database entries. 

        :param course_id: ID of the course to be edited
        :type course_id: str
        
        :return: None
        """
        for idx, c in enumerate(self.courses):
            if c.course_id == course_id:
                self.delete_record(idx)
                break

    def delete_record(self, row):
        """
        Delete a specific course.

        This method confirms the user's request to delete the selected course record, removes the course from the assigned courses list of the corresponding instructor, and from
        the registered courses list of the enrolled students. It then deletes the course record from the database,  reloads the courses data into the table, and provides user feedback via a message box. 

        :return: None
        """
        course = self.courses[row]
        try:
            # Confirm deletion
            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the course '{course.course_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm != QMessageBox.Yes:
                return
            else:
                # Unassign instructor (if any)
                if course.course_instructor is not None:
                    instructor = course.course_instructor
                    instructor.assigned_courses = [
                        c for c in instructor.assigned_courses if c.course_id != course.course_id
                    ]
                    self.dm.update_instructor_in_db(instructor)
                

                # Remove course from all students
                for student in course.enrolled_students:
                    # Remove by ID to avoid identity mismatches
                    if any(c.course_id == course.course_id for c in student.registered_courses):
                        student.registered_courses = [
                            c for c in student.registered_courses if c.course_id != course.course_id
                        ]
                        self.dm.update_student_in_db(student)
                self.dm.delete_course_from_db(course.course_id)
                # Refresh table view
                self.load_course_data()

                # Notify other views to refresh
                self.data_updated.emit()

                
                QMessageBox.information(self, "Deleted", f"Course '{course.course_name}' deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Search courses
    def search_bar(self):#

        """
        Search for the course by ID, name, enrolled student names, or assigned instructor.

        This method allows the user to input a filtering query, and displays courses accordingly.
        It hides non-matching rows and rebuilds the table to only display the records that have an ID, name, assigned instructor name, or enrolled student name matching the user's input text.

        :return: None
        """
        search_query = self.search_input.text().strip().lower()
        courses = self.dm.load_courses_from_db()

        if not search_query:
            self.load_course_data()
            return

        filtered = []
        for course in courses:
            if (
                search_query in course.course_id.lower()
                or search_query in course.course_name.lower()
                or (course.course_instructor and search_query in course.course_instructor.name.lower())
            ):
                filtered.append(course)
                continue

            for student in course.enrolled_students:
                if search_query in student.name.lower() or search_query in student.student_id.lower():
                    filtered.append(course)
                    break

        self.table.setRowCount(0)
        self.table.setRowCount(len(filtered))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Course ID", "Name", "Instructor", "Enrolled Students", "Status", "Actions"
        ])

        for row, course in enumerate(filtered):
            instructor_name = course.course_instructor.name if course.course_instructor else "—"
            enrolled_students_names = (
                ", ".join(student.name for student in course.enrolled_students)
                if course.enrolled_students else "None"
            )

            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            edit_button.clicked.connect(lambda _, cid=course.course_id: self.edit_record_by_id(cid))
            delete_button.clicked.connect(lambda _, cid=course.course_id: self.delete_record_by_id(cid))

            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            self.table.setItem(row, 0, QTableWidgetItem(course.course_id))
            self.table.setItem(row, 1, QTableWidgetItem(course.course_name))
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    course.course_instructor.name if course.course_instructor else "N/A"
                ),
            )
            self.table.setItem(row, 3, QTableWidgetItem(enrolled_students_names))
            self.table.setItem(row, 4, QTableWidgetItem("Active"))
            self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)

    # Export courses to CSV
    def export_to_csv(self):
        """
        Export all course records to a CSV file.

        This method loads all courses data from database, and writes them into a timestamped CSV file. 
        Each course record includes the ID, name, list of enrolled students, and assigned instructor. 
        Once the data is exported, a success message is provided to the user via a message box; otherwise, an error message is displayed. 
        :return: None
        """
        try:
            courses = self.dm.load_courses_from_db()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"courses_{timestamp}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Course ID", "Name", "Instructor", "Enrolled Students", "Status"])
                for course in courses:
                    instructor_name = course.course_instructor.name if course.course_instructor else "—"
                    students = ", ".join(s.name for s in course.enrolled_students)
                    writer.writerow([course.course_id, course.course_name, instructor_name, students, "Active"])
            QMessageBox.information(self, "Export Successful", f"Exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export courses: {e}")


# Edit Course Dialog
class EditCourseDialog(QDialog):

    """
    A dialog window for editing an existing course's ID and name.

    :param course: the course object being edited.
    :type course: Course
    :param parent: Optional parent widget.
    :type parent: QWidget, optional

    :ivar course: Reference to the course being edited.
    :vartype course: Course
    :ivar id_input: Input field for the course ID.
    :vartype id_input: QLineEdit
    :ivar name_input: Input field for the course name.
    :vartype name_input: QLineEdit
    """
    def __init__(self, course, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Course")
        self.course = course

        layout = QFormLayout()

        self.id_input = QLineEdit(course.course_id)
        self.name_input = QLineEdit(course.course_name)

        layout.addRow("Course ID:", self.id_input)
        layout.addRow("Course Name:", self.name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def save_changes(self):
        """"
        Save the edited course ID and name.

        This method retrieves the updated course ID and name from the course editing dialong, and assigns them to the corresponding attributes of the course object.
        It performs basic validation by stripping whitespace, and raises an exception if an error occurs during the process of updating the course object.

        :raises Exception: If an error occurs while applying the changes to the selected course.
        :return: None
        """
        try:
            self.course.course_id = self.id_input.text().strip()
            self.course.course_name = self.name_input.text().strip()
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", str(e))
            raise

