# FastAPI-SQLModel-User

This is a basic implementation of an API that can be used as a template for new Entity Microservices. Through its API users can be added, modyfied and deleted.

It also includes a very basic HTML-form that presents a list of Users through [gridjs.io.](https://gridjs.io/)

The solution is based on:
  - FastAPI - Leading API framework
  - SQLModel - Models on top of SQLAlchemy ORM
  - SQLite - Database
  - Icecream - Improved debug prints. See https://github.com/gruns/icecream
  - Grid.js - Grid to present data
  - bcrypt - Encrypt passwords
  - Faker - Generate fake names for test data

# To install
pip install -r requirements.txt

Note: 

Pydantic V1 which is used in FastAPI and SQLModel can be installed with: pip install "pydantic==1.*" See https://docs.pydantic.dev/dev-v2/migration/

# To run
uvicorn main:app

# To use

http://127.0.0.1:8000/users/ - list users previously added through API calls


http://127.0.0.1:8000/docs - swagger documentation and for testing API calls


http://127.0.0.1:8000/app/user.html - to view Users 
