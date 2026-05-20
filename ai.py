import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env
API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_ai(question):

    response = requests.post(

        "https://openrouter.ai/api/v1/chat/completions",

        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },

        json={

            "model": "openai/gpt-3.5-turbo",

            "messages": [

                {
                    "role": "system",

                    "content": """
                    You are a database assistant.

                    Detect database operations:

                    CREATE
                    READ
                    UPDATE
                    DELETE

                    Return only JSON.
                    output json format : 
                    {data:
                    {'operation': 'CREATE',
                     'name': 'xyz',
                      'marks': 99
                       "filters": {
                      "id": 25
                     }, }
                    }  
                    User:
                      Delete Ashu

                     Output:
                     {
                        "intent": "DELETE",
                        "filters": {
                        "name": "Ashu"
                     },
                     "data": {},
                     "query_type": ""
                     }


                    User:
                     Delete student Ashu

                     Output:
                    {
                       "intent": "DELETE",
                        "filters": {
                        "name": "Ashu"
                    },
                    "data": {},
                    "query_type": ""
                      }


                      User:
                      Delete student Ashu with marks 99

                      Output:
                       {
                         "intent": "DELETE",
                          "filters": {
                            "name": "Ashu",
                             "marks": 99
                        },
                        "data": {},
                        "query_type": ""
                        }


                       User:
                       Delete id 5

                        Output:
                        {
                         "intent": "DELETE",
                         "filters": {
                         "id": 5
                        },
                        "data": {},
                        "query_type": ""
                    }
                    """
                },

                {
                    "role": "user",
                    "content": question
                }

            ]
        }
    )

    return response.json()