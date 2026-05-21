from fastapi import FastAPI

from database import engine, SessionLocal

from models import Base

from crud import *

from ai import ask_ai

import json

import logging

from fastapi.middleware.cors import CORSMiddleware


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()


# ==========================================
# CORS
# ==========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# CREATE TABLES
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# HOME
# ==========================================

@app.get("/")
async def home():

    return {

        "message": "AI Database Chatbot Running"
    }


# ==========================================
# STUDENTS
# ==========================================

@app.get("/students")
async def read_students():

    db = SessionLocal()

    students = get_students(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks,
            "course_id": s.course_id
        }

        for s in students
    ]


# ==========================================
# TEACHERS
# ==========================================

@app.get("/teachers")
async def read_teachers():

    db = SessionLocal()

    teachers = get_teachers(db)

    return [

        {
            "id": t.id,
            "teacher_name": t.teacher_name
        }

        for t in teachers
    ]


# ==========================================
# COURSES
# ==========================================

@app.get("/courses")
async def read_courses():

    db = SessionLocal()

    courses = get_courses(db)

    return [

        {
            "id": c.id,
            "course_name": c.course_name,
            "teacher_id": c.teacher_id
        }

        for c in courses
    ]


# ==========================================
# ANALYTICS
# ==========================================

@app.get("/analytics/count-students")
async def count_students_api():

    db = SessionLocal()

    return [

        {
            "total_students": count_students(db)
        }
    ]


@app.get("/analytics/count-teachers")
async def count_teachers_api():

    db = SessionLocal()

    return [

        {
            "total_teachers": count_teachers(db)
        }
    ]


@app.get("/analytics/count-courses")
async def count_courses_api():

    db = SessionLocal()

    return [

        {
            "total_courses": count_courses(db)
        }
    ]


