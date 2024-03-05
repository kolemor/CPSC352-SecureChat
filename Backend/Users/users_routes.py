import contextlib
import sqlite3
import typing
import collections
import os
import httpx
import datetime
import logging.config

from fastapi import Depends, HTTPException, APIRouter, status, Query
from pydantic_settings import BaseSettings
from Backend.Users.users_schema import *
from Backend.Users.users_hash import hash_password, verify_password

DEBUG = False

router = APIRouter()

database = "Backend/users.db"

# The next two functions handles JWT claim
def expiration_in(minutes):
    creation = datetime.datetime.now(tz=datetime.timezone.utc)
    expiration = creation + datetime.timedelta(minutes=minutes)
    return creation, expiration


def generate_claims(username, user_id, status):
    _, exp = expiration_in(20)

    claims = {
        "aud": "krakend.local.gd",
        "iss": "auth.local.gd",
        "sub": username,
        "jti": str(user_id),
        "status": status,
        "exp": int(exp.timestamp()),
    }
    token = {
        "access_token": claims,
        "refresh_token": claims,
        "exp": int(exp.timestamp()),
    }

    return token

# Connect to the database
def get_db():
    with contextlib.closing(sqlite3.connect(database, check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db

#==========================================Users==================================================

# The login endpoint, where JWT validation needs to occur
@router.post("/users/login", tags=['Users'])
def get_user_login(user: User, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM user WHERE name = ?
        """, (user.name,)
    )
    user_data = cursor.fetchone()
    
    # Check if user exists
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username")

    # Verify the password
    if not verify_password(user.password, user_data['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    
    cursor.execute(
        """
        INSERT INTO user_status (user_id, status_id)
        VALUES (?, (SELECT sid FROM status WHERE status = 'online'))
        """, (user_data['uid'],)
    )

    #Issue JWT token
    token_data = generate_claims(user_data['name'], user_data['uid'], "Online")
    return token_data


# Create new user endpoint
@router.post("/users/register", tags=['Users'])
async def register_new_user(user: User, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT * FROM user WHERE name = ?
        """, (user.name,)
    )
    user_data = cursor.fetchone()
    
    # Check if user exists
    if user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # Hash the password before storing it
    password_hash = hash_password(user.password)

    #Store new user data in DB
    cursor.execute(
        """
        INSERT INTO users (name, password, status)
        VALUES (?, ?, ?)
        """, (user.name, password_hash, "Offline")
    )

    db.commit()

    return {"message": "User created successfully"}



# Have a user check their password
@router.get("/users/check_password", tags=['Users'])
def get_user_password(username: str = Query(..., title="Username", description="Your username"),
    password: str = Query(..., title="Password", description="Your password"),
    db: sqlite3.Connection = Depends(get_db)):

    # Query the database to retrieve the user's password hash
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT password FROM user WHERE name = ?
        """, (username,)
    )
    q = cursor.fetchone()

    # Check if user exists
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check the password
    password_hash = q[0]

    if verify_password(password, password_hash):
        return {"message": "Password is correct"}
    else:
        return {"message": "Password is incorrect"}