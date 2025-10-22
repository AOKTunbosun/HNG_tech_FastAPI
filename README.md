# HNG-project Stage 1
This is a task given to develop 5 API endpoints which process a string which returns a json response with fields such as: is_palindorme, word_count etc.

### Tech Stack
These are the main technologies used:
- Python
- FastAPI

## Getting Started
### Prerequisites
- Python version 3.10+

### Installation
**git clone https://github.com/AOKTunbosun/HNG_tech_FastAPI**

### Installing dependencies
Run the following commands:
- **pip install pipenv**
- **pipenv install**

### Running locally
**Navigate to the database.py and comment out the SQLALCHEMY_DATABASE_URL with data/prod.sqlite**
**Uncomment the SQLALCHEMY_DATABASE_URL with ./blog.db**
In terminal run:
**uvicorn main:app --reload --port 8000**

### Environment variables needed
*No Environment Variables Needed*
