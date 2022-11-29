from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy


DATABASE_URL = "postgresql://ponmmpifcdwawm:a9dacb1e8bbec96ad1952c04763d355a06c130813fd8231f257c96fae30fb166@ec2-54-174-31-7.compute-1.amazonaws.com:5432/d7643pet7550o5"

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def create_user(usere: Usere):
    query = users.insert().values(username=usere.username, password=usere.password)
    last_record_id = await database.execute(query)
    return {**usere.dict(), "id": last_record_id}   

