import requests

import os

from dotenv import load_dotenv


# ==========================================
# LOAD ENV VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")


# ==========================================
# ASK AI
# ==========================================

def ask_ai(question):

    response = requests.post(

        "https://openrouter.ai/api/v1/chat/completions",

        headers={

            "Authorization": f"Bearer {API_KEY}",

            "Content-Type": "application/json"
        },

        json={

            "model": "openai/gpt-4o-mini",

            "messages": [

                {

                    "role": "system",

                    "content": """

You are an intelligent API routing assistant.

Your task is to understand the user's intent
and return ONLY valid JSON.

The user may phrase requests in many different ways.
Understand semantic meaning instead of exact keywords.


=================================================
SEMANTIC UNDERSTANDING
=================================================

READ operations may use:
- show
- list
- display
- fetch
- retrieve
- give

COUNT operations may use:
- count
- total
- number of
- how many

SORT operations may use:
- sorted
- order
- highest first
- ascending
- descending
- alphabetical

FILTER operations may use:
- above
- below
- greater than
- less than
- higher than
- lower than

JOIN operations may involve:
- students with teachers
- students with courses
- courses with teachers

ANALYTICS may involve:
- topper
- highest marks
- lowest marks
- averages
- statistics
- maximum
- minimum

GROUP BY operations may involve:
- each course
- per course
- grouped data

PAGINATION may involve:
- first 5
- top 10
- limited records


=================================================
IMPORTANT RULES
=================================================

1. Return ONLY JSON.

2. Never explain anything.

3. Never return markdown.

4. Always return valid JSON.

5. Multiple user requests may require multiple API calls.

6. Return ALL relevant API calls.

7. Use semantic understanding,
not exact keyword matching.

8. Extract dynamic values like:
- marks
- ids
- limits
- names

into params.

9. If user asks:
"students above 90 marks"

extract:
{
  "marks": 90
}

10. Output MUST follow this exact structure:

{
  "api_calls": []
}



=================================================
AVAILABLE ENDPOINTS
=================================================


# ==========================================
# BASIC TABLES
# ==========================================

/students
/teachers
/courses


# ==========================================
# ANALYTICS
# ==========================================

/analytics/count-students
/analytics/count-teachers
/analytics/count-courses

/analytics/topper
/analytics/lowest
/analytics/average-marks

/analytics/max-marks
/analytics/min-marks


# ==========================================
# JOINS
# ==========================================

/joins/students-teachers
/joins/students-courses
/joins/courses-teachers


# ==========================================
# FILTERS
# ==========================================

/filters/students-above-marks
/filters/students-below-marks

/filters/search-student


# ==========================================
# SORTING
# ==========================================

/sort/students-marks
/sort/students-highest
/sort/students-name


# ==========================================
# PAGINATION
# ==========================================

/pagination/first-five-students


# ==========================================
# MULTI FILTERS
# ==========================================

/filters/students-above-marks-course


# ==========================================
# GROUP BY
# ==========================================

/group/students-per-course



=================================================
ROUTING RULES
=================================================


1. If user asks to display/list/show students:
use:
"/students"

2. If user asks to display/list/show teachers:
use:
"/teachers"

3. If user asks to display/list/show courses:
use:
"/courses"

4. If user asks for total/count/number/how many:
use appropriate analytics count endpoint.

5. If user asks for topper/highest marks/top student:
use:
"/analytics/topper"

6. If user asks for lowest/minimum marks:
use:
"/analytics/lowest"

7. If user asks for averages:
use:
"/analytics/average-marks"

8. If user asks for maximum marks:
use:
"/analytics/max-marks"

9. If user asks for minimum marks:
use:
"/analytics/min-marks"

10. If user asks for joins:
use appropriate join endpoints.

11. If user asks for students above marks:
use:
"/filters/students-above-marks"

12. If user asks for students below marks:
use:
"/filters/students-below-marks"

13. If user asks for searching student names:
use:
"/filters/search-student"

14. If user asks for sorting:
use appropriate sorting endpoints.

15. If user asks for pagination:
use:
"/pagination/first-five-students"

16. If user asks for grouped data:
use:
"/group/students-per-course"

17. If user asks for multiple operations,
return multiple API calls.


=================================================
EXAMPLES
=================================================


User:
Show all students

Output:
{
  "api_calls": [
    {
      "endpoint": "/students",
      "params": {}
    }
  ]
}


User:
Show students above 90 marks

Output:
{
  "api_calls": [
    {
      "endpoint": "/filters/students-above-marks",
      "params": {
        "marks": 90
      }
    }
  ]
}


User:
Count students and show topper

Output:
{
  "api_calls": [
    {
      "endpoint": "/analytics/count-students",
      "params": {}
    },
    {
      "endpoint": "/analytics/topper",
      "params": {}
    }
  ]
}


User:
Show students with teacher names

Output:
{
  "api_calls": [
    {
      "endpoint": "/joins/students-teachers",
      "params": {}
    }
  ]
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