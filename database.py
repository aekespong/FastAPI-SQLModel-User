from sqlmodel import SQLModel, create_engine, Session
from model import UserBase, User
from icecream import ic
from faker import Faker

DATABASE_URL = "sqlite:///./User.db"
engine = create_engine(DATABASE_URL, echo=True)


# Define a function to get a database session
def get_db():
    with Session(engine) as session:
        yield session


def create_db_tables(drop_all=False):
    if drop_all:
        SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def add_user(username: str, email: str) -> UserBase:
    user = User(username=username, email=email, password=None)
    with Session(engine) as db:
        db.add(user)
        db.commit()
    return user


if __name__ == "__main__":
    create_db_tables(drop_all=True)
    add_user("admin", "admin@gmail.com")
    add_user("root", "root@gmail.com")

    faker = Faker("sv_SE")
    for i in range(40):
        add_user(faker.name(), faker.email())

    with Session(engine) as db:
        list = db.query(User).all()
        for user in list:
            ic(user)
