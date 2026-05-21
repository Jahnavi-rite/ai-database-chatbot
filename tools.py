from langchain.tools import StructuredTool

from crud import *

from database import SessionLocal


# ==========================================
# GET ALL STUDENTS
# ==========================================

def get_students_tool():

    db = SessionLocal()

    students = get_students(db)

    return {

        "type": "table",

        "title": "All Students",

        "data": [

            {
                "id": s.id,
                "name": s.name,
                "marks": s.marks,
                "course_id": s.course_id
            }

            for s in students
        ]
    }


# ==========================================
# FILTER ABOVE MARKS
# ==========================================

def filter_students_above_marks_tool(

    marks: int
):

    db = SessionLocal()

    students = get_students_above_marks(

        db,

        marks
    )

    return {

        "type": "table",

        "title": f"Students Above {marks}",

        "data": [

            {
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]
    }


# ==========================================
# FILTER BELOW MARKS
# ==========================================

def filter_students_below_marks_tool(

    marks: int
):

    db = SessionLocal()

    students = get_students_below_marks(

        db,

        marks
    )

    return {

        "type": "table",

        "title": f"Students Below {marks}",

        "data": [

            {
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]
    }


# ==========================================
# SEARCH STUDENT
# ==========================================

def search_student_tool(

    name: str
):

    db = SessionLocal()

    students = search_student_by_name(

        db,

        name
    )

    return {

        "type": "table",

        "title": f"Search Results For {name}",

        "data": [

            {
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]
    }


# ==========================================
# SORT ALPHABETICALLY
# ==========================================

def sort_students_alphabetically_tool(

    students: list
):

    if len(students) == 0:

        return {

            "type": "table",

            "title": "Sorted Students",

            "data": []
        }


    if isinstance(students[0], dict):

        sorted_students = sorted(

            students,

            key=lambda x: x["name"]
        )

    else:

        sorted_students = sorted(students)


    return {

        "type": "table",

        "title": "Students Sorted Alphabetically",

        "data": sorted_students
    }


# ==========================================
# SORT HIGHEST MARKS
# ==========================================

def sort_students_highest_marks_tool(

    students: list
):

    sorted_students = sorted(

        students,

        key=lambda x: x["marks"],

        reverse=True
    )

    return {

        "type": "table",

        "title": "Students Sorted By Highest Marks",

        "data": sorted_students
    }


# ==========================================
# COUNT STUDENTS
# ==========================================

def count_students_tool():

    db = SessionLocal()

    return {

        "type": "analytics",

        "title": "Student Count",

        "data": {

            "total_students": count_students(db)
        }
    }


# ==========================================
# COUNT TEACHERS
# ==========================================

def count_teachers_tool():

    db = SessionLocal()

    return {

        "type": "analytics",

        "title": "Teacher Count",

        "data": {

            "total_teachers": count_teachers(db)
        }
    }


# ==========================================
# COUNT COURSES
# ==========================================

def count_courses_tool():

    db = SessionLocal()

    return {

        "type": "analytics",

        "title": "Course Count",

        "data": {

            "total_courses": count_courses(db)
        }
    }


# ==========================================
# TOPPER
# ==========================================

def topper_tool():

    db = SessionLocal()

    students = get_topper(db)

    return {

        "type": "table",

        "title": "Topper Students",

        "data": [

            {
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]
    }


# ==========================================
# STUDENTS + TEACHERS JOIN
# ==========================================

def students_teachers_join_tool():

    db = SessionLocal()

    results = get_students_courses_teachers(db)

    return {

        "type": "table",

        "title": "Students With Teachers",

        "data": [

            {
                "student": r.name,
                "marks": r.marks,
                "course": r.course_name,
                "teacher": r.teacher_name
            }

            for r in results
        ]
    }


# ==========================================
# STUDENTS + COURSES JOIN
# ==========================================

def students_courses_join_tool():

    db = SessionLocal()

    results = get_students_with_courses(db)

    return {

        "type": "table",

        "title": "Students With Courses",

        "data": [

            {
                "student": r.name,
                "course": r.course_name,
                "marks": r.marks
            }

            for r in results
        ]
    }


# ==========================================
# COURSES + TEACHERS JOIN
# ==========================================

def courses_teachers_join_tool():

    db = SessionLocal()

    results = get_courses_with_teachers(db)

    return {

        "type": "table",

        "title": "Courses With Teachers",

        "data": [

            {
                "course": r.course_name,
                "teacher": r.teacher_name
            }

            for r in results
        ]
    }


# ==========================================
# GROUP BY
# ==========================================

def students_per_course_tool():

    db = SessionLocal()

    results = students_per_course(db)

    return {

        "type": "table",

        "title": "Students Per Course",

        "data": [

            {
                "course_name": r.course_name,
                "total_students": r.total_students
            }

            for r in results
        ]
    }


# ==========================================
# ADD STUDENT
# ==========================================

def add_student_tool(

    name: str,

    marks: int,

    course_id: int = None
):

    db = SessionLocal()

    student = add_student(

        db,

        name,

        marks,

        course_id
    )

    return {

        "type": "message",

        "title": "Student Added",

        "data": {

            "message": f"{student.name} added successfully"
        }
    }


# ==========================================
# DELETE STUDENT
# ==========================================

def delete_student_tool(

    name: str
):

    db = SessionLocal()

    delete_student(

        db,

        name
    )

    return {

        "type": "message",

        "title": "Student Deleted",

        "data": {

            "message": f"{name} deleted successfully"
        }
    }


# ==========================================
# UPDATE STUDENT MARKS
# ==========================================

def update_student_marks_tool(

    name: str,

    marks: int
):

    db = SessionLocal()

    update_student_marks(

        db,

        name,

        marks
    )

    return {

        "type": "message",

        "title": "Student Updated",

        "data": {

            "message": f"{name} updated successfully"
        }
    }


# ==========================================
# TOOLS
# ==========================================

tools = [

    StructuredTool.from_function(

        func=get_students_tool,

        name="GetStudents",

        description="Get all students"
    ),

    StructuredTool.from_function(

        func=filter_students_above_marks_tool,

        name="FilterStudentsAboveMarks",

        description="Get students above marks"
    ),

    StructuredTool.from_function(

        func=filter_students_below_marks_tool,

        name="FilterStudentsBelowMarks",

        description="Get students below marks"
    ),

    StructuredTool.from_function(

        func=search_student_tool,

        name="SearchStudent",

        description="Search student by name"
    ),

    StructuredTool.from_function(

        func=sort_students_alphabetically_tool,

        name="SortStudentsAlphabetically",

        description="Sort students alphabetically"
    ),

    StructuredTool.from_function(

        func=sort_students_highest_marks_tool,

        name="SortStudentsHighestMarks",

        description="Sort students by highest marks"
    ),

    StructuredTool.from_function(

        func=count_students_tool,

        name="CountStudents",

        description="Count total students"
    ),

    StructuredTool.from_function(

        func=count_teachers_tool,

        name="CountTeachers",

        description="Count total teachers"
    ),

    StructuredTool.from_function(

        func=count_courses_tool,

        name="CountCourses",

        description="Count total courses"
    ),

    StructuredTool.from_function(

        func=topper_tool,

        name="Topper",

        description="Get topper students"
    ),

    StructuredTool.from_function(

        func=students_teachers_join_tool,

        name="StudentsTeachersJoin",

        description="Get students with teachers"
    ),

    StructuredTool.from_function(

        func=students_courses_join_tool,

        name="StudentsCoursesJoin",

        description="Get students with courses"
    ),

    StructuredTool.from_function(

        func=courses_teachers_join_tool,

        name="CoursesTeachersJoin",

        description="Get courses with teachers"
    ),

    StructuredTool.from_function(

        func=students_per_course_tool,

        name="StudentsPerCourse",

        description="Get number of students per course"
    ),

    StructuredTool.from_function(

        func=add_student_tool,

        name="AddStudent",

        description="Add a student"
    ),

    StructuredTool.from_function(

        func=delete_student_tool,

        name="DeleteStudent",

        description="Delete a student"
    ),

    StructuredTool.from_function(

        func=update_student_marks_tool,

        name="UpdateStudentMarks",

        description="Update student marks"
    )
]