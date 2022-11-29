from typing import List

import databases

import sqlalchemy

from fastapi import FastAPI
from pydantic import BaseModel


DATABASE_URL = "postgresql://wgyequohwxqqbw:aef771f22dda6d3a9d190dfc2ba030033c2bc2bb2408301841cefec53d987036@ec2-3-219-135-162.compute-1.amazonaws.com:5432/djbagsds6mm4t"

database = databases.Database(DATABASE_URL)


metadata = sqlalchemy.MetaData()



notes = sqlalchemy.Table(

    "notes",

    metadata,

    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),

    sqlalchemy.Column("text", sqlalchemy.String),

    sqlalchemy.Column("completed", sqlalchemy.Boolean),

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
    text: str
    completed: bool


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
async def create_note(note: NoteIn):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

