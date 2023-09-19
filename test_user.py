import pytest
from icecream import ic
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app
from encrypt import hash_password, check_password
from model import UserBase, User
from database import get_db


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "username": "Admin",
            "email": "email@email.com",
            "fullname": "Adam Adamsson",
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "Admin"
    assert data["email"] == "email@email.com"


def test_create_user_incomplete(client: TestClient):
    # No secret_name
    response = client.post("/users/", json={"name": "Deadpond"})
    assert response.status_code == 422


def test_create_user_invalid(client: TestClient):
    # secret_name has an invalid type
    response = client.post(
        "/users/",
        json={
            "username": "deadpond",
            "email": {"message": "Not okey!"},
        },
    )
    assert response.status_code == 422


def test_list_users(session: Session, client: TestClient):
    user_1 = UserBase(username="deadpond", email="dive@email.com")
    user_2 = UserBase(username="rustyman", email="rusty@email.com")
    session.add(user_1)
    session.add(user_2)
    session.commit()

    response = client.get("/users/")
    data = response.json()["users"]

    assert response.status_code == 200

    ic(data)

    assert len(data) == 2
    assert data[0]["username"] == user_1.username


def test_read_user(session: Session, client: TestClient):
    user_1 = UserBase(username="deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.get(f"/users/{user_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == user_1.username
    assert data["email"] == user_1.email


def test_update_user(session: Session, client: TestClient):
    user_1 = UserBase(username="Deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.patch(
        f"/users/{user_1.id}", json={"username": "deadpuddle", "email": "aaaa@bee.com"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "deadpuddle"


def test_update_user_missing_field(session: Session, client: TestClient):
    user_1 = UserBase(username="Deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.patch(f"/users/{user_1.id}", json={"username": "deadpuddle"})
    missing_field = response.json()

    assert response.status_code == 422
    ic(missing_field)


def test_delete_user(session: Session, client: TestClient):
    user_1 = UserBase(username="Deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.delete(f"/users/{user_1.id}")

    user_in_db = session.get(UserBase, user_1.id)
    ic()
    ic(user_in_db)

    assert response.status_code == 200

    assert user_in_db is None


def test_encrypt_password():
    hash = hash_password("User pw")
    assert check_password("User pw", hashed_password=hash)

    assert not check_password("other pw", hashed_password=hash)


def test_user_with_password(session: Session, client: TestClient):
    secret_pw = "aPassowrd"

    user_1 = User(username="Deadpond", email="dive@email.com", password=secret_pw)
    session.add(user_1)
    session.commit()
    session.refresh(user_1)

    user_2 = session.get(User, user_1.id)
    assert user_1.username == user_2.username
    assert user_1.password == secret_pw

    user_2.password = hash_password(user_1.password)

    assert check_password(secret_pw, user_2.password) is True


def test_set_password_and_login(session: Session, client: TestClient):
    secret_pw = "aPassowrd"

    user = User(username="Deadpond", email="dive@email.com")
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/user/set_password",
        json={
            "id": user.id,
            "username": "Deadpond",
            "email": "aaaa@bee.com",
            "password": secret_pw,
        },
    )
    json_response = response.json()

    assert response.status_code == 200
    assert len(json_response["password"]) > 20
    
    # Verify login for the same user
    
    response = client.post(
        "/user/login",
        json={
            "id": user.id,
            "username": "Deadpond",
            "email": "aaaa@bee.com",
            "password": secret_pw,
        },
    )
    json_response = response.json()

    assert response.status_code == 200
    assert len(json_response["password"]) > 20
