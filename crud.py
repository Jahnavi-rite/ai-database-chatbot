from sqlalchemy.orm import Session
from models import Student, Teacher, Course

# CREATE
# =========================
# CREATE STUDENT
# =========================

def add_student(db, name, marks, course_id=None):

    student = Student(

        name=name,

        marks=marks,

        course_id=course_id
    )

    db.add(student)

    db.commit()

    return student

# READ
def get_students(db: Session):

    return db.query(Student).all()


# UPDATE
def update_student(db: Session, name: str, marks: int):

    student = db.query(Student).filter(
        Student.name == name
    ).first()

    if student:

        student.marks = marks

        db.commit()

    return student


# DELETE
def delete_student(db: Session, name: str):

    name = name.strip().lower()
    print(name)
    students = db.query(Student).all()

    for student in students:

        if student.name.strip().lower() == name:

            db.delete(student)

    db.commit()

    return {
        "message": "Deleted"
    }

def delete_student_by_id(db, student_id):

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student:

        db.delete(student)

        db.commit()

    return student
# =========================
# TEACHER CRUD
# =========================

def add_teacher(db, teacher_name):

    teacher = Teacher(
        teacher_name=teacher_name
    )

    db.add(teacher)

    db.commit()

    return teacher


def get_teachers(db):

    return db.query(Teacher).all()
# =========================
# DELETE TEACHER
# =========================

def delete_teacher(db, teacher_name):

    teacher = db.query(Teacher).filter(

        Teacher.teacher_name == teacher_name

    ).first()

    if teacher:

        db.delete(teacher)

        db.commit()

    return teacher


# =========================
# COURSE CRUD
# =========================

def add_course(db, course_name, teacher_id):

    course = Course(
        course_name=course_name,
        teacher_id=teacher_id
    )

    db.add(course)

    db.commit()

    return course


def get_courses(db):

    return db.query(Course).all()

# =========================
# DELETE COURSE
# =========================

def delete_course(db, course_name):

    course = db.query(Course).filter(

        Course.course_name == course_name

    ).first()

    if course:

        db.delete(course)

        db.commit()

    return course
# =========================
# STUDENT + COURSE JOIN
# =========================

def get_students_with_courses(db):

    results = db.query(

        Student.id,

        Student.name,

        Student.marks,

        Course.course_name

    ).join(

        Course,

        Student.course_id == Course.id

    ).all()

    return results



# =========================
# STUDENT + COURSE + TEACHER JOIN
# =========================

def get_students_courses_teachers(db):

    results = db.query(

        Student.id,

        Student.name,

        Student.marks,

        Course.course_name,

        Teacher.teacher_name

    ).join(

        Course,

        Student.course_id == Course.id

    ).join(

        Teacher,

        Course.teacher_id == Teacher.id

    ).all()

    return results
# =========================
# COURSE + TEACHER JOIN
# =========================

def get_courses_with_teachers(db):

    results = db.query(

        Course.id,

        Course.course_name,

        Teacher.teacher_name

    ).join(

        Teacher,

        Course.teacher_id == Teacher.id

    ).all()

    return results
def get_students_above_marks(db, marks):

    return db.query(Student).filter(

        Student.marks > marks

    ).all()
def get_students_below_marks(db, marks):

    return db.query(Student).filter(

        Student.marks < marks

    ).all()
def search_student_by_name(db, name):

    return db.query(Student).filter(

        Student.name.ilike(f"%{name}%")

    ).all()
def get_topper(db):

    return db.query(Student).order_by(

        Student.marks.desc()

    ).limit(1).all()
def get_lowest_student(db):

    return db.query(Student).order_by(

        Student.marks.asc()

    ).limit(1).all()
def count_students(db):

    return db.query(Student).count()
from sqlalchemy import func

def average_marks(db):

    return db.query(

        func.avg(Student.marks)

    ).scalar()
def get_students_above_marks_with_teachers(db, marks):

    results = db.query(

        Student.id,

        Student.name,

        Student.marks,

        Course.course_name,

        Teacher.teacher_name

    ).join(

        Course,

        Student.course_id == Course.id

    ).join(

        Teacher,

        Course.teacher_id == Teacher.id

    ).filter(

        Student.marks > marks

    ).all()

    return results
# =========================
# COUNT COURSES
# =========================

def count_courses(db):

    return db.query(Course).count()



# =========================
# COUNT TEACHERS
# =========================

def count_teachers(db):

    return db.query(Teacher).count()
# =========================
# SORT STUDENTS BY MARKS
# =========================

def get_students_sorted_by_marks(db):

    return db.query(Student).order_by(

        Student.marks.asc()

    ).all()



# =========================
# HIGHEST MARKS FIRST
# =========================

def get_students_highest_first(db):

    return db.query(Student).order_by(

        Student.marks.desc()

    ).all()



# =========================
# ALPHABETICAL ORDER
# =========================

def get_students_alphabetically(db):

    return db.query(Student).order_by(

        Student.name.asc()

    ).all()
# =========================
# PAGINATION
# =========================

def get_first_five_students(db):

    return db.query(Student).limit(5).all()
# =========================
# ABOVE MARKS IN COURSE
# =========================

def get_students_above_marks_in_course(

    db,

    marks,

    course_name
):

    results = db.query(

        Student.id,

        Student.name,

        Student.marks,

        Course.course_name

    ).join(

        Course,

        Student.course_id == Course.id

    ).filter(

        Student.marks > marks,

        Course.course_name == course_name

    ).all()

    return results
from sqlalchemy import func


# MAXIMUM MARKS
def maximum_marks(db):

    return db.query(

        func.max(Student.marks)

    ).scalar()


# MINIMUM MARKS
def minimum_marks(db):

    return db.query(

        func.min(Student.marks)

    ).scalar()


# AVERAGE MARKS IN COURSE
def average_marks_in_course(

    db,

    course_name
):

    result = db.query(

        func.avg(Student.marks)

    ).join(

        Course,

        Student.course_id == Course.id

    ).filter(

        Course.course_name == course_name

    ).scalar()

    return result
# =========================
# STUDENTS PER COURSE
# =========================

def students_per_course(db):

    results = db.query(

        Course.course_name,

        func.count(Student.id).label("total_students")

    ).join(

        Student,

        Student.course_id == Course.id

    ).group_by(

        Course.course_name

    ).all()

    return results
# =========================
# STUDENT + COURSE + TEACHER JOIN
# =========================

def get_students_courses_teachers(db):

    results = db.query(

        Student.id,

        Student.name,

        Student.marks,

        Course.course_name,

        Teacher.teacher_name

    ).join(

        Course,

        Student.course_id == Course.id

    ).join(

        Teacher,

        Course.teacher_id == Teacher.id

    ).all()

    return results