from sqlalchemy.orm import Session
from models import Student

# CREATE
def add_student(db: Session, name: str, marks: int):

    student = Student(
        name=name,
        marks=marks
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