from typing import List

import databases

import sqlalchemy

from fastapi import FastAPI
from pydantic import BaseModel


DATABASE_URL = "postgresql://ponmmpifcdwawm:a9dacb1e8bbec96ad1952c04763d355a06c130813fd8231f257c96fae30fb166@ec2-54-174-31-7.compute-1.amazonaws.com:5432/d7643pet7550o5"

database = databases.Database(DATABASE_URL)


metadata = sqlalchemy.MetaData()



notes = sqlalchemy.Table(

    "notes",

    metadata,

    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),

    sqlalchemy.Column("username", sqlalchemy.String),

    sqlalchemy.Column("password", sqlalchemy.String),

)



engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)


class NoteIn(BaseModel):
    text: str
    completed: bool


class Note(BaseModel):
    id: int
    username: str
    password: str


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note)
async def create_note(note: Note):
    query = notes.insert().values(username=note.username, password=note.password)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

