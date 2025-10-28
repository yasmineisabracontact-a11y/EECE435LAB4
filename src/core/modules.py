"""
Students, Instructors, and Courses Module

This module defines the Person class, which serves as the base class for Student 
and Instructor. It also defines the Course class that represents course entities 
and manages their relationships with students and instructors.

All classes include validation logic, property accessors, and methods to convert 
objects to and from dictionary format for database and JSON storage integration.
"""


class Person:
    """
    Base class representing a person in the school system.

    This class defines common attributes and validation logic for name, email, 
    and age, which are inherited by both Student and Instructor classes.

    :param name: The name of the person.
    :type name: str
    :param email: The email address of the person.
    :type email: str
    :param age: The age of the person.
    :type age: int
    """

    def __init__(self, name: str, email: str, age: int):
        self.name = name
        self.email = email
        self.age = age

    @property
    def name(self):
        """Get or set the person's name."""
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        if not value.strip():
            raise ValueError("Name must not be empty.")
        self._name = value

    @property
    def email(self):
        """Get or set the person's email address."""
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise ValueError("Email must be a string.")
        if not value.strip():
            raise ValueError("Email must not be empty.")
        if not value.endswith("starschool.com"):
            raise ValueError("Email must end with @starschool.com.")
        self._email = value

    @property
    def age(self):
        """Get or set the person's age."""
        return self._age

    @age.setter
    def age(self, value):
        if not isinstance(value, int):
            raise ValueError("Age must be an integer.")
        if value < 0:
            raise ValueError("Age must be non-negative.")
        self._age = value

    def introduce(self):
        """Print a short introduction for the person."""
        print(f"Hi, my name is {self.name}, {self.age} years old. You can reach me at {self.email}.")


