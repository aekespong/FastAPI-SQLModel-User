# FastAPI-SQLModel-User

User is a basic implementation of an API.

It also includes a very basic HTML-form that presents a list of Users.

The solution is based on:
  - FastAPI
  - SQLModel
  - Icecream
  - Grid.js

Icecream is used instead of print(). See https://github.com/gruns/icecream

# To install
pip install -r requirements.txt

Note: Pydantic V1 which is used in FastAPI and SQLModel can be installed with: pip install "pydantic==1.*" See https://docs.pydantic.dev/dev-v2/migration/

# To run
uvicorn main:app
