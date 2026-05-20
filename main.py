from fastapi import FastAPI
from database import engine, SessionLocal
from models import Base
from crud import *
from ai import ask_ai
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
async def home():

    return {
        "message": "AI Chatbot Running"
    }


@app.get("/chat/{question}")
async def chat(question: str):

    db = SessionLocal()

    # Ask AI
    ai_response = ask_ai(question)

    # Extract AI content
    content = ai_response["choices"][0]["message"]["content"]

    # Convert JSON string → Python dictionary
    action = json.loads(content)
    operation = action["data"]["operation"]
 
    # CREATE
    if operation == "CREATE":

        student = add_student(
            db,
            action["data"]["name"],
            action["data"]["marks"]
        )

        return "Student Added"
        


    # READ
    elif operation == "READ":

        students = get_students(db)

        return [
            {
                "id": s.id,
                "name": s.name,
                "marks": s.marks
            }
            for s in students
        ]


    # UPDATE
    elif operation == "UPDATE":

        update_student(
            db,
            action["data"]["name"],
            action["data"]["marks"]
        )

        return {
            "message": "Student Updated"
        }


    # DELETE
    elif operation == "DELETE":

        data = action.get("data", {})
        name = data.get("name") or action.get("name")
   
        delete_student(db, name)

        return {
            "message": "Student Deleted"
        }


    return {
        "message": "Unknown Operation"
    }