class Student(Person):
    """
    Represents a student in the school system.

    Inherits from Person and adds a unique student ID and a list of registered courses.

    :param name: Student's name.
    :type name: str
    :param email: Student's email.
    :type email: str
    :param age: Student's age.
    :type age: int
    :param student_id: Unique student identifier (must start with 'S').
    :type student_id: str
    :param registered_courses: List of courses the student is registered in.
    :type registered_courses: list[Course]
    """

    def __init__(self, name, email, age, student_id: str, registered_courses: list):
        super().__init__(name, email, age)
        self.student_id = student_id
        self.registered_courses = registered_courses if registered_courses is not None else []

    @property
    def student_id(self):
        """Get or set the student's ID."""
        return self._student_id

    @student_id.setter
    def student_id(self, value):
        if not isinstance(value, str):
            raise ValueError("Student IDs must be strings.")
        if not value.strip():
            raise ValueError("Student ID must not be empty.")
        if not value.startswith("S"):
            raise ValueError("Your ID must start with 'S'.")
        self._student_id = value

    @property
    def id(self):
        """Alias property for student_id."""
        return self.student_id

    @id.setter
    def id(self, value):
        self.student_id = value

    @property
    def registered_courses(self):
        """Get or set the list of courses the student is registered in."""
        return self._registered_courses

    @registered_courses.setter
    def registered_courses(self, value):
        if not isinstance(value, list):
            raise ValueError("Registered courses must be a list.")
        for course in value:
            if not isinstance(course, Course):
                raise ValueError("Courses must be Course objects.")
        self._registered_courses = value

    def register_course(self, course):
        """
        Register the student in a new course.

        :param course: The course to register in.
        :type course: Course
        :raises ValueError: If the course is already registered or invalid.
        """
        if not isinstance(course, Course):
            raise ValueError("Courses must be Course objects.")
        if course in self._registered_courses:
            raise ValueError(f"Student is already registered in {course.course_name}.")
        self._registered_courses.append(course)

    def introduce(self):
        """Print a student-specific introduction."""
        print(f"I am {self.name}, a student with ID {self.student_id}.")

    def to_dict(self) -> dict:
        """
        Convert the student object into a dictionary for serialization.

        :return: Dictionary representation of the student.
        :rtype: dict
        """
        registered_course_ids = [course.course_id for course in self.registered_courses]
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "registered_courses_ids": registered_course_ids,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Create a Student object from a dictionary.

        :param data: Dictionary containing student data.
        :type data: dict
        :return: A Student instance.
        :rtype: Student
        """
        return cls(
            name=data["name"],
            email=data["email"],
            age=data["age"],
            student_id=data["student_id"],
            registered_courses=[],
        )


class Instructor(Person):
    """
    Represents an instructor in the school system.

    Inherits from Person and adds a unique instructor ID and assigned courses list.

    :param name: Instructor's name.
    :type name: str
    :param email: Instructor's email.
    :type email: str
    :param age: Instructor's age.
    :type age: int
    :param instructor_id: Unique instructor identifier (must start with 'I').
    :type instructor_id: str
    :param assigned_courses: List of courses assigned to this instructor.
    :type assigned_courses: list[Course]
    """

    def __init__(self, name, email, age, instructor_id: str, assigned_courses: list):
        super().__init__(name, email, age)
        self.instructor_id = instructor_id
        self.assigned_courses = assigned_courses if assigned_courses is not None else []

    @property
    def instructor_id(self):
        """Get or set the instructor's ID."""
        return self._instructor_id

    @instructor_id.setter
    def instructor_id(self, value):
        if not isinstance(value, str):
            raise ValueError("Instructor IDs must be strings.")
        if not value.strip():
            raise ValueError("Instructor ID must not be empty.")
        if not value.startswith("I"):
            raise ValueError("Your ID must start with 'I'.")
        self._instructor_id = value

    @property
    def assigned_courses(self):
        """Get or set the list of assigned courses."""
        return self._assigned_courses

    @assigned_courses.setter
    def assigned_courses(self, value):
        if not isinstance(value, list):
            raise ValueError("Assigned courses must be a list.")
        for course in value:
            if not isinstance(course, Course):
                raise ValueError("Courses must be Course objects.")
        self._assigned_courses = value

    def assign_course(self, course):
        """Assign a new course to the instructor."""
        if not isinstance(course, Course):
            raise ValueError("Assigned course must be a Course object.")
        if course in self._assigned_courses:
            raise ValueError(f"{course.course_name} is already assigned to this instructor.")
        self._assigned_courses.append(course)

    def introduce(self):
        """Print an instructor-specific introduction."""
        print(f"I am {self.name}, an instructor with ID {self.instructor_id}.")

    def to_dict(self) -> dict:
        """
        Convert the instructor object into a dictionary for serialization.

        :return: Dictionary representation of the instructor.
        :rtype: dict
        """
        assigned_course_ids = [course.course_id for course in self.assigned_courses]
        return {
            "instructor_id": self.instructor_id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "assigned_courses_ids": assigned_course_ids,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Instructor":
        """
        Create an Instructor object from a dictionary.

        :param data: Dictionary containing instructor data.
        :type data: dict
        :return: An Instructor instance.
        :rtype: Instructor
        """
        return cls(
            name=data["name"],
            email=data["email"],
            age=data["age"],
            instructor_id=data["instructor_id"],
            assigned_courses=[],
        )


class Course:
    """
    Represents a course offered in the school.

    Each course has a unique ID, a name, an assigned instructor, and a list of enrolled students.

    :param course_id: Unique course identifier (must start with 'C').
    :type course_id: str
    :param course_name: Name of the course.
    :type course_name: str
    :param course_instructor: Instructor assigned to teach this course.
    :type course_instructor: Instructor, optional
    :param enrolled_students: List of students enrolled in this course.
    :type enrolled_students: list[Student], optional
    """

    def __init__(self, course_id: str, course_name: str, course_instructor: "Instructor" = None, enrolled_students: list = None):
        self.course_id = course_id
        self.course_name = course_name
        self.course_instructor = course_instructor
        self.enrolled_students = enrolled_students if enrolled_students is not None else []

    @property
    def course_id(self):
        """Get or set the course ID."""
        return self._course_id

    @course_id.setter
    def course_id(self, value):
        if not isinstance(value, str):
            raise ValueError("Course IDs must be strings.")
        if not value.strip():
            raise ValueError("Course IDs must not be empty.")
        if not value.startswith("C"):
            raise ValueError("Course IDs must start with 'C'.")
        self._course_id = value

    @property
    def course_name(self):
        """Get or set the course name."""
        return self._course_name

    @course_name.setter
    def course_name(self, value):
        if not isinstance(value, str):
            raise ValueError("Course name must be a string.")
        if not value.strip():
            raise ValueError("Course name must not be empty.")
        self._course_name = value

    @property
    def course_instructor(self):
        """Get or set the instructor assigned to the course."""
        return self._course_instructor

    @course_instructor.setter
    def course_instructor(self, value):
        if value is not None and not isinstance(value, Instructor):
            raise ValueError("Course instructor must be an Instructor object.")
        if hasattr(self, "_course_instructor") and self._course_instructor is not None and value is not None and self._course_instructor != value:
            raise ValueError(f"Course {self.course_name} is already assigned to instructor {self._course_instructor.name}.")
        self._course_instructor = value

    @property
    def enrolled_students(self):
        """Get or set the list of students enrolled in this course."""
        return self._enrolled_students

    @enrolled_students.setter
    def enrolled_students(self, value):
        if not isinstance(value, list):
            raise ValueError("Enrolled students must be a list.")
        for student in value:
            if not isinstance(student, Student):
                raise ValueError("Enrolled students must be Student objects.")
        self._enrolled_students = value

    def register_student(self, student: Student):
        """
        Register a student in this course.

        :param student: The student to register.
        :type student: Student
        :raises ValueError: If the student is already registered or invalid.
        """
        if not isinstance(student, Student):
            raise ValueError("Students must be Student objects.")
        if student in self.enrolled_students:
            raise ValueError(f"Student is already registered in {self.course_name}.")
        self._enrolled_students.append(student)

    def to_dict(self) -> dict:
        """
        Convert the course object into a dictionary for serialization.

        :return: Dictionary representation of the course.
        :rtype: dict
        """
        enrolled_student_ids = [student.student_id for student in self.enrolled_students]
        instructor_id = self.course_instructor.instructor_id if self.course_instructor else None
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor_id": instructor_id,
            "enrolled_students_ids": enrolled_student_ids,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Course":
        """
        Create a Course object from a dictionary.

        :param data: Dictionary containing course data.
        :type data: dict
        :return: A Course instance.
        :rtype: Course
        """
        return cls(
            course_id=data["course_id"],
            course_name=data["course_name"],
            course_instructor=None,
            enrolled_students=[],
        )
