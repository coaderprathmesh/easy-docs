from agents import graph
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
#importing packages for excepting multiple file at ones.
from fastapi import UploadFile, File
from typing import List
#the function to imbed the documents in vector.
from ingest_data import process_docs

#constructor
app = FastAPI()
#setting templates directory
templates = Jinja2Templates(directory="templates")
#mounting the static files
app.mount("/static", StaticFiles(directory="static"), name="static")
#home page constructor
@app.get("/")
async def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.post("/upload")
async def upload_docs(files: List[UploadFile] = File(...)):
    count_chunks = 0
    for file in files:
        file_name = file.filename
        file_content = await file.read()
        chunks = process_docs(file_name,file_content)
        if int(chunks):
            count_chunks += chunks
    return {"response":f"files processed: {len(files)} and total chunks: {count_chunks}"}


#chat interface

#defining the query type
class ChatRequest(BaseModel):
    user_query: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def ask(request: ChatRequest):
    result = graph.invoke({
        "question": request.user_query
    })
    return ChatResponse(answer=result["full_answer"])
