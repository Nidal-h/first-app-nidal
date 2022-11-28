from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Usere(BaseModel):
    id: int = None
    username: str
    password: str

class Settings(BaseModel):
    authjwt_secret_key: str = "my_jwt_secret"

@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.get("/")
def read_root():
    conn = psycopg2.connect(
        dbname='admin', user='postgres', password='nidal', host='localhost', port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM usere ORDER BY id DESC")
    rows = cur.fetchall()
    formatted_useres = []
    for row in rows:
        formatted_useres.append(
            Usere(
                id=row[0],
                username=row[1],
                password=row[2]
            )
        )
    cur.close()
    conn.close()
    return formatted_useres


@app.post('/login')
def login(usere: Usere, Authorize: AuthJWT = Depends()):
    conn = psycopg2.connect(
        dbname='admin', user='postgres', password='nidal', host='localhost', port=5432
    )
    cur = conn.cursor()
    cur.execute(f"INSERT INTO usere (id,username,password) VALUES('{usere.id}','{usere.username}','{usere.password}')")
    access_token = Authorize.create_access_token(subject=usere.username)
    cur.close()
    conn.commit()
    conn.close()
    return {"access_token": access_token}


@app.get('/test-jwt')
def user(Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    return {"user": 123124124, 'data': 'jwt test works'} 
    #current_user = Authorize.get_jwt_subject()
    #return {"user": current_user, 'data': 'jwt test works'}    