@app.get("/analytics/topper")
async def topper_api():

    db = SessionLocal()

    students = get_topper(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


@app.get("/analytics/lowest")
async def lowest_api():

    db = SessionLocal()

    students = get_lowest_student(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


@app.get("/analytics/average-marks")
async def average_marks_api():

    db = SessionLocal()

    return [

        {
            "average_marks": average_marks(db)
        }
    ]


@app.get("/analytics/max-marks")
async def max_marks_api():

    db = SessionLocal()

    return [

        {
            "maximum_marks": maximum_marks(db)
        }
    ]


@app.get("/analytics/min-marks")
async def min_marks_api():

    db = SessionLocal()

    return [

        {
            "minimum_marks": minimum_marks(db)
        }
    ]


# ==========================================
# JOINS
# ==========================================

@app.get("/joins/students-teachers")
async def students_teachers_join():

    db = SessionLocal()

    results = get_students_courses_teachers(db)

    return [

        {
            "id": r.id,
            "name": r.name,
            "marks": r.marks,
            "course_name": r.course_name,
            "teacher_name": r.teacher_name
        }

        for r in results
    ]


@app.get("/joins/students-courses")
async def students_courses_join():

    db = SessionLocal()

    results = get_students_with_courses(db)

    return [

        {
            "id": r.id,
            "name": r.name,
            "marks": r.marks,
            "course_name": r.course_name
        }

        for r in results
    ]


@app.get("/joins/courses-teachers")
async def courses_teachers_join():

    db = SessionLocal()

    results = get_courses_with_teachers(db)

    return [

        {
            "id": r.id,
            "course_name": r.course_name,
            "teacher_name": r.teacher_name
        }

        for r in results
    ]


# ==========================================
# FILTERS
# ==========================================

@app.get("/filters/students-above-marks")
async def students_above_marks(marks: int):

    db = SessionLocal()

    students = get_students_above_marks(db, marks)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


@app.get("/filters/students-below-marks")
async def students_below_marks(marks: int):

    db = SessionLocal()

    students = get_students_below_marks(db, marks)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


@app.get("/filters/search-student")
async def search_student(name: str):

    db = SessionLocal()

    students = search_student_by_name(db, name)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


# ==========================================
# SORTING
# ==========================================

@app.get("/sort/students-marks")
async def sort_students_marks():

    db = SessionLocal()

    students = get_students_sorted_by_marks(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


@app.get("/sort/students-highest")
async def sort_students_highest():

    db = SessionLocal()

    students = get_students_highest_first(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


@app.get("/sort/students-name")
async def sort_students_name():

    db = SessionLocal()

    students = get_students_alphabetically(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


# ==========================================
# PAGINATION
# ==========================================

@app.get("/pagination/first-five-students")
async def first_five_students():

    db = SessionLocal()

    students = get_first_five_students(db)

    return [

        {
            "id": s.id,
            "name": s.name,
            "marks": s.marks
        }

        for s in students
    ]


# ==========================================
# GROUP BY
# ==========================================

@app.get("/group/students-per-course")
async def students_group_course():

    db = SessionLocal()

    results = students_per_course(db)

    return [

        {
            "course_name": r.course_name,
            "total_students": r.total_students
        }

        for r in results
    ]


# ==========================================
# AI CHAT ROUTE
# ==========================================

@app.get("/chat/{question}")
async def chat(question: str):

    db = SessionLocal()

    try:

        ai_response = ask_ai(question)

        content = ai_response["choices"][0]["message"]["content"]

        print(content)

        content = content.replace("```json", "")

        content = content.replace("```", "")

        action = json.loads(content)

        print(action)

        api_calls = action.get("api_calls", [])

        final_results = {

            "results": []
        }


        for call in api_calls:

            endpoint = call.get("endpoint")

            params = call.get("params", {})


            # ==================================
            # STUDENTS
            # ==================================

            if endpoint == "/students":

                students = get_students(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Students",

                    "type": "table",

                    "count": len(students),

                    "data": [

                        {
                            "id": s.id,
                            "name": s.name,
                            "marks": s.marks,
                            "course_id": s.course_id
                        }

                        for s in students
                    ]
                })


            # ==================================
            # TEACHERS
            # ==================================

            elif endpoint == "/teachers":

                teachers = get_teachers(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Teachers",

                    "type": "table",

                    "count": len(teachers),

                    "data": [

                        {
                            "id": t.id,
                            "teacher_name": t.teacher_name
                        }

                        for t in teachers
                    ]
                })


            # ==================================
            # COURSES
            # ==================================

            elif endpoint == "/courses":

                courses = get_courses(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Courses",

                    "type": "table",

                    "count": len(courses),

                    "data": [

                        {
                            "id": c.id,
                            "course_name": c.course_name,
                            "teacher_id": c.teacher_id
                        }

                        for c in courses
                    ]
                })


            # ==================================
            # STUDENTS + TEACHERS JOIN
            # ==================================

            elif endpoint == "/joins/students-teachers":

                results = get_students_courses_teachers(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Students With Teachers",

                    "type": "table",

                    "count": len(results),

                    "data": [

                        {
                            "id": r.id,
                            "name": r.name,
                            "marks": r.marks,
                            "course_name": r.course_name,
                            "teacher_name": r.teacher_name
                        }

                        for r in results
                    ]
                })


            # ==================================
            # STUDENTS + COURSES JOIN
            # ==================================

            elif endpoint == "/joins/students-courses":

                results = get_students_with_courses(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Students With Courses",

                    "type": "table",

                    "count": len(results),

                    "data": [

                        {
                            "id": r.id,
                            "name": r.name,
                            "marks": r.marks,
                            "course_name": r.course_name
                        }

                        for r in results
                    ]
                })


            # ==================================
            # COURSES + TEACHERS JOIN
            # ==================================

            elif endpoint == "/joins/courses-teachers":

                results = get_courses_with_teachers(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Courses With Teachers",

                    "type": "table",

                    "count": len(results),

                    "data": [

                        {
                            "id": r.id,
                            "course_name": r.course_name,
                            "teacher_name": r.teacher_name
                        }

                        for r in results
                    ]
                })


            # ==================================
            # COUNT STUDENTS
            # ==================================

            elif endpoint == "/analytics/count-students":

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Student Count",

                    "type": "analytics",

                    "data": [

                        {
                            "total_students": count_students(db)
                        }
                    ]
                })


            # ==================================
            # COUNT TEACHERS
            # ==================================

            elif endpoint == "/analytics/count-teachers":

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Teacher Count",

                    "type": "analytics",

                    "data": [

                        {
                            "total_teachers": count_teachers(db)
                        }
                    ]
                })


            # ==================================
            # COUNT COURSES
            # ==================================

            elif endpoint == "/analytics/count-courses":

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Course Count",

                    "type": "analytics",

                    "data": [

                        {
                            "total_courses": count_courses(db)
                        }
                    ]
                })


            # ==================================
            # TOPPER
            # ==================================

            elif endpoint == "/analytics/topper":

                topper = get_topper(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Topper",

                    "type": "table",

                    "count": len(topper),

                    "data": [

                        {
                            "id": s.id,
                            "name": s.name,
                            "marks": s.marks
                        }

                        for s in topper
                    ]
                })


            # ==================================
            # LOWEST
            # ==================================

            elif endpoint == "/analytics/lowest":

                students = get_lowest_student(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Lowest Marks Students",

                    "type": "table",

                    "count": len(students),

                    "data": [

                        {
                            "id": s.id,
                            "name": s.name,
                            "marks": s.marks
                        }

                        for s in students
                    ]
                })


            # ==================================
            # FILTER ABOVE MARKS
            # ==================================

            elif endpoint == "/filters/students-above-marks":

                marks = params.get("marks")

                students = get_students_above_marks(db, marks)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": f"Students Above {marks}",

                    "type": "table",

                    "count": len(students),

                    "data": [

                        {
                            "id": s.id,
                            "name": s.name,
                            "marks": s.marks
                        }

                        for s in students
                    ]
                })


            # ==================================
            # FILTER BELOW MARKS
            # ==================================

            elif endpoint == "/filters/students-below-marks":

                marks = params.get("marks")

                students = get_students_below_marks(db, marks)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": f"Students Below {marks}",

                    "type": "table",

                    "count": len(students),

                    "data": [

                        {
                            "id": s.id,
                            "name": s.name,
                            "marks": s.marks
                        }

                        for s in students
                    ]
                })


            # ==================================
            # SEARCH STUDENT
            # ==================================

            elif endpoint == "/filters/search-student":

                name = params.get("name")

                students = search_student_by_name(db, name)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": f"Search Results for {name}",

                    "type": "table",

                    "count": len(students),

                    "data": [

                        {
                            "id": s.id,
                            "name": s.name,
                            "marks": s.marks
                        }

                        for s in students
                    ]
                })


            # ==================================
            # GROUP BY
            # ==================================

            elif endpoint == "/group/students-per-course":

                results = students_per_course(db)

                final_results["results"].append({

                    "endpoint": endpoint,

                    "title": "Students Per Course",

                    "type": "table",

                    "count": len(results),

                    "data": [

                        {
                            "course_name": r.course_name,
                            "total_students": r.total_students
                        }

                        for r in results
                    ]
                })


        return final_results


    except Exception as e:

        print("ERROR:", e)

        return {

            "error": str(e)
        }