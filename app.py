import os
import psycopg2
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl 
import uvicorn
import json

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


@app.get("/me")
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


@app.delete("/unsubscribe")
def unsubscribe(unsubscribe_request: SubscribeRequest):
    """Unsubscribe a user from a webhook URL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the user exists
    cursor.execute("SELECT email FROM users WHERE api_key = %s;", (str(unsubscribe_request.api_key),))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user with the webhook URL
    cursor.execute(
        "UPDATE users SET webhook_url = NULL WHERE api_key = %s AND webhook_url = %s;", 
        (str(unsubscribe_request.api_key), str(unsubscribe_request.webhook_url))
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": "User successfully unsubscribed from webhook"}


@app.get("/sample")
def get_sample_data():
    """
    Get sample data  
    Note: Before publishing API, make sure that the FIRST element of the sample data is as comprehensive as possible,
    so zapier can understand the data structure as best as possible. (zapier only reads the first element of the response for testing)

    Not sure if sentences should be seperated as I have done them for now...

    converted to json here manually, but actual data is json serialized as it gets sent to the webhook
    
    """
    return [
    {
        "md5": "123",
        "pii": {
            "first_name": "Linda",
            "last_name": "Williams",
            "address": "3771 Oak St",
            "city": "Clinton",
            "state": "MI",
            "zip_code": "32717",
            "zip4": "8238",
            "fips_state_code": "27",
            "fips_county_code": "332",
            "county_name": "West County",
            "latitude": "48.727740387547",
            "longitude": "-105.67535678949835",
            "address_type": "H",
            "cbsa": "50042",
            "census_tract": "271794",
            "census_block_group": "2",
            "census_block": "8609",
            "gender": "Female",
            "scf": "161",
            "dma": "256",
            "msa": "353",
            "congressional_district": "227",
            "head_of_household": "Yes",
            "birth_month_and_year": "05/1971",
            "age": "53",
            "prop_type": "Multi Family",
            "n_household_children": "1",
            "credit_range": "Poor",
            "household_income": "25000-50000",
            "household_net_worth": "1000000+",
            "home_owner_status": "No",
            "marital_status": "Single",
            "occupation": "Designer",
            "median_home_value": "839621",
            "education": "Masters",
            "length_of_residence": "17",
            "n_household_adults": "4",
            "political_party": "None",
            "health_beauty_products": "0",
            "cosmetics": "1",
            "jewelry": "0",
            "investment_type": "False",
            "investments": "0",
            "pet_owner": "0",
            "pets_affinity": "1",
            "health_affinity": "3",
            "diet_affinity": "2",
            "fitness_affinity": "5",
            "outdoors_affinity": "5",
            "boating_sailing_affinity": "0",
            "camping_hiking_climbing_affinity": "1",
            "fishing_affinity": "0",
            "hunting_affinity": "4",
            "aerobics": "4",
            "nascar": "0",
            "scuba": "3",
            "weight_lifting": "2",
            "healthy_living_interest": "2",
            "motor_racing": "5",
            "foreign_travel": "1",
            "self_improvement": "3",
            "walking": "2",
            "fitness": "4",
            "ethnicity_detail": "Caucasian",
            "ethnic_group": "Asian",
            "email_1": "fu114@example.com",
            "email_2": "asdhj@example.com",
            "email_3": "yess@example.com",
            "phone_1": "6398861128",
            "phone_1_dnc": "False",
            "phone_2": "4357177368",
            "phone_2_dnc": "True",
            "phone_3": "4554198036",
            "phone_3_dnc": "False"
        },
        "insight": "Insight for first md5 123",
        "sentence_1": "another test sentence for first md5 123",
        "sentence_2": "fourth test sentence for first md5 123",
        "sentence_3": "third test sentence for first md5 123",
        "sentence_4": "test sentence for first md5 123",
    },
    {
        "md5": "456",
        "pii": {
            "first_name": "John",
            "last_name": "Rodriguez",
            "address": "8743 Cedar St",
            "city": "Springfield",
            "state": "CA",
            "zip_code": "58633",
            "zip4": "8015",
            "fips_state_code": "05",
            "fips_county_code": "149",
            "county_name": "South County",
            "latitude": "34.841154350310966",
            "longitude": "-100.72690362515483",
            "address_type": "H",
            "cbsa": "15548",
            "census_tract": "558076",
            "census_block_group": "7",
            "census_block": "8239",
            "gender": "Male",
            "scf": "436",
            "dma": "653",
            "msa": "609",
            "congressional_district": "356",
            "head_of_household": "Yes",
            "birth_month_and_year": "03/1992",
            "age": "32",
            "prop_type": "Condo",
            "n_household_children": "0",
            "credit_range": "Fair",
            "household_income": "150000+",
            "household_net_worth": "0-100000",
            "home_owner_status": "Yes",
            "marital_status": "Single",
            "occupation": "Designer",
            "median_home_value": "268924",
            "education": "Doctorate",
            "length_of_residence": "24",
            "n_household_adults": "3",
            "political_party": "None",
            "health_beauty_products": "1",
            "cosmetics": "0",
            "jewelry": "0",
            "investment_type": "True",
            "investments": "0",
            "pet_owner": "1",
            "pets_affinity": "1",
            "health_affinity": "0",
            "diet_affinity": "1",
            "fitness_affinity": "1",
            "outdoors_affinity": "5",
            "boating_sailing_affinity": "5",
            "camping_hiking_climbing_affinity": "4",
            "fishing_affinity": "5",
            "hunting_affinity": "0",
            "aerobics": "0",
            "nascar": "4",
            "scuba": "3",
            "weight_lifting": "4",
            "healthy_living_interest": "3",
            "motor_racing": "1",
            "foreign_travel": "2",
            "self_improvement": "1",
            "walking": "4",
            "fitness": "3",
            "ethnicity_detail": "Hispanic",
            "ethnic_group": "Hispanic",
            "email_1": "jp963@example.com",
            "email_2": None,
            "email_3": None,
            "phone_1": "3219118776",
            "phone_1_dnc": "False",
            "phone_2": "4954258937",
            "phone_2_dnc": "False",
            "phone_3": "3721272528",
            "phone_3_dnc": "True"
        },
        "insight": "Insight for second md5 456",
        "sentence_1": "sentence for second md5 456",
        "sentence_2": "another sentence for second md5 456",
    },
    {
        "md5": "789",
        "pii": {
            "first_name": "Robert",
            "last_name": "Smith",
            "address": "5111 Park St",
            "city": "Greenville",
            "state": "TX",
            "zip_code": "87137",
            "zip4": "3038",
            "fips_state_code": "37",
            "fips_county_code": "704",
            "county_name": "South County",
            "latitude": "43.59928911528708",
            "longitude": "-76.01964873311118",
            "address_type": "",
            "cbsa": "91917",
            "census_tract": "430829",
            "census_block_group": "3",
            "census_block": "9991",
            "gender": "Female",
            "scf": "626",
            "dma": "580",
            "msa": "637",
            "congressional_district": "54",
            "head_of_household": "Yes",
            "birth_month_and_year": "03/1973",
            "age": "51",
            "prop_type": "Condo",
            "n_household_children": "3",
            "credit_range": "Good",
            "household_income": "25000-50000",
            "household_net_worth": "100000-250000",
            "home_owner_status": "No",
            "marital_status": "Single",
            "occupation": "Teacher",
            "median_home_value": "523049",
            "education": "Doctorate",
            "length_of_residence": "3",
            "n_household_adults": "5",
            "political_party": "Democrat",
            "health_beauty_products": "0",
            "cosmetics": "0",
            "jewelry": "0",
            "investment_type": "True",
            "investments": "0",
            "pet_owner": "1",
            "pets_affinity": "4",
            "health_affinity": "3",
            "diet_affinity": "3",
            "fitness_affinity": "3",
            "outdoors_affinity": "4",
            "boating_sailing_affinity": "4",
            "camping_hiking_climbing_affinity": "5",
            "fishing_affinity": "3",
            "hunting_affinity": "3",
            "aerobics": "0",
            "nascar": "3",
            "scuba": "2",
            "weight_lifting": "1",
            "healthy_living_interest": "0",
            "motor_racing": "3",
            "foreign_travel": "3",
            "self_improvement": "5",
            "walking": "3",
            "fitness": "0",
            "ethnicity_detail": "Asian",
            "ethnic_group": "African American",
            "email_1": "ag992@example.com",
            "email_2": None,
            "email_3": None,
            "phone_1": "4127518758",
            "phone_1_dnc": "False",
            "phone_2": "6904582051",
            "phone_2_dnc": "True",
            "phone_3": "2271944833",
            "phone_3_dnc": "True"
        },
        "insight": "Insight for third md5 789",
        "sentence_1": "sentence for third md5 789",
    }
]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
