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
    data = [
            {
                'md5': '123',
                'pii': {'first_name': 'Mary', 'last_name': 'Garcia', 'address': '7832 Hill St', 'city': 'Greenville', 'state': 'OH', 'zip_code': '75995', 'zip4': '7647', 'fips_state_code': '21', 'fips_county_code': '737', 'county_name': 'West County', 'latitude': '49.08158285482676', 'longitude': '-113.60484624187765', 'address_type': '', 'cbsa': '92699', 'census_tract': '142537', 'census_block_group': '5', 'census_block': '1672', 'gender': 'Male', 'scf': '625', 'dma': '822', 'msa': '114', 'congressional_district': '293', 'head_of_household': 'No', 'birth_month_and_year': '11/1998', 'age': '26', 'prop_type': 'Multi Family', 'n_household_children': '0', 'credit_range': 'Very Good', 'household_income': '25000-50000', 'household_net_worth': '0-100000', 'home_owner_status': 'No', 'marital_status': 'Married', 'occupation': 'Lawyer', 'median_home_value': '901764', 'education': 'Some College', 'length_of_residence': '14', 'n_household_adults': '2', 'political_party': 'Independent', 'health_beauty_products': '1', 'cosmetics': '0', 'jewelry': '0', 'investment_type': 'False', 'investments': '1', 'pet_owner': '1', 'pets_affinity': '2', 'health_affinity': '4', 'diet_affinity': '1', 'fitness_affinity': '1', 'outdoors_affinity': '3', 'boating_sailing_affinity': '1', 'camping_hiking_climbing_affinity': '1', 'fishing_affinity': '1', 'hunting_affinity': '2', 'aerobics': '4', 'nascar': '1', 'scuba': '3', 'weight_lifting': '1', 'healthy_living_interest': '2', 'motor_racing': '5', 'foreign_travel': '1', 'self_improvement': '5', 'walking': '5', 'fitness': '3', 'ethnicity_detail': 'Asian', 'ethnic_group': 'Other', 'email_1': 'xj961@example.com', 'email_2': 'test@gmail.com', 'email_3': 'test2@gmail.com', 'phone_1': '1818654010', 'phone_1_dnc': 'True', 'phone_2': '9377732292', 'phone_2_dnc': 'False', 'phone_3': '9087654311', 'phone_3_dnc': 'False'}, 
                'insight': 'Insight for first md5 123', 
                'sentence_1': 'another test sentence for first md5 123', 
                'sentence_2': 'test sentence for first md5 123', 
                'sentence_3': 'third test sentence for first md5 123', 
                'sentence_4': 'fourth test sentence for first md5 123', 
                'date_delivered': '2025-01-01'
            },
          
            {
                'md5': '456', 
                'pii': {'first_name': 'John', 'last_name': 'Davis', 'address': '8661 Maple St', 'city': 'Franklin', 'state': 'PA', 'zip_code': '31918', 'zip4': '7674', 'fips_state_code': '47', 'fips_county_code': '722', 'county_name': 'West County', 'latitude': '32.192241002390716', 'longitude': '-71.35995173709608', 'address_type': '', 'cbsa': '76180', 'census_tract': '132502', 'census_block_group': '9', 'census_block': '2839', 'gender': 'Female', 'scf': '238', 'dma': '479', 'msa': '124', 'congressional_district': '5', 'head_of_household': 'Yes', 'birth_month_and_year': '08/2000', 'age': '24', 'prop_type': 'Apartment', 'n_household_children': '4', 'credit_range': 'Fair', 'household_income': '150000+', 'household_net_worth': '250000-500000', 'home_owner_status': 'No', 'marital_status': 'Divorced', 'occupation': 'Lawyer', 'median_home_value': '405252', 'education': 'High School', 'length_of_residence': '7', 'n_household_adults': '3', 'political_party': 'Independent', 'health_beauty_products': '1', 'cosmetics': '0', 'jewelry': '1', 'investment_type': None, 'investments': '1', 'pet_owner': '1', 'pets_affinity': '0', 'health_affinity': '4', 'diet_affinity': '0', 'fitness_affinity': '2', 'outdoors_affinity': '3', 'boating_sailing_affinity': '4', 'camping_hiking_climbing_affinity': '3', 'fishing_affinity': '0', 'hunting_affinity': '5', 'aerobics': '3', 'nascar': '4', 'scuba': '5', 'weight_lifting': '0', 'healthy_living_interest': '5', 'motor_racing': '4', 'foreign_travel': '3', 'self_improvement': '2', 'walking': '3', 'fitness': '2', 'ethnicity_detail': 'Hispanic', 'ethnic_group': 'African American', 'email_1': 'zo401@example.com', 'email_2': None, 'email_3': None, 'phone_1': '3629822559', 'phone_1_dnc': 'True', 'phone_2': None, 'phone_2_dnc': None, 'phone_3': None, 'phone_3_dnc': None}, 
                'insight': 'Insight for second md5 456', 
                'sentence_1': 'sentence for second md5 456', 
                'sentence_2': 'another sentence for second md5 456', 
                'date_delivered': '2025-01-01'
            }
        ]

    return json.dumps(data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
