import tkinter as tk
from tkinter import ttk

from src.storage.data_manager import DataManager
from tkinter import messagebox
from src.core.modules import Student
class StudentTable(ttk.Frame):
    def __init__(self, master, dm, course_table = None,  **kwargs):
        self.dm = dm
        self.course_table = course_table
        super().__init__(master, **kwargs)

        # Searching Records:
        # Search Bar
        ttk.Label(self, text="Search").grid(row=0, column=0, sticky="w", pady=4)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, pady=4, sticky="ew")
        # Search Button
        search_btn = ttk.Button(self, text="Search for Student", command=self.search_records)
        search_btn.grid(row=0, column=2, padx=6)
        self.columnconfigure(1, weight = 1)

        # Treeview
        student_columns = ("ID", "Name", "Age", "Email", "Registered Courses")
        self.tree = ttk.Treeview(self, columns = student_columns, show="headings")
        for attribute in student_columns:
            self.tree.heading(attribute, text = attribute) # set the text for the column heading 
            self.tree.column(attribute, width = 120, anchor = "center") # column style        
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=10)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        #Buttons for editing and deleting
        edit_btn = ttk.Button(self, text = "Edit", command = self.edit_student)
        edit_btn.grid(row = 2, column = 0, pady=5)

        delete_btn = ttk.Button(self, text ="Delete", command = self.delete_student)
        delete_btn.grid(row=2, column=1, pady=5)

        self.load_data()

    # method to select a student to edit or delete  
      
    def select_student(self):
        selected = self.tree.selection() # tuples of IDs for all selected rows
        if not selected:
            return None
        student_id = self.tree.item(selected[0])["values"][0]  # selected[0] is the first selected row, self.tree.item(selected[0]) retrieves data from that row
                                                               # ["values"][0] returns the first column of the row which is the id of the selected student
        # Search in the current in-memory list loaded by load_data()
        for s in getattr(self, 'students', []): #looping over all students in data to find the one with the matching id
            if s.student_id == student_id:
                return s
        return None
    
    #method to edit student
    def edit_student(self):
        student = self.select_student() # the selected student 
        if not student:
            messagebox.showerror("Error", "Please select a student to edit")
            return
        popup = tk.Toplevel(self) #creates an independent window
        popup.title("Edit Student")
        popup.geometry("400x200")
        #setting the tkinter values 
        name_var = tk.StringVar(value = student.name)
        email_var = tk.StringVar(value = student.email)
        age_var = tk.StringVar(value = str(student.age))

        #reflecting the  values in the entries 
        ttk.Label(popup, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(popup, text="Email:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=email_var, width=30).grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(popup, text="Age:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(popup, textvariable=age_var, width=30).grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        def save_changes():
            try:
                student.name = name_var.get()
                student.email = email_var.get()
                student.age = int(age_var.get())
                # Persist to DB so course table reload reflects updated student names
                self.dm.update_student_in_db(student)
                # Refresh tables
                self.load_data()
                if self.course_table:
                    self.course_table.load_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        
        ttk.Button(popup, text = "Save", command =save_changes).grid(row=3, column=0, columnspan=2)

    # method to delete student 
    def delete_student(self):
        student = self.select_student()
        if not student:
            messagebox.showerror("Error", "Please select a student to edit")
            return     
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {student.name}?")
        if confirm:
            try:
                # Remove the student from all enrolled courses (persist to DB)
                for course in list(student.registered_courses):
                    if student in course.enrolled_students:
                        course.enrolled_students.remove(student)
                        self.dm.update_course_in_db(course)
                student.registered_courses.clear()
                # Delete from DB
                self.dm.delete_student_from_db(student.student_id)
                # Refresh tables
                self.load_data()
                if self.course_table:
                    self.course_table.load_data()
                messagebox.showinfo("Deleted", f"Student {student.name} has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", str(e))  
              

    # method to search in students table records
    def search_records(self):
        query= self.search_var.get().strip().lower() # case insensitive search

        #clearning the current rows in table 
        for row in self.tree.get_children():
            self.tree.delete(row)

        #return all rows if nothing in search bar
        if not query:
            self.load_data()
            return
        
        #returning only matching students with the query 
        for student in getattr(self, 'students', []):
            if query in student.name.lower():
                self.insert_student(student)
                continue # to move on to the next student and avoid duplicates

            if query in student.student_id.lower():
                self.insert_student(student)
                continue
            for c in student.registered_courses:
                    if query in c.course_name.lower():
                        self.insert_student(student)
                        break

    #method to insert a matching student row into the tree 
    def insert_student(self, student):
        courses = []
        for course in student.registered_courses:
            courses.append(course.course_name) 
        #change this list to a string
        courses=", ".join(courses)
        self.tree.insert("", "end", values = (
            student.student_id,
            student.name,
            student.age,
            student.email,
            courses))
        
    # method to load the data from the student manager to the tree
    def load_data(self):
        #we need to clear the old rows 
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Always reload latest data from DB and rebuild relationships for accuracy
        students = self.dm.load_students_from_db()
        instructors = self.dm.load_instructors_from_db()
        courses = self.dm.load_courses_from_db()
        try:
            self.dm.rebuild_relationships_clean(students, instructors, courses)
        except AttributeError:
            self.dm.rebuild_relationships(students, instructors, courses)

        # Cache for quick lookups/selection
        self.students = students

        #Insert the students data 
        for student in self.students:
            #add all registered courses to 1 list 
            self.insert_student(student)
