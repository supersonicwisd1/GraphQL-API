from fastapi import FastAPI
import requests
from models.user import User, FBAccount
from database import db, mongo
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr, BaseModel
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED
from database import db_session
from models.user import User, FBAccount
from passlib.context import CryptContext
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.graphql import GraphQLApp
from schema.schema import schema
import jwt
from pymongo import MongoClient
import os
from pymongo import MongoClient

app = FastAPI()


mongo_client = MongoClient("mongodb://<host>:<port>/")
db = mongo_client["<database_name>"]

mongo_client = MongoClient(os.getenv("MONGO_URL"))
db = mongo_client[os.getenv("MONGO_DB")]

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
access_token_expires = 3600


app.add_route("/graphql", GraphQLApp(schema=schema))


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: dict):
    return {"item": item}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.post("/users/register", response_model=User)
def register_user(user: User, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def authenticate_user(db, email: EmailStr, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


# Use a secret key for creating the access token
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
access_token_expires = 3600

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=access_token_expires)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=400, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}
        )

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
