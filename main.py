from fastapi import FastAPI, HTTPException, Depends
from icecream import ic
from sqlmodel import Session
from fastapi.staticfiles import StaticFiles

from database import create_db_tables, get_db, User

app = FastAPI()

app.mount("/app", StaticFiles(directory="app"), name="app")


@app.on_event("startup")
def on_startup():
    create_db_tables(drop_all=False)


@app.post("/users/clear")
def clear_user(db: Session = Depends(get_db)):
    create_db_tables(drop_all=True)
    return {"cleared": True}


def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    return user


@app.post("/users/", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    ic.configureOutput(prefix='create_user START ')
    ic(user)
    if user.id is not None:
        db_user = db.get(User, user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User already exist")
        
    db.add(user)
    db.commit()
    db.refresh(user)
    ic.configureOutput(prefix='create_user RESULT: ')
    ic(user)
    return user


@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    users_data = db.query(User).all()
    data = {"users": users_data}
    return data


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    return user


@app.patch("/users/{user_id}", response_model=User)
def update_user(
    *, session: Session = Depends(get_db), user_id: int, user: User
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete("/users/{team_id}")
def remove_user(*, session: Session = Depends(get_db), team_id: int):
    team = session.get(User, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(team)
    session.commit()
    return {"deleted": True}
