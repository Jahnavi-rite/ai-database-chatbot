from fastapi import FastAPI
from database import engine, SessionLocal
from models import Base
from crud import *
from ai import ask_ai

import json
import logging

from fastapi.middleware.cors import CORSMiddleware


# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# =========================
# FASTAPI APP
# =========================

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================
# CREATE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# HOME ROUTE
# =========================

@app.get("/")
async def home():

    return {
        "message": "AI Chatbot Running"
    }


# =========================
# CHAT ROUTE
# =========================

@app.get("/chat/{question}")
async def chat(question: str):

    db = SessionLocal()

    # =========================
    # ASK AI
    # =========================

    ai_response = ask_ai(question)

    # Extract AI response content
    content = ai_response["choices"][0]["message"]["content"]

    logger.info(content)

    # Convert JSON string → Python dictionary
    action = json.loads(content)

    print(action)

    # =========================
    # EXTRACT DATA
    # =========================

    intent = action.get("intent")

    filters = action.get("filters", {})

    data = action.get("data", {})

    query_type = action.get("query_type")


    # =========================
    # CREATE
    # =========================

    if intent == "CREATE":

        add_student(

            db,

            data.get("name"),

            data.get("marks")
        )

        students = get_students(db)

        return [

            {
                "id": s.id,
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]


    # =========================
    # READ
    # =========================

    elif intent == "READ":

        students = get_students(db)

        return [

            {
                "id": s.id,
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]


    # =========================
    # UPDATE
    # =========================

    elif intent == "UPDATE":

        update_student(

            db,

            filters.get("name"),

            data.get("marks")
        )

        students = get_students(db)

        return [

            {
                "id": s.id,
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]


    # =========================
    # DELETE
    # =========================

    elif intent == "DELETE":

        print("DELETE BLOCK RUNNING")

        print("FILTERS:", filters)

        student_id = filters.get("id")

        name = filters.get("name")

        print("ID:", student_id)

        print("NAME:", name)


        # DELETE USING ID
        if student_id:

            delete_student_by_id(
                db,
                student_id
            )


        # DELETE USING NAME
        elif name:

            delete_student(
                db,
                name
            )


        students = get_students(db)

        return [

            {
                "id": s.id,
                "name": s.name,
                "marks": s.marks
            }

            for s in students
        ]


    # =========================
    # ANALYTICS
    # =========================

    elif intent == "ANALYTICS":


        # =========================
        # TOPPER
        # =========================

        if query_type == "TOPPER":

            topper = get_topper(db)

            return {
                "topper": {
                    "id": topper.id,
                    "name": topper.name,
                    "marks": topper.marks
                }
            }


        # =========================
        # COUNT
        # =========================

        elif query_type == "COUNT":

            total = count_students(db)

            return {
                "total_students": total
            }


        # =========================
        # ABOVE MARKS
        # =========================

        elif query_type == "ABOVE_MARKS":

            marks = filters.get("marks_above")

            students = get_students_above_marks(
                db,
                marks
            )

            return [

                {
                    "id": s.id,
                    "name": s.name,
                    "marks": s.marks
                }

                for s in students
            ]


        return {
            "message": "Unknown Analytics Query"
        }


    # =========================
    # UNKNOWN
    # =========================

    return {
        "message": "Could not understand query"
    }