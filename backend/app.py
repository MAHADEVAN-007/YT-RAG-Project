from fastapi import FastAPI
from typing import Annotated

app = FastAPI()



@app.get('/home', name='home')
async def home(request: Request)

