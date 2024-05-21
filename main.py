from fastapi import FastAPI
from chatcore import run_chain
from pydantic import BaseModel


app = FastAPI()

class Question(BaseModel):
    query: str
    session_id: str
    



@app.get("/")
def test():
    return {"Hello": "World"}


@app.post("/chat")
def chat(question : Question):

    #check session to retrieve history
    history = ""

    return run_chain(query=question.query, history=history)