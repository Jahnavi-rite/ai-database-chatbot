import json
from typing import Optional

from mcp.server.fastmcp import FastMCP
from sqlalchemy import func
from database import SessionLocal
from models import Student, Teacher, Course

mcp = FastMCP(name="Student Database MCP Server")


def _json_response(data: dict) -> str:
    """Serialize response to JSON string for safe MCP transport."""
    return json.dumps(data, default=str)


# ==========================================
# BASIC QUERIES
# ==========================================

@mcp.tool()
def get_students() -> str:
    """Get all students with their id, name, marks, and course_id."""
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        return _json_response({
            "type": "table",
            "title": "All Students",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks, "course_id": s.course_id}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def get_teachers() -> str:
    """Get all teachers with their id and teacher_name."""
    db = SessionLocal()
    try:
        teachers = db.query(Teacher).all()
        return _json_response({
            "type": "table",
            "title": "All Teachers",
            "data": [
                {"id": t.id, "teacher_name": t.teacher_name}
                for t in teachers
            ],
            "count": len(teachers)
        })
    finally:
        db.close()


@mcp.tool()
def get_courses() -> str:
    """Get all courses with their id, course_name, and teacher_id."""
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        return _json_response({
            "type": "table",
            "title": "All Courses",
            "data": [
                {"id": c.id, "course_name": c.course_name, "teacher_id": c.teacher_id}
                for c in courses
            ],
            "count": len(courses)
        })
    finally:
        db.close()


# ==========================================
# ANALYTICS - COUNTS
# ==========================================

@mcp.tool()
def count_students() -> str:
    """Get the total number of students."""
    db = SessionLocal()
    try:
        total = db.query(Student).count()
        return _json_response({"type": "analytics", "title": "Total Students", "data": {"total_students": total}})
    finally:
        db.close()


@mcp.tool()
def count_teachers() -> str:
    """Get the total number of teachers."""
    db = SessionLocal()
    try:
        total = db.query(Teacher).count()
        return _json_response({"type": "analytics", "title": "Total Teachers", "data": {"total_teachers": total}})
    finally:
        db.close()


@mcp.tool()
def count_courses() -> str:
    """Get the total number of courses."""
    db = SessionLocal()
    try:
        total = db.query(Course).count()
        return _json_response({"type": "analytics", "title": "Total Courses", "data": {"total_courses": total}})
    finally:
        db.close()


# ==========================================
# ANALYTICS - MARKS
# ==========================================

@mcp.tool()
def get_topper() -> str:
    """Get the student with the highest marks."""
    db = SessionLocal()
    try:
        student = db.query(Student).order_by(Student.marks.desc()).first()
        if student:
            return _json_response({
                "type": "table",
                "title": "Topper Student",
                "data": [{"id": student.id, "name": student.name, "marks": student.marks}],
                "count": 1
            })
        return _json_response({"type": "table", "title": "Topper Student", "data": [], "count": 0})
    finally:
        db.close()


@mcp.tool()
def get_lowest_student() -> str:
    """Get the student with the lowest marks."""
    db = SessionLocal()
    try:
        student = db.query(Student).order_by(Student.marks.asc()).first()
        if student:
            return _json_response({
                "type": "table",
                "title": "Lowest Marks Student",
                "data": [{"id": student.id, "name": student.name, "marks": student.marks}],
                "count": 1
            })
        return _json_response({"type": "table", "title": "Lowest Marks Student", "data": [], "count": 0})
    finally:
        db.close()


@mcp.tool()
def get_average_marks() -> str:
    """Get the average marks of all students."""
    db = SessionLocal()
    try:
        avg = db.query(func.avg(Student.marks)).scalar()
        return _json_response({"type": "analytics", "title": "Average Marks", "data": {"average_marks": round(float(avg), 2) if avg else 0}})
    finally:
        db.close()


@mcp.tool()
def get_maximum_marks() -> str:
    """Get the maximum marks among all students."""
    db = SessionLocal()
    try:
        mx = db.query(func.max(Student.marks)).scalar()
        return _json_response({"type": "analytics", "title": "Maximum Marks", "data": {"maximum_marks": mx if mx else 0}})
    finally:
        db.close()


@mcp.tool()
def get_minimum_marks() -> str:
    """Get the minimum marks among all students."""
    db = SessionLocal()
    try:
        mn = db.query(func.min(Student.marks)).scalar()
        return _json_response({"type": "analytics", "title": "Minimum Marks", "data": {"minimum_marks": mn if mn else 0}})
    finally:
        db.close()


# ==========================================
# ANALYTICS - COURSE-SPECIFIC
# ==========================================

@mcp.tool()
def get_average_marks_for_course(course_name: str) -> str:
    """Get the average marks for students in a specific course. Parameter: course_name (string)."""
    db = SessionLocal()
    try:
        avg = db.query(func.avg(Student.marks)).join(Course, Student.course_id == Course.id).filter(Course.course_name == course_name).scalar()
        return _json_response({"type": "analytics", "title": f"Average Marks in {course_name}", "data": {"average_marks": round(float(avg), 2) if avg else 0}})
    finally:
        db.close()


@mcp.tool()
def get_maximum_marks_for_course(course_name: str) -> str:
    """Get the maximum marks for students in a specific course. Parameter: course_name (string)."""
    db = SessionLocal()
    try:
        mx = db.query(func.max(Student.marks)).join(Course, Student.course_id == Course.id).filter(Course.course_name == course_name).scalar()
        return _json_response({"type": "analytics", "title": f"Maximum Marks in {course_name}", "data": {"maximum_marks": mx if mx else 0}})
    finally:
        db.close()


@mcp.tool()
def get_minimum_marks_for_course(course_name: str) -> str:
    """Get the minimum marks for students in a specific course. Parameter: course_name (string)."""
    db = SessionLocal()
    try:
        mn = db.query(func.min(Student.marks)).join(Course, Student.course_id == Course.id).filter(Course.course_name == course_name).scalar()
        return _json_response({"type": "analytics", "title": f"Minimum Marks in {course_name}", "data": {"minimum_marks": mn if mn else 0}})
    finally:
        db.close()


@mcp.tool()
def get_topper_for_course(course_name: str) -> str:
    """Get the topper student in a specific course. Parameter: course_name (string)."""
    db = SessionLocal()
    try:
        student = db.query(Student).join(Course, Student.course_id == Course.id).filter(Course.course_name == course_name).order_by(Student.marks.desc()).first()
        if student:
            return _json_response({
                "type": "table",
                "title": f"Topper in {course_name}",
                "data": [{"id": student.id, "name": student.name, "marks": student.marks, "course_name": course_name}],
                "count": 1
            })
        return _json_response({"type": "table", "title": f"Topper in {course_name}", "data": [], "count": 0})
    finally:
        db.close()


# ==========================================
# JOINS
# ==========================================

@mcp.tool()
def get_students_with_courses() -> str:
    """Get all students joined with their course names."""
    db = SessionLocal()
    try:
        results = db.query(
            Student.id, Student.name, Student.marks, Student.course_id, Course.course_name, Course.teacher_id
        ).join(Course, Student.course_id == Course.id).all()
        return _json_response({
            "type": "table",
            "title": "Students With Courses",
            "data": [
                {"id": r.id, "name": r.name, "marks": r.marks, "course_id": r.course_id, "course_name": r.course_name, "teacher_id": r.teacher_id}
                for r in results
            ],
            "count": len(results)
        })
    finally:
        db.close()


@mcp.tool()
def get_students_with_teachers() -> str:
    """Get all students with their course and teacher names."""
    db = SessionLocal()
    try:
        results = db.query(
            Student.id, Student.name, Student.marks, Student.course_id, Course.course_name, Teacher.teacher_name
        ).join(Course, Student.course_id == Course.id).join(Teacher, Course.teacher_id == Teacher.id).all()
        return _json_response({
            "type": "table",
            "title": "Students With Teachers",
            "data": [
                {"id": r.id, "name": r.name, "marks": r.marks, "course_id": r.course_id, "course_name": r.course_name, "teacher_name": r.teacher_name}
                for r in results
            ],
            "count": len(results)
        })
    finally:
        db.close()


@mcp.tool()
def get_courses_with_teachers() -> str:
    """Get all courses with their teacher names."""
    db = SessionLocal()
    try:
        results = db.query(
            Course.id, Course.course_name, Teacher.teacher_name
        ).join(Teacher, Course.teacher_id == Teacher.id).all()
        return _json_response({
            "type": "table",
            "title": "Courses With Teachers",
            "data": [
                {"id": r.id, "course_name": r.course_name, "teacher_name": r.teacher_name}
                for r in results
            ],
            "count": len(results)
        })
    finally:
        db.close()


# ==========================================
# FILTERS
# ==========================================

@mcp.tool()
def get_students_above_marks(marks: int) -> str:
    """Get students with marks strictly greater than the given value. Parameter: marks (integer)."""
    db = SessionLocal()
    try:
        students = db.query(Student).filter(Student.marks > marks).all()
        return _json_response({
            "type": "table",
            "title": f"Students Above {marks} Marks",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def get_students_below_marks(marks: int) -> str:
    """Get students with marks strictly less than the given value. Parameter: marks (integer)."""
    db = SessionLocal()
    try:
        students = db.query(Student).filter(Student.marks < marks).all()
        return _json_response({
            "type": "table",
            "title": f"Students Below {marks} Marks",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def search_student(name: str) -> str:
    """Search students by name (partial match, case-insensitive). Parameter: name (string)."""
    db = SessionLocal()
    try:
        students = db.query(Student).filter(Student.name.ilike(f"%{name}%")).all()
        return _json_response({
            "type": "table",
            "title": f"Search Results for '{name}'",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def get_students_above_marks_in_course(marks: int, course_name: str) -> str:
    """Get students above a marks threshold in a specific course. Parameters: marks (integer), course_name (string)."""
    db = SessionLocal()
    try:
        results = db.query(
            Student.id, Student.name, Student.marks, Course.course_name
        ).join(Course, Student.course_id == Course.id).filter(
            Student.marks > marks,
            Course.course_name == course_name
        ).all()
        return _json_response({
            "type": "table",
            "title": f"Students Above {marks} in {course_name}",
            "data": [
                {"id": r.id, "name": r.name, "marks": r.marks, "course_name": r.course_name}
                for r in results
            ],
            "count": len(results)
        })
    finally:
        db.close()


# ==========================================
# SORTING
# ==========================================

@mcp.tool()
def sort_students_by_marks_ascending() -> str:
    """Get all students sorted by marks in ascending order (lowest first)."""
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.marks.asc()).all()
        return _json_response({
            "type": "table",
            "title": "Students Sorted by Marks (Ascending)",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def sort_students_by_marks_descending() -> str:
    """Get all students sorted by marks in descending order (highest first)."""
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.marks.desc()).all()
        return _json_response({
            "type": "table",
            "title": "Students Sorted by Marks (Descending)",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def sort_students_alphabetically() -> str:
    """Get all students sorted alphabetically by name (A to Z)."""
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.name.asc()).all()
        return _json_response({
            "type": "table",
            "title": "Students Sorted Alphabetically (A-Z)",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


# ==========================================
# PAGINATION
# ==========================================

@mcp.tool()
def get_first_five_students() -> str:
    """Get the first 5 students from the database."""
    db = SessionLocal()
    try:
        students = db.query(Student).limit(5).all()
        return _json_response({
            "type": "table",
            "title": "First 5 Students",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students)
        })
    finally:
        db.close()


@mcp.tool()
def get_students_paginated(offset: int = 0, limit: int = 10) -> str:
    """Get students with pagination. Parameters: offset (integer, default 0), limit (integer, default 10)."""
    db = SessionLocal()
    try:
        students = db.query(Student).offset(offset).limit(limit).all()
        total = db.query(Student).count()
        return _json_response({
            "type": "table",
            "title": f"Students (offset={offset}, limit={limit})",
            "data": [
                {"id": s.id, "name": s.name, "marks": s.marks}
                for s in students
            ],
            "count": len(students),
            "total": total
        })
    finally:
        db.close()


# ==========================================
# GROUP BY
# ==========================================

@mcp.tool()
def get_students_per_course() -> str:
    """Get the number of students enrolled in each course."""
    db = SessionLocal()
    try:
        results = db.query(
            Course.course_name,
            func.count(Student.id).label("total_students")
        ).join(Student, Student.course_id == Course.id).group_by(Course.course_name).all()
        return _json_response({
            "type": "table",
            "title": "Students Per Course",
            "data": [
                {"course_name": r.course_name, "total_students": r.total_students}
                for r in results
            ],
            "count": len(results)
        })
    finally:
        db.close()


# ==========================================
# CRUD - STUDENTS
# ==========================================

@mcp.tool()
def add_student(name: str, marks: int, course_id: Optional[int] = None) -> str:
    """Add a new student. Parameters: name (string), marks (integer), course_id (optional integer)."""
    db = SessionLocal()
    try:
        student = Student(name=name, marks=marks, course_id=course_id)
        db.add(student)
        db.commit()
        return _json_response({
            "type": "message",
            "title": "Student Added",
            "data": {"message": f"Student '{name}' added with ID {student.id}"}
        })
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


@mcp.tool()
def update_student_marks(student_id: int, marks: int) -> str:
    """Update marks for a student by ID. Parameters: student_id (integer), marks (integer)."""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            student.marks = marks
            db.commit()
            return _json_response({"type": "message", "title": "Student Updated", "data": {"message": f"Student {student.name} marks updated to {marks}"}})
        return _json_response({"type": "error", "title": "Not Found", "data": {"message": f"Student with ID {student_id} not found"}})
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


@mcp.tool()
def update_student_course(student_id: int, course_id: int) -> str:
    """Update course for a student by ID. Parameters: student_id (integer), course_id (integer)."""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            student.course_id = course_id
            db.commit()
            return _json_response({"type": "message", "title": "Student Updated", "data": {"message": f"Student {student.name} course updated to {course_id}"}})
        return _json_response({"type": "error", "title": "Not Found", "data": {"message": f"Student with ID {student_id} not found"}})
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


@mcp.tool()
def delete_student_by_id(student_id: int) -> str:
    """Delete a student by ID. Parameter: student_id (integer)."""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            db.delete(student)
            db.commit()
            return _json_response({"type": "message", "title": "Student Deleted", "data": {"message": f"Student '{student.name}' deleted"}})
        return _json_response({"type": "error", "title": "Not Found", "data": {"message": f"Student with ID {student_id} not found"}})
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


# ==========================================
# CRUD - TEACHERS
# ==========================================

@mcp.tool()
def add_teacher(teacher_name: str) -> str:
    """Add a new teacher. Parameter: teacher_name (string)."""
    db = SessionLocal()
    try:
        teacher = Teacher(teacher_name=teacher_name)
        db.add(teacher)
        db.commit()
        return _json_response({
            "type": "message",
            "title": "Teacher Added",
            "data": {"message": f"Teacher '{teacher_name}' added with ID {teacher.id}"}
        })
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


@mcp.tool()
def delete_teacher_by_id(teacher_id: int) -> str:
    """Delete a teacher by ID. Parameter: teacher_id (integer)."""
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if teacher:
            db.delete(teacher)
            db.commit()
            return _json_response({"type": "message", "title": "Teacher Deleted", "data": {"message": f"Teacher '{teacher.teacher_name}' deleted"}})
        return _json_response({"type": "error", "title": "Not Found", "data": {"message": f"Teacher with ID {teacher_id} not found"}})
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


# ==========================================
# CRUD - COURSES
# ==========================================

@mcp.tool()
def add_course(course_name: str, teacher_id: int) -> str:
    """Add a new course. Parameters: course_name (string), teacher_id (integer)."""
    db = SessionLocal()
    try:
        course = Course(course_name=course_name, teacher_id=teacher_id)
        db.add(course)
        db.commit()
        return _json_response({
            "type": "message",
            "title": "Course Added",
            "data": {"message": f"Course '{course_name}' added with ID {course.id}"}
        })
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()


@mcp.tool()
def delete_course_by_id(course_id: int) -> str:
    """Delete a course by ID. Parameter: course_id (integer)."""
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            db.delete(course)
            db.commit()
            return _json_response({"type": "message", "title": "Course Deleted", "data": {"message": f"Course '{course.course_name}' deleted"}})
        return _json_response({"type": "error", "title": "Not Found", "data": {"message": f"Course with ID {course_id} not found"}})
    except Exception as e:
        db.rollback()
        return _json_response({"type": "error", "title": "Error", "data": {"message": str(e)}})
    finally:
        db.close()
