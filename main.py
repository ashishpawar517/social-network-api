from fastapi import FastAPI, Depends, Response, status, HTTPException
import schemas
import models
from hashing import Hash
from typing import List

# from . import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from jwt_token import create_access_token
import oauth2
from fastapi.security import OAuth2PasswordRequestForm

# create all the tables
models.Base.metadata.create_all(engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/post/create", tags=["Posts"])
def create(
    request: schemas.Post,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    # print(get_current_user)
    email = get_current_user
    user = db.query(models.User).filter(models.User.email == email).first()
    new_post = models.Post(title=request.title, body=request.body, user_id=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/all", tags=["Posts"])
def getAll(
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/my", tags=["Posts"])
def getAll(
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    email = get_current_user
    user = db.query(models.User).filter(models.User.email == email).first()

    posts = db.query(models.Post).filter(models.Post.user_id == user.id).all()
    return posts


# @app.get("/blog/titles", response_model=List[schemas.Title], tags=["blogs"])
# def getAll_titles(
#     db: Session = Depends(get_db),
#     # get_current_user: schemas.User = Depends(oauth2.get_current_user),
# ):
#     blogs = db.query(models.Blog).all()
#     return blogs


@app.get("/post/{id}", tags=["Posts"], response_model=schemas.ShowPost)
def getOne(
    id,
    response: Response,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        # response.status_code =  status.HTTP_404_NOT_FOUND
        # return {'details':'id not found'}
        raise HTTPException(status_code=404, detail="id not found")
    return post


@app.delete("/post/{id}", tags=["Posts"])
def delete_blog(
    id,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    # db.query(models.Post).filter(models.Post.id == id).delete(synchronize_session=False)
    email = get_current_user
    user = db.query(models.User).filter(models.User.email == email).first()
    current = db.query(models.Post).filter(models.Post.id == id).filter(models.Post.user_id == user.id)
    if not current.first():
        return f"You do not own the post with provided ID {id}"
    
    current.delete(synchronize_session=False)
    db.commit()
    return "Post deleted with id " + id


@app.put("/post/{id}", tags=["Posts"])
def update_blog(
    id,
    request: schemas.Post,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    email = get_current_user
    user = db.query(models.User).filter(models.User.email == email).first()
    current = db.query(models.Post).filter(models.Post.id == id).filter(models.Post.user_id == user.id)
    
    if not current.first():
        return f"You do not own the post with provided ID {id}"
    
    current.update({"title": request.title, "body": request.body})
    db.commit()
    return "Post updated with id " + id


# users

@app.post("/user", response_model=schemas.UserSafe, tags=["Users"])
def create_user(request: schemas.User, db: Session = Depends(get_db)):

    hashed_password = Hash.encrypt(request.password)
    new_user = models.User(
        name=request.name, email=request.email, password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/user/{id}", response_model=schemas.UserSafe, tags=["Users"])
def get_user(
    id: int,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        return "not found"

    return user


@app.get("/current", response_model=schemas.UserSafe, tags=["Users"])
def get_current_user(
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):

    email = get_current_user
    user = db.query(models.User).filter(models.User.email == email).first()
    
    return user


# AUTHENTICATIONS
@app.post("/login", tags=["Users"])
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="invalid credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=404, detail="invalid passcode")

    access_token = create_access_token(data={"sub": user.email, "token_type": "bearer"})
    return {"access_token": access_token, "token_type": "bearer"}
