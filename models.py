from sqlalchemy import Column, Integer, String, ForeignKey

from database import Base


class Teacher(Base):

    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    teacher_name = Column(String)



class Course(Base):

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    course_name = Column(String)

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id")
    )



class Student(Base):

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    marks = Column(Integer)

    course_id = Column(
        Integer,
        ForeignKey("courses.id")
    )