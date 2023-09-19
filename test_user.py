import pytest
from icecream import ic
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app
from database import User, get_db


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
        "/users/", json={"username": "Admin", "email": "email@email.com"}
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


def test_read_users(session: Session, client: TestClient):
    user_1 = User(username="deadpond", email="dive@email.com")
    user_2 = User(username="rustyman", email="rusty@email.com")
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
    user_1 = User(username="deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.get(f"/users/{user_1.id}")
    data = response.json()
    
    assert response.status_code == 200
    assert data["username"] == user_1.username
    assert data["email"] == user_1.email


def test_update_user(session: Session, client: TestClient):
    user_1 = User(username="Deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.patch(f"/users/{user_1.id}", json={"username": "deadpuddle"})
    missing_field = response.json()

    assert response.status_code == 422
    ic(missing_field)

    response = client.patch(
        f"/users/{user_1.id}", json={"username": "deadpuddle", "email": "aaaa@bee.com"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "deadpuddle"


def test_delete_user(session: Session, client: TestClient):
    user_1 = User(username="Deadpond", email="dive@email.com")
    session.add(user_1)
    session.commit()

    response = client.delete(f"/users/{user_1.id}")

    user_in_db = session.get(User, user_1.id)
    ic()
    ic(user_in_db)

    assert response.status_code == 200

    assert user_in_db is None
