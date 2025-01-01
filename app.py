import os
import psycopg2
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl 
import uvicorn


DATABASE_URL = os.environ['DATABASE_URL']

app = FastAPI()

class User(BaseModel):
    email: str
    api_key: uuid.UUID | None = None
    webhook_url: str | None = None

class SubscribeRequest(BaseModel):
    webhook_url: HttpUrl
    api_key: uuid.UUID

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) UNIQUE NOT NULL,
            api_key UUID UNIQUE NOT NULL,
            webhook_url VARCHAR(255)
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
def get_user(api_key: uuid.UUID):
    """Fetch user details by api_key"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, webhook_url FROM users WHERE api_key = %s;", (str(api_key),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return {"email": user[0], "webhook_url": user[1]}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/subscribe")
def subscribe(subscribe_request: SubscribeRequest):
    """Subscribe a user to a webhook URL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the user exists
    cursor.execute("SELECT email FROM users WHERE api_key = %s;", (str(subscribe_request.api_key),))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user with the webhook URL
    cursor.execute("UPDATE users SET webhook_url = %s WHERE api_key = %s;", (str(subscribe_request.webhook_url), str(subscribe_request.api_key)))
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": "User successfully subscribed to webhook", "webhook_url": str(subscribe_request.webhook_url)}

@app.post("/unsubscribe")
def unsubscribe(api_key: uuid.UUID):
    """Unsubscribe a user from a webhook URL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the user exists
    cursor.execute("SELECT email FROM users WHERE api_key = %s;", (str(api_key),))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user with the webhook URL
    cursor.execute("UPDATE users SET webhook_url = NULL WHERE api_key = %s;", (str(api_key),))
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": "User successfully unsubscribed from webhook"}


@app.get("/getleads/{api_key}")
def get_leads(api_key: uuid.UUID):
    """
    Fetch leads from the webhook URL
    
    Note:  Before publishing API, make sure that the sample data is as comprehensive as possible,
    so zapier can understand the data structure as best as possible.

    This endpoint is just a test, and will always be a test, in the sdk, the actual data is sent to the webhook_url,
    there is no polling, for real-intent.
    

    """
    # conn = get_db_connection()
    # cursor = conn.cursor()
    
    # Check if the user exists
    # cursor.execute("SELECT webhook_url FROM users WHERE api_key = %s;", (str(api_key),))
    # webhook_url = cursor.fetchone()
    
    # if not webhook_url:
    #     cursor.close()
    #     conn.close()
    #     raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch leads from the webhook URL
    # This is a dummy response for demonstration
    leads = [
        {"md5": "aaaaaaaaaa", "name": "John Doe", "email": "johndoe@gmail.com"},
        {"md5": "zzzzzzzzzz", "name": "Jane Doe", "email": "janedoe@gmail.com"},
    ]

    # cursor.close()
    # conn.close()

    return leads

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
