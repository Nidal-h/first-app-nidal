from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from typing import List
import databases
import sqlalchemy

DATABASE_URL = "postgresql://suhcsqekypfson:399b493c1c5e6d81c81833d4f33830b16d5fc671e7e4127a1a61a244c4702706@ec2-44-205-112-253.compute-1.amazonaws.com:5432/deopdbh5407fba"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(

    "users",

    metadata,

    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),

    sqlalchemy.Column("username", sqlalchemy.String),

    sqlalchemy.Column("password", sqlalchemy.String),


)



engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

class Usere(BaseModel):
    id: int = None
    username: str
    password: str

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
@app.get("/", response_model=List[Usere])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.post("/login", response_model=Usere)
async def create_user(usere: Usere, Authorize: AuthJWT = Depends()):
    query = users.insert().values(username=usere.username, password=usere.password)
    last_record_id = await database.execute(query)
    return {**usere.dict(), "id": last_record_id}
    

