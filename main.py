# app essentials
from fastapi import FastAPI, Depends, HTTPException
from langchain_community.llms import CTransformers
from langchain import PromptTemplate, LLMChain

import json
from uuid import uuid4

# db
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# core conversation func
from load_gpt import load_llm
from chatcore_history import run_chain as history_chain

# data models
from models.chatmodel import get_db, ChatSchema, MessageSchema, CompletedMessageSchema
from models.chatmodel import Chat

# for auth
from models.usermodel import User
from tools.security.auth import check_user

app = FastAPI()

# @app.get("/get_chat_history/{chat_id}", response_model=ChatSchema)
def get_chat_history(chat_id: str, db: Session):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")
    print(chat)
    return chat
    #return CompletedMessageSchema(id=chat.id, messages=[MessageSchema(sender=msg.sender, content=msg.content) for msg in chat.messages])

@app.get("/")
def test():
    return {"Hello": "World"}

@app.get("/checkdb")
def testdb(db: Session = Depends(get_db)):
    tables = db.execute(text("SELECT * FROM information_schema.tables WHERE table_schema = 'public'"))
    for table in tables:
        print(table)
    return {"output": "rds connections check complete"}


@app.post("/chat")
def chat(message : MessageSchema, db: Session = Depends(get_db), user: str = Depends(check_user)):

    history = "" 

    if message.chatid == '':
        # create new chat id
        response = run_chain(query=message.query, history=history)
        new_chat_message = CompletedMessageSchema(query=message.query, response=response)

        new_chat = Chat(messages=[new_chat_message.json()], owner = user)

        # push
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        #create response
        api_resp = {
             "chat_id" : new_chat.id,
             "response": response,
        }

        return api_resp

    else : 

        #check session to retrieve history
        chat_history = get_chat_history(message.chatid, db)
        #print(chat_history.messages)


        #message_list = [CompletedMessageSchema.parse_raw(msg) for msg in chat_history.messages]
        message_list = [msg for msg in chat_history.messages]
        print(len(message_list))

        # add new message and response to history
        response = run_chain(query=message.query, history="we were talking about global warming")

        new_chat_message = CompletedMessageSchema(query=message.query, response=response)
        message_list.append(new_chat_message.json())

        chat_history.messages=message_list
        chat_history.owner = user
        
        db.commit()
        
        return response


@app.post("/sessions")
def get_sessions(db: Session = Depends(get_db), user: str = Depends(check_user)): 

    chat_ids = db.query(Chat.id).filter(Chat.owner == user).all()

    sessions = [x[0] for x in chat_ids]

    return {"sessions" : sessions}

@app.post("/chat_history")
def get_session_history(chat_id : str, db: Session = Depends(get_db), user: str = Depends(check_user)): 


    #check session to retrieve history
    chat_history = get_chat_history(chat_id, db)
    #print(chat_history.messages)


    #message_list = [CompletedMessageSchema.parse_raw(msg) for msg in chat_history.messages]
    message_list = chat_history.messages
    #chat_history_json = json.loads(chat_history.messages)
    #message_list = [json.loads(msg for msg in chat_history_json]
    print(message_list)
    # for x in json.loads(message_list):
    #     print(x)



    api_resp = {
        "chat_history" : message_list,
        "items" : len(message_list)
    }

    return api_resp

@app.post("/chat_with_context")
def history_aware_chat(message : MessageSchema, db: Session = Depends(get_db), user: str = Depends(check_user)):

    history = "" 

    if message.chatid == '':
        # create new chat id

        chat_id = str(uuid4())

        response = history_chain(query=message.query, session_id=chat_id, history_data=history)
        new_chat_message = CompletedMessageSchema(query=message.query, response=response)
        
        new_chat = Chat()
        new_chat.chat_id = chat_id
        new_chat.messages=[new_chat_message.json()] 
        new_chat.owner = user

        # push
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        #create response
        api_resp = {
             "chat_id" : new_chat.id,
             "response": response,
        }

        return api_resp

    else : 

        #check session to retrieve history
        chat_history = get_chat_history(message.chatid, db)
        #print(chat_history.messages)


        #message_list = [CompletedMessageSchema.parse_raw(msg) for msg in chat_history.messages]
        
        message_list = [json.loads(msg) if type(msg) == str else msg for msg in chat_history.messages ]


        #print(json.loads(message_list[0]))

        # add new message and response to history
        response = history_chain(query=message.query, session_id=message.chatid, history_data=message_list)

        new_chat_message = CompletedMessageSchema(query=message.query, response=response)
        message_list.append(new_chat_message.json())

        chat_history.messages=message_list
        chat_history.owner = user
        
        db.commit()
        
        return response



# will be moved to a separate script
from pydantic import BaseModel

class Query(BaseModel):
    text : str

def get_llm(select):
    if select == "OPEN-AI":
        llm = load_llm()
    else:
        model_name = "TheBloke/CodeLlama-13B-Instruct-GGUF"
        model_file="codellama-13b-instruct.Q4_K_M.gguf"
        config = {'max_new_tokens': 1024, 'repetition_penalty': 1.1, 'context_length': 8000, 'temperature':0, 'gpu_layers':50}
        llm = CTransformers(model=model_name, model_file=model_file, model_type='llama', gpu_layers=50, config=config)
    return llm

def generate_prompt(prompt_file="prompt.md"):
    with open(prompt_file, "r") as f:
        prompt = f.read()

    promt_temp = PromptTemplate(template=prompt, input_variables=["query"])
    return promt_temp   

prompt_template = generate_prompt()
llm = get_llm("OPEN-AI")
llmchain = LLMChain(llm=llm, prompt=prompt_template)

@app.post("/get_entities/")
async def get_entities(query: Query):
    result = llmchain.invoke({"query":query.text})
    output = result['text']
    entities = output[output.find("(")+1:output.find(")")]
    return entities

import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(3000))