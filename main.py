import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# Database setup
def create_database():
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Create Students table (allow email and phone to be NULL)
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT,
                        phone TEXT)''')

    # Create Courses table
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        course_name TEXT NOT NULL,
                        description TEXT)''')

    # Create Student_Courses table with assigned_date
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_courses (
                        student_id INTEGER,
                        course_id INTEGER,
                        assigned_date TEXT,
                        FOREIGN KEY(student_id) REFERENCES students(id),
                        FOREIGN KEY(course_id) REFERENCES courses(id))''')

    conn.commit()
    conn.close()

# Tkinter window setup
class StudentCourseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Course Management")
        self.root.geometry("600x400")

        # Create a notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill="both")

        # Create frames for each tab
        self.student_frame = ttk.Frame(self.notebook)
        self.course_frame = ttk.Frame(self.notebook)
        self.assign_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.student_frame, text="Manage Students")
        self.notebook.add(self.course_frame, text="Manage Courses")
        self.notebook.add(self.assign_frame, text="Assign Students to Courses")

        # Call functions to populate each tab
        self.manage_students_tab()
        self.manage_courses_tab()
        self.assign_students_tab()

    # Student Management Tab
    def manage_students_tab(self):
        tk.Label(self.student_frame, text="Student Management", font=("Arial", 16)).pack(pady=10)

        # Student form fields
        tk.Label(self.student_frame, text="Name").pack()
        self.student_name_entry = tk.Entry(self.student_frame)
        self.student_name_entry.pack()

        tk.Label(self.student_frame, text="Email (optional)").pack()
        self.student_email_entry = tk.Entry(self.student_frame)
        self.student_email_entry.pack()

        tk.Label(self.student_frame, text="Phone (optional)").pack()
        self.student_phone_entry = tk.Entry(self.student_frame)
        self.student_phone_entry.pack()

        # Student action buttons
        tk.Button(self.student_frame, text="Add Student", command=self.add_student).pack(pady=5)
        tk.Button(self.student_frame, text="View All Students", command=self.view_students).pack(pady=5)

    # Course Management Tab
    def manage_courses_tab(self):
        tk.Label(self.course_frame, text="Course Management", font=("Arial", 16)).pack(pady=10)

        # Course form fields
        tk.Label(self.course_frame, text="Course Name").pack()
        self.course_name_entry = tk.Entry(self.course_frame)
        self.course_name_entry.pack()

        tk.Label(self.course_frame, text="Description").pack()
        self.course_description_entry = tk.Entry(self.course_frame)
        self.course_description_entry.pack()

        # Course action buttons
        tk.Button(self.course_frame, text="Add Course", command=self.add_course).pack(pady=5)
        tk.Button(self.course_frame, text="View All Courses", command=self.view_courses).pack(pady=5)

    # Assign Students to Courses Tab
    def assign_students_tab(self):
        tk.Label(self.assign_frame, text="Assign Students to Courses", font=("Arial", 16)).pack(pady=10)

        # Fetch students and courses for dropdowns
        self.refresh_assign_dropdowns()

        # Assign button
        tk.Button(self.assign_frame, text="Assign Student to Course", command=self.assign_student_to_course).pack(pady=10)

        # View assigned students and courses
        tk.Button(self.assign_frame, text="View Students with Courses", command=self.view_assigned_students).pack(pady=10)

    # Refresh student and course dropdowns in the Assign Students to Courses tab
    def refresh_assign_dropdowns(self):
        # Update the values of the dropdowns without recreating the labels

        # If the dropdowns already exist, just update their values
        if hasattr(self, 'student_dropdown'):
            self.student_list = self.get_students()
            self.course_list = self.get_courses()
            self.student_dropdown['values'] = self.student_list
            self.course_dropdown['values'] = self.course_list
        else:
            # Create the labels and dropdowns only once
            tk.Label(self.assign_frame, text="Select Student").pack(pady=5)
            self.student_var = tk.StringVar(self.assign_frame)
            self.student_dropdown = ttk.Combobox(self.assign_frame, textvariable=self.student_var)
            self.student_list = self.get_students()
            self.student_dropdown['values'] = self.student_list
            self.student_dropdown.pack()

            tk.Label(self.assign_frame, text="Select Course").pack(pady=5)
            self.course_var = tk.StringVar(self.assign_frame)
            self.course_dropdown = ttk.Combobox(self.assign_frame, textvariable=self.course_var)
            self.course_list = self.get_courses()
            self.course_dropdown['values'] = self.course_list
            self.course_dropdown.pack()

    # CRUD Operations for Students
    def add_student(self):
        name = self.student_name_entry.get()
        email = self.student_email_entry.get() or None  # Make email optional
        phone = self.student_phone_entry.get() or None  # Make phone optional
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO students (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.refresh_assign_dropdowns()  # Refresh dropdowns after adding student
            self.clear_student_fields()  # Clear input fields after adding student
        except Exception as e:
            messagebox.showerror("Error", f"Error adding student: {e}")
        conn.close()

    def clear_student_fields(self):
        """Clear the input fields in the Add Student section."""
        self.student_name_entry.delete(0, tk.END)
        self.student_email_entry.delete(0, tk.END)
        self.student_phone_entry.delete(0, tk.END)

    def view_students(self):
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, email FROM students")
        students = cursor.fetchall()
        conn.close()

        view_window = tk.Toplevel(self.root)
        view_window.title("View All Students")
        view_window.geometry("600x400")

        # Create a table format
        tree = ttk.Treeview(view_window, columns=('ID', 'Name', 'Phone', 'Email'), show='headings')
        tree.heading('ID', text='Student ID')
        tree.heading('Name', text='Name')
        tree.heading('Phone', text='Contact No')
        tree.heading('Email', text='Email')

        # Insert student data into the table
        for student in students:
            tree.insert('', tk.END, values=student)

        tree.pack(expand=True, fill="both")

    # CRUD Operations for Courses
    def add_course(self):
        course_name = self.course_name_entry.get()
        description = self.course_description_entry.get()
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO courses (course_name, description) VALUES (?, ?)", (course_name, description))
            conn.commit()
            messagebox.showinfo("Success", "Course added successfully!")
            self.refresh_assign_dropdowns()  # Refresh dropdowns after adding course
            self.clear_course_fields()  # Clear input fields after adding course
        except Exception as e:
            messagebox.showerror("Error", f"Error adding course: {e}")
        conn.close()

    def clear_course_fields(self):
        """Clear the input fields in the Add Course section."""
        self.course_name_entry.delete(0, tk.END)
        self.course_description_entry.delete(0, tk.END)

    def view_courses(self):
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, course_name, description FROM courses")
        courses = cursor.fetchall()
        conn.close()

        view_window = tk.Toplevel(self.root)
        view_window.title("View All Courses")
        view_window.geometry("600x400")

        # Create a table format
        tree = ttk.Treeview(view_window, columns=('ID', 'Course Name', 'Description'), show='headings')
        tree.heading('ID', text='Course ID')
        tree.heading('Course Name', text='Course Name')
        tree.heading('Description', text='Description')

        # Insert course data into the table
        for course in courses:
            tree.insert('', tk.END, values=course)

        tree.pack(expand=True, fill="both")

    # Assign a student to a course
    def assign_student_to_course(self):
        student_name = self.student_var.get()
        course_name = self.course_var.get()

        if not student_name or not course_name:
            messagebox.showerror("Error", "Please select both a student and a course!")
            return

        # Get student_id and course_id
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM students WHERE name=?", (student_name,))
        student_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM courses WHERE course_name=?", (course_name,))
        course_id = cursor.fetchone()[0]

        # Check for duplicate assignment
        cursor.execute("SELECT * FROM student_courses WHERE student_id=? AND course_id=?", (student_id, course_id))
        if cursor.fetchone():
            messagebox.showerror("Error", f"{student_name} is already assigned to {course_name}!")
            conn.close()
            return

        # Add the current date for assignment
        assigned_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor.execute("INSERT INTO student_courses (student_id, course_id, assigned_date) VALUES (?, ?, ?)", 
                           (student_id, course_id, assigned_date))
            conn.commit()
            messagebox.showinfo("Success", f"Assigned {student_name} to {course_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error assigning student to course: {e}")
        conn.close()

    def view_assigned_students(self):
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT courses.id, courses.course_name, students.id, students.name, student_courses.assigned_date
                          FROM students 
                          JOIN student_courses ON students.id = student_courses.student_id 
                          JOIN courses ON courses.id = student_courses.course_id
                          ORDER BY courses.course_name''')
        assigned = cursor.fetchall()
        conn.close()

        view_window = tk.Toplevel(self.root)
        view_window.title("View Students with Assigned Courses")
        view_window.geometry("700x400")

        # Create a table format
        tree = ttk.Treeview(view_window, columns=('Course ID', 'Course Name', 'Student ID', 'Student Name', 'Assigned Date'), show='headings')
        tree.heading('Course ID', text='Course ID')
        tree.heading('Course Name', text='Course Name')
        tree.heading('Student ID', text='Student ID')
        tree.heading('Student Name', text='Student Name')
        tree.heading('Assigned Date', text='Assigned Date')

        # Insert assigned data into the table
        for record in assigned:
            tree.insert('', tk.END, values=record)

        tree.pack(expand=True, fill="both")

    # Helper to fetch student names
    def get_students(self):
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students")
        students = [row[0] for row in cursor.fetchall()]
        conn.close()
        return students

    # Helper to fetch course names
    def get_courses(self):
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in cursor.fetchall()]
        conn.close()
        return courses

# Main function to initialize the app
if __name__ == "__main__":
    create_database()  # Ensure the database is set up
    root = tk.Tk()
    app = StudentCourseApp(root)
    root.mainloop()
