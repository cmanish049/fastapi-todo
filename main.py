from fastapi import FastAPI

import models
from database import engine
from router import admin, auth, todos, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(router=admin.router)
app.include_router(router=users.router)
