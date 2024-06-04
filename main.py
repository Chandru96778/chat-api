from fastapi import FastAPI
from chatcore import run_chain
from pydantic import BaseModel
from load_gpt import load_llm
from langchain_community.llms import CTransformers
from langchain import PromptTemplate, LLMChain
from pydantic import BaseModel


app = FastAPI()

class Question(BaseModel):
    query: str
    session_id: str
    
class Query(BaseModel):
    text : str

@app.get("/")
def test():
    return {"Hello": "World"}


@app.post("/chat")
def chat(question : Question):

    #check session to retrieve history
    history = ""

    return run_chain(query=question.query, history=history)


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
