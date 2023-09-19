from fastapi import FastAPI, HTTPException, Depends
from icecream import ic
from sqlmodel import Session
from fastapi.staticfiles import StaticFiles
from encrypt import hash_password, check_password

from database import create_db_tables, get_db, UserBase, User

app = FastAPI()

app.mount("/app", StaticFiles(directory="app"), name="app")


@app.on_event("startup")
def on_startup():
    create_db_tables(drop_all=False)


@app.post("/users/clear")
def clear_user(db: Session = Depends(get_db)):
    create_db_tables(drop_all=True)
    return {"cleared": True}


def get_user(user_id: int, db: Session = Depends(get_db)) -> UserBase:
    user = db.get(UserBase, user_id)
    return user


@app.post("/users/", response_model=UserBase)
def create_user(user: UserBase, db: Session = Depends(get_db)):
    """Create user without password"""
    ic.configureOutput(prefix="create_user START ")
    ic(user)
    if user.id is not None:
        db_user = db.get(UserBase, user.id)
        if db_user:
            raise HTTPException(status_code=404, detail="User already exist")

    db.add(user)
    db.commit()
    db.refresh(user)
    ic.configureOutput(prefix="create_user RESULT: ")
    ic(user)
    return user


@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    users_data = db.query(UserBase).all()
    data = {"users": users_data}
    return data


@app.get("/users/{user_id}", response_model=UserBase)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    return user


@app.patch("/users/{user_id}", response_model=UserBase)
def update_user(*, session: Session = Depends(get_db), user_id: int, user: UserBase):
    db_user = session.get(UserBase, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def remove_user(*, session: Session = Depends(get_db), user_id: int):
    user = session.get(UserBase, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"deleted": True}


@app.post("/user/set_password", response_model=User)
def set_password(user: User, db: Session = Depends(get_db)):
    """Set existing user password. Will be encrypted before it is stored in the database"""
    if user.password is None:
        raise HTTPException(status_code=404, detail="User.password is missing")

    if user.id is None:
        raise HTTPException(status_code=404, detail="User Id is missing")
    else:
        db_user = db.get(User, user.id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User {user.id=} doesn't exist"
            )
        ic(user)
        db_user.password = hash_password(user.password)
        ic(db_user)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    ic(db_user)
    return db_user


@app.post("/user/login", response_model=User)
def login(user: User, db: Session = Depends(get_db)):
    """Check password with the encrypted password stored in the database"""
    if user.password is None:
        raise HTTPException(status_code=404, detail="User password is missing")

    if user.id is None:
        raise HTTPException(status_code=404, detail="User Id is missing")
    else:
        db_user = db.get(User, user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail=f"User {user.id=} doesn't exist")

        if check_password(user.password, db_user.password):
            return db_user  # Login successful

    return None  # Login failed
