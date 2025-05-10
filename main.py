import sys
import os
dirpath = os.path.dirname(__file__)
sys.path.append(dirpath)  # adds current dir to path
from typing import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend import ChatRequest, CharacterInfo, query_deepseek, initiate_query_deepseek, check_file_exists, replace_template
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",  # <-- must match exactly!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # no wildcards
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods: POST, GET, etc
    allow_headers=["*"],  # allow all headers
)

# Mount /static to serve files from ./static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class TextData(BaseModel):
    text: str

@app.post("/chat/")
async def chat(data: ChatRequest):
    # history_filepath = request.cookies.get('history_filepath')
    reply = query_deepseek(data.message, data.path)
    
    content = {"reply": reply}
    response = JSONResponse(content=content)
    return response

@app.post("/initiate/")
async def initiate_chat(character_info: CharacterInfo):
    message, filepath = initiate_query_deepseek(character_info)
    
    content = {"message": "User info saved successfully!", "file": filepath, "Reply": message}
    response = JSONResponse(content=content)
    # response.set_cookie(key="history_filepath", value=filepath, secure=True, samesite='none')
    return response


@app.post("/replace-template/")
async def replace_template_endpoint(text_data: TextData):
    success = replace_template(text_data.text)
    if success:
        return JSONResponse({"message": "Template replaced successfully!"})
    else:
        raise HTTPException(status_code=500, detail="Failed to replace template.")


@app.get("/")
async def root():
    return {"message": "Welcome to the Voice Clone Preparation API (F5-TTS Ready)"}
