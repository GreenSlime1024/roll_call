from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import motor.motor_asyncio as motor
from dotenv import load_dotenv
import os
from typing import Literal
import re

app = FastAPI()

load_dotenv()

mongo = motor.AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = mongo["rollcall"]
coll = db["people"]

SECRET_KEY = os.getenv("JWT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
ESP32_TOKEN = os.getenv("ESP32_TOKEN")

security = HTTPBearer()

def is_valid_email(email: str) -> bool:
    if email == "greenslime1024@gmail.com":
        return True
    pattern = r"std111310[1-9]@goo\.tyai\.tyc\.edu\.tw$|std11131[0-2][0-9]@goo\.tyai\.tyc\.edu\.tw$|std111313[0-7]@goo\.tyai\.tyc\.edu\.tw$"
    return bool(re.match(pattern, email))

def is_admin_email(email: str) -> bool:
    return email in ["std1113125@goo.tyai.tyc.edu.tw", "std1113114@goo.tyai.tyc.edu.tw", "std1113118@goo.tyai.tyc.edu.tw"]

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        if not is_valid_email(payload['email']):
            raise HTTPException(status_code=403, detail="Unauthorized email domain")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_admin(token: dict = Depends(verify_token)):
    if not is_admin_email(token['email']):
        raise HTTPException(status_code=403, detail="Admin access required")
    return token

async def verify_esp32_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if credentials.credentials != ESP32_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid ESP32 token")
        return True
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

class Person(BaseModel):
    rfid_id: str
    student_id: int | None = None
    present: bool | None = None
    type: Literal["student_id", "present", None] = None
    

@app.get("/api")
async def hello_world(token: dict = Depends(verify_token)):
    return f"Hello, {token['username']}!"

@app.post("/api/login")
async def login(credential: dict):
    try:
        google_token = credential.get("credential")
        idinfo = id_token.verify_oauth2_token(google_token, requests.Request(), GOOGLE_CLIENT_ID)
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = idinfo['email']
        if not is_valid_email(email):
            raise HTTPException(status_code=403, detail="Unauthorized email domain")
            
        token = jwt.encode({
            'sub': idinfo['sub'],
            'email': email,
            'username': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'exp': datetime.now() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        return {"token": token}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

@app.post("/api/person")
async def person(person: Person, token: dict = Depends(verify_admin)):
    if person.type is None:
        person_doc = await coll.find_one({"rfid_id": person.rfid_id})
        if person_doc is None:
            await coll.delete_many({"student_id": None})
            await coll.insert_one({"rfid_id": person.rfid_id, "student_id": person.student_id, "present": person.present})
            return {"message": "Added person"}
        else:
            await coll.update_one({"_id": person_doc["_id"]}, {"$set": {"present": person.present}})
            return {"message": "Added person", "student_id": person_doc["student_id"]}
    
    elif person.type == "student_id":
        student_id_doc = await coll.find_one({"student_id": person.student_id})
        if student_id_doc is not None:
            raise HTTPException(status_code=400, detail="Student ID already in use")
        await coll.update_one({"rfid_id": person.rfid_id}, {"$set": {"student_id": person.student_id}})
        return {"message": "Updated student_id"}
    
    elif person.type == "present":
        await coll.update_one({"rfid_id": person.rfid_id}, {"$set": {"present": person.present}})
        return {"message": "Updated present status"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid type")

@app.post("/api/esp32/person")
async def esp32_person(person: Person, verified: bool = Depends(verify_esp32_token)):
    person_doc = await coll.find_one({"rfid_id": person.rfid_id})
    if person_doc is None:
        await coll.delete_many({"student_id": None})
        await coll.insert_one({"rfid_id": person.rfid_id, "student_id": None, "present": True})
        return {"message": "Added person"}
    else:
        await coll.update_one({"_id": person_doc["_id"]}, {"$set": {"present": True}})
        return {"message": "Updated person", "student_id": person_doc["student_id"]}

@app.get("/api/people")
async def people(token: dict = Depends(verify_token)):
    people = []
    async for person in coll.find():
        del person["_id"]
        people.append(person)
    return {"people": people}

@app.get("/api/check-admin")
async def check_admin(token: dict = Depends(verify_token)):
    return {"is_admin": is_admin_email(token['email'])}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8000)