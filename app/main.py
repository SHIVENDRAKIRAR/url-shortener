from fastapi import FastAPI
from sqlalchemy import text

from app.database.db import engine
from app.models.url import Base
from app.models.user import User
from app.routes.url import router as url_router
from app.routes.auth import router as auth_router

app = FastAPI()

Base.metadata.create_all(bind=engine)
User.metadata.create_all(bind=engine)

app.include_router(url_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "URL Shortener API Running"}


@app.get("/test-db")
def test_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"message": "Database connected successfully"}

    except Exception as e:
        return {"error": str(e)}