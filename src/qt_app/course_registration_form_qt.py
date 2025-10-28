from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit
from PyQt5.QtCore import pyqtSignal
from src.storage.data_manager import DataManager
from src.core.modules import Student, Course


class CourseRegistrationForm(QWidget):
    data_updated = pyqtSignal()  # Signal to notify other components that data changed

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm

        layout = QVBoxLayout()

        # Student ID input
        layout.addWidget(QLabel("Student ID"))
        self.student_id = QLineEdit()
        layout.addWidget(self.student_id)

        # Course selection dropdown
        layout.addWidget(QLabel("Courses"))
        self.courses_dropdown = QComboBox()
        self.load_courses_into_dropdown()
        layout.addWidget(self.courses_dropdown)

        # Register button
        register_button = QPushButton("Register Course")
        register_button.clicked.connect(self.register_course)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def load_courses_into_dropdown(self):
        """Load course names into the dropdown from database."""
        self.courses_dropdown.clear()
        for course in self.dm.load_courses_from_db():
            self.courses_dropdown.addItem(f"{course.course_name} ({course.course_id})")

    def register_course(self):
        try:
            input_student_id = self.student_id.text().strip()
            selection_text = self.courses_dropdown.currentText()

            # Validate input
            if not input_student_id or not selection_text:
                raise ValueError("Please enter a valid Student ID and select a Course.")

            # Extract course_id from selection like "Name (ID)" if present
            matched_course_id = None
            matched_course_name = None
            if selection_text.endswith(")") and "(" in selection_text:
                try:
                    left = selection_text.rfind("(")
                    matched_course_id = selection_text[left+1:-1]
                    matched_course_name = selection_text[:left].strip()
                except Exception:
                    matched_course_id = None
                    matched_course_name = None
            # Fallback: lookup by name (unique name assumed)
            if not matched_course_id:
                for course in self.dm.load_courses_from_db():
                    if course.course_name == selection_text:
                        matched_course_id = course.course_id
                        matched_course_name = course.course_name
                        break

            if not matched_course_id:
                raise ValueError(f"Course '{selection_text}' not found in database.")

            # Perform atomic registration (merge, don't overwrite)
            self.dm.register_student_in_course(input_student_id, matched_course_id)

            # Notify user
            QMessageBox.information(
                self,
                "Success",
                f"Student {input_student_id} registered for {matched_course_name} successfully."
            )

            # Emit signal to update GUI tables
            self.data_updated.emit()

            # Clear inputs
            self.student_id.clear()
            if self.courses_dropdown.count() > 0:
                self.courses_dropdown.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
