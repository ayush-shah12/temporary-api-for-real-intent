import os
import psycopg2
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
import uvicorn


DATABASE_URL = os.getenv("DATABASE_URL")



app = FastAPI()

class User(BaseModel):
    email: str

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) UNIQUE NOT NULL,
            api_key UUID UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_table()


@app.get("/")
def home():
    return {"message": "hi"}


@app.post("/register")
def register(user: User):
    """Register a new user with email and generate an api_key"""
    # Generate a unique API key
    api_key = str(uuid.uuid4())
    
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, api_key) VALUES (%s, %s);", (user.email, api_key))
        conn.commit()
        cursor.close()
        conn.close()
        return {"email": user.email, "api_key": api_key}
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@app.get("/getuser/{api_key}")
def get_user(api_key: str):
    """Fetch user details by api_key"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE api_key = %s;", (api_key,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return {"email": user[0]}
    else:
        raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
