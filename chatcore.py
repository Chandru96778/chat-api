from load_gpt import load_embeddings, load_llm
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

from load_gpt import load_embeddings, load_llm
from langchain.chains import ConversationChain


def llm_chain():
    try:

       
        llm = load_llm()
        
        print("---------------->",llm, flush=True)

        sys_prompt = """
                    You are a helpful, respectful and honest assistant who can respond as learned personality with excellent learning capabilities and explanability.
                    Always answer as helpfully as possible, while being safe. 
                    Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. 
                    Please ensure that your responses are socially unbiased and positive in nature.

                    If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. 
                    If you don't know the answer to a question, please don't share false information.
                    
                    Your name is TRC BOT. You are an Intelligent TRC_Assistant for TRC Companies Inc. 
                    Always answer as helpfully as possible using the context text provided. 
                    Your answers should only answer the question once and not have any text after the answer is done.
                    
                    Do not end the answer abruptly instead build the conversation with user.
                    Give good explanation on what you are answering and use great vocabulary.
                    Explain your answer, do not give one line answers.
                    """
        instruction = """
                    Current conversation:
                    {history}
                    TRC_member: {input}
                    TRC_Bot:
                    """

        prompt_template = sys_prompt + instruction

        prompt = PromptTemplate(input_variables=["history","input"], template= prompt_template)
        
        print(prompt)
        

        print("reached retrievalchain")
        
        window_memory = ConversationBufferWindowMemory(human_prefix="TRC_Member", 
                                                    k=10,
                                                    memory_key = "history"
                                                    )
        qa = ConversationChain(
                prompt=prompt,
                llm=llm,
                verbose = True,
                memory= window_memory
                )
        return qa
    except Exception as e:
        print("Exception occurred in load_model_and_embeddings:", e)
        return None
    
def run_chain(query, history):

    #embeddings = load_embeddings()
    qa = llm_chain()
    result = qa.predict(input = query)
            # print("123",result)
            
    response = result
    return response
