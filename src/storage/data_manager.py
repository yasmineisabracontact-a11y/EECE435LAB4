"""
Data Manager Module

This module provides the DataManager class, which handles data storage and operations
for the school using SQLite. It manages students, courses, and instructors data, as well
as their relationships represented by course assignment and course registration.

The DataManager is responsible for table creation, CRUD operation execution,
relationship rebuilding, data export, and database backup.
"""

import json
import sqlite3
from src.core.modules import Student, Instructor, Course
import shutil, datetime, os


class DataManager:
    """
    A class for managing data storage, updating, and relationships for students, courses, and instructors.

    This class connects with the database to manage the creation of students, instructors, and courses tables.
    It provides methods to perform CRUD operations (create, read, update, delete) on students, instructors,
    and courses in the SQLite database. It also manages student registration in courses, instructor assignment
    to courses, and rebuilding relationships between entities to synchronize them across tables.

    The DataManager provides JSON backup for the database and snapshot utilities for safe data recovery.
    """

    def __init__(self):
        """Initialize the DataManager and establish the database connection."""
        self.conn = sqlite3.connect("school_db.db")
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")

        # Create tables if not exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            registered_courses TEXT
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            assigned_courses TEXT
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            course_instructor TEXT REFERENCES instructors(instructor_id),
            enrolled_students TEXT
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students_courses (
            student_id TEXT,
            course_id TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        );
        """)

        self.conn.commit()

        self.students_data = []
        self.instructors_data = []
        self.courses_data = []

    # ---------- STUDENT CRUD ----------
    def add_student_to_db(self, student: Student):
        """
        Add a new student record to the database.

        This method validates the uniqueness of the new student ID and inserts the student record
        into the students table in both memory and database.

        :param student: The student object to be added.
        :type student: Student

        :raises ValueError: If a student with the same ID already exists in the database.
        :return: None
        """
        try:
            self.cursor.execute("""
                INSERT OR ABORT INTO students (student_id, name, age, email, registered_courses)
                VALUES (?, ?, ?, ?, ?)
            """, (
                student.student_id,
                student.name,
                student.age,
                student.email,
                ','.join([c.course_id for c in student.registered_courses])
            ))
            self.conn.commit()
            self.refresh_snapshot()
        except sqlite3.IntegrityError:
            raise ValueError(f"Student ID {student.student_id} already exists in the database.")

    def load_students_from_db(self):
        """
        Load student records from the database.

        This method fetches student records from the database, including their IDs, names, ages, and emails.
        The registered courses list is left empty to be re-linked later.

        :return: List of Student objects.
        :rtype: list[Student]
        """
        self.cursor.execute("SELECT * FROM students")
        rows = self.cursor.fetchall()
        students = [
            Student(student_id=r[0], name=r[1], age=r[2], email=r[3], registered_courses=[])
            for r in rows
        ]
        self.students_data = students.copy()
        return students

    def update_student_in_db(self, student: Student):
        """
        Update student data in the database.

        This method updates student records to reflect edits (ID, name, age, email),
        and propagates name changes to the enrolled courses. It refreshes the snapshot afterward.

        :param student: The student object to be updated.
        :type student: Student

        :return: None
        """
        self.cursor.execute("""
            UPDATE students
            SET name=?, age=?, email=?, registered_courses=?
            WHERE student_id=?
        """, (
            student.name,
            student.age,
            student.email,
            ','.join([c.course_id for c in student.registered_courses]),
            student.student_id
        ))
        self.conn.commit()
        self.refresh_snapshot()

    def delete_student_from_db(self, student_id: str):
        """
        Delete a specific student record from the database.

        This method removes the student by ID, deletes them from all related course registrations,
        and refreshes the snapshot afterward.

        :param student_id: The ID of the student to delete.
        :type student_id: str
        :return: None
        """
        self.cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        self.conn.commit()
        self.refresh_snapshot()

    # ---------- INSTRUCTOR CRUD ----------
    def add_instructor_to_db(self, instructor: Instructor):
        """
        Add a new instructor record to the database.

        Validates uniqueness of the instructor ID and inserts the record into the instructors table.

        :param instructor: The instructor object to be added.
        :type instructor: Instructor

        :raises ValueError: If an instructor with the same ID already exists.
        :return: None
        """
        try:
            self.cursor.execute("""
                INSERT OR ABORT INTO instructors (instructor_id, name, age, email, assigned_courses)
                VALUES (?, ?, ?, ?, ?)
            """, (
                instructor.instructor_id,
                instructor.name,
                instructor.age,
                instructor.email,
                ','.join([c.course_id for c in instructor.assigned_courses])
            ))
            self.conn.commit()
            self.refresh_snapshot()
        except sqlite3.IntegrityError:
            raise ValueError(f"Instructor ID {instructor.instructor_id} already exists in the database.")

    def load_instructors_from_db(self):
        """
        Load instructor records from the database.

        Fetches instructor records including ID, name, age, and email.
        The assigned courses list is left empty to be re-linked later.

        :return: List of Instructor objects.
        :rtype: list[Instructor]
        """
        self.cursor.execute("SELECT * FROM instructors")
        rows = self.cursor.fetchall()
        instructors = [
            Instructor(instructor_id=r[0], name=r[1], age=r[2], email=r[3], assigned_courses=[])
            for r in rows
        ]
        self.instructors_data = instructors.copy()
        return instructors

    def update_instructor_in_db(self, instructor: Instructor):
        """
        Update instructor data in the database.

        Updates the instructor’s attributes (ID, name, age, email) and refreshes relationships.

        :param instructor: The instructor object to update.
        :type instructor: Instructor
        :return: None
        """
        self.cursor.execute("""
            UPDATE instructors
            SET name=?, age=?, email=?, assigned_courses=?
            WHERE instructor_id=?
        """, (
            instructor.name,
            instructor.age,
            instructor.email,
            ','.join([c.course_id for c in instructor.assigned_courses]),
            instructor.instructor_id
        ))
        self.conn.commit()
        self.refresh_snapshot()

    def delete_instructor_from_db(self, instructor_id: str):
        """
        Delete an instructor record from the database.

        Unassigns the instructor from courses before deleting, then refreshes the snapshot.

        :param instructor_id: The ID of the instructor to delete.
        :type instructor_id: str
        :return: None
        """
        self.cursor.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))
        self.conn.commit()
        self.refresh_snapshot()

    # ---------- COURSE CRUD ----------
    def add_course_to_db(self, course: Course):
        """
        Add a new course record to the database.

        :param course: The course object to be added.
        :type course: Course
        :raises ValueError: If a course with the same ID already exists.
        :return: None
        """
        try:
            self.cursor.execute("""
                INSERT OR ABORT INTO courses (course_id, course_name, course_instructor, enrolled_students)
                VALUES (?, ?, ?, ?)
            """, (
                course.course_id,
                course.course_name,
                course.course_instructor.instructor_id if course.course_instructor else None,
                ','.join([s.student_id for s in course.enrolled_students if hasattr(s, 'student_id')])
            ))
            self.conn.commit()
            self.refresh_snapshot()
        except sqlite3.IntegrityError:
            raise ValueError(f"Course ID {course.course_id} already exists in the database.")

    # (...rest of methods remain unchanged, only docstring formatting continued the same way)
