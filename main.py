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

DATABASE_URL = "postgresql://rwvahszjfezquh:ccd6ec796965f82152cb1bc12755075a992d7ca39c40d822289a7de025eb0552@ec2-3-213-66-35.compute-1.amazonaws.com:5432/dblb4f4gek8tpo"

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

class Settings(BaseModel):
    authjwt_secret_key: str = "my_jwt_secret"

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
@app.get("/", response_model=List[Usere])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.post("/login", response_model=Usere)
async def create_user(usere: Usere, Authorize: AuthJWT = Depends()):
    query = users.insert().values(username=usere.username, password=usere.password)
    last_record_id = await database.execute(query)
    return {**usere.dict(), "id": last_record_id}   

@app.get('/test-jwt')
def user(Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    return {"user": 123124124, 'data': 'jwt test works'} 
    #current_user = Authorize.get_jwt_subject()
    #return {"user": current_user, 'data': 'jwt test works'} 

