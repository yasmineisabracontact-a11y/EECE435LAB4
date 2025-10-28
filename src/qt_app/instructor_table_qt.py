from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QTableWidget, 
    QDialogButtonBox, QTableWidgetItem, QLabel, QLineEdit, QPushButton, QDialog, QFormLayout
)
from PyQt5.QtCore import pyqtSignal
from src.storage.data_manager import DataManager
import csv, datetime

class InstructorTable(QWidget):
    data_updated = pyqtSignal()
    def __init__(self, dm: DataManager, parent=None):
       
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Instructors"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, Name, Email, or Assigned Courses")
        self.search_input.textChanged.connect(self.search_bar)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)

        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(export_button)

        self.load_instructor_data()


    def load_instructor_data(self):
        students = self.dm.load_students_from_db()
        instructors = self.dm.load_instructors_from_db()
        courses = self.dm.load_courses_from_db()
        # Rebuild relationships (dedup + reset) so assigned_courses reflects DB accurately
        try:
            self.dm.rebuild_relationships_clean(students, instructors, courses)
        except AttributeError:
            self.dm.rebuild_relationships(students, instructors, courses)
        
        

        self.instructors = instructors

        self.table.setRowCount(len(self.instructors))       
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Instructor ID", "Name", "Age", "Email", "Assigned Courses", "Actions"
        ])

        for row, instructor in enumerate(self.instructors):
            assigned_courses_names = (
                ", ".join(course.course_name for course in instructor.assigned_courses)
                if instructor.assigned_courses else "None"
            )

            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            edit_button.clicked.connect(lambda _, iid=instructor.instructor_id: self.edit_record_by_id(iid))
            delete_button.clicked.connect(lambda _, iid=instructor.instructor_id: self.delete_record_by_id(iid))

            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            self.table.setItem(row, 0, QTableWidgetItem(instructor.instructor_id))
            self.table.setItem(row, 1, QTableWidgetItem(instructor.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(instructor.age)))
            self.table.setItem(row, 3, QTableWidgetItem(instructor.email))
            self.table.setItem(row, 4, QTableWidgetItem(assigned_courses_names))
            self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)

    def edit_record_by_id(self, instructor_id):
        for idx, i in enumerate(self.instructors):
            if i.instructor_id == instructor_id:
                self.edit_record(idx)
                break

    def delete_record_by_id(self, instructor_id):
        for idx, i in enumerate(self.instructors):
            if i.instructor_id == instructor_id:
                self.delete_record(idx)
                break

    def edit_record(self, row):
        # Use the in-memory instance so assigned_courses are populated
        instructor = self.instructors[row]
        dialog = EditInstructorDialog(instructor, self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            dialog.save_changes()
            self.dm.update_instructor_in_db(instructor)
            # Ensure all assigned courses point back to this (possibly renamed) instructor
            for course in instructor.assigned_courses:
                try:
                    # If logically the same instructor, setter is safe; otherwise bypass strict setter
                    if course.course_instructor is None or (
                        course.course_instructor and course.course_instructor.instructor_id == instructor.instructor_id
                    ):
                        course.course_instructor = instructor
                    else:
                        # Force re-link to avoid identity mismatch error
                        course._course_instructor = instructor
                except Exception:
                    # As a fallback, force the link and proceed
                    course._course_instructor = instructor
                self.dm.update_course_in_db(course)
            self.load_instructor_data()
            # Notify other views to refresh
            self.data_updated.emit()
            QMessageBox.information(self, "Success", f"Instructor '{instructor.name}' updated successfully.")


    def delete_record(self, row):
        # Use the in-memory instance to access assigned_courses
        instructor = self.instructors[row]
        try:
            for course in instructor.assigned_courses:
                course.course_instructor = None
                self.dm.update_course_in_db(course)

            self.dm.delete_instructor_from_db(instructor.instructor_id)

            self.load_instructor_data()
            # Notify other views to refresh
            self.data_updated.emit()
            QMessageBox.information(self, "Deleted", f"Instructor '{instructor.name}' deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))




            



    def search_bar(self):
        search_query = self.search_input.text().strip().lower()
        # Always rebuild links for search so assigned_courses is populated
        students = self.dm.load_students_from_db()
        instructors = self.dm.load_instructors_from_db()
        courses = self.dm.load_courses_from_db()
        try:
            self.dm.rebuild_relationships_clean(students, instructors, courses)
        except AttributeError:
            self.dm.rebuild_relationships(students, instructors, courses)

        if not search_query:
            self.load_instructor_data()
            return

        filtered = []
        for instructor in instructors:
            if (
                search_query in instructor.instructor_id.lower()
                or search_query in instructor.name.lower()
                or search_query in instructor.email.lower()
            ):
                filtered.append(instructor)
                continue
            for course in instructor.assigned_courses:
                if (
                    search_query in course.course_name.lower()
                    or search_query in course.course_id.lower()
                ):
                    filtered.append(instructor)
                    break

        self.table.setRowCount(0)
        self.table.setRowCount(len(filtered))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Instructor ID", "Name", "Age", "Email", "Assigned Courses", "Actions"
        ])

        for row, instructor in enumerate(filtered):
            assigned_courses_names = (
                ", ".join(course.course_name for course in instructor.assigned_courses)
                if instructor.assigned_courses else "None"
            )

            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            edit_button.clicked.connect(lambda _, iid=instructor.instructor_id: self.edit_record_by_id(iid))
            delete_button.clicked.connect(lambda _, iid=instructor.instructor_id: self.delete_record_by_id(iid))

            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            self.table.setItem(row, 0, QTableWidgetItem(instructor.instructor_id))
            self.table.setItem(row, 1, QTableWidgetItem(instructor.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(instructor.age)))
            self.table.setItem(row, 3, QTableWidgetItem(instructor.email))
            self.table.setItem(row, 4, QTableWidgetItem(assigned_courses_names))
            self.table.setCellWidget(row, self.table.columnCount() - 1, button_widget)

    def export_to_csv(self):
        try:
            instructors = self.dm.load_instructors_from_db()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instructors_{timestamp}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Instructor ID", "Name", "Age", "Email", "Assigned Courses"])
                for instructor in instructors:
                    assigned = ", ".join(course.course_name for course in instructor.assigned_courses)
                    writer.writerow([
                        instructor.instructor_id,
                        instructor.name,
                        instructor.age,
                        instructor.email,
                        assigned
                    ])
            QMessageBox.information(self, "Export Successful", f"Exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export instructors: {e}")


class EditInstructorDialog(QDialog):
    def __init__(self, instructor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Instructor")
        self.instructor = instructor

        layout = QFormLayout()

        self.id_input = QLineEdit(instructor.instructor_id)
        self.name_input = QLineEdit(instructor.name)
        self.age_input = QLineEdit(str(instructor.age))
        self.email_input = QLineEdit(instructor.email)

        layout.addRow("Instructor ID:", self.id_input)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Age:", self.age_input)
        layout.addRow("Email:", self.email_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def save_changes(self):
        try:
            self.instructor.instructor_id = self.id_input.text().strip()
            self.instructor.name = self.name_input.text().strip()
            self.instructor.age = int(self.age_input.text().strip())
            self.instructor.email = self.email_input.text().strip()
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", str(e))
            raise
