from load_gpt import load_embeddings, load_llm
from langchain.prompts import PromptTemplate

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader


from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import BaseMessage

from typing import Sequence, List


from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers import ContextualCompressionRetriever



def load_vectorbase(embeddings):
    vectorstore = Chroma(persist_directory="chroma_db",
           collection_name = "trc_pages_collection",  
           embedding_function=embeddings)
    return vectorstore

embeddings = load_embeddings()

store = {}



def llm_chain(history):
    try:

       
        llm = load_llm()
        
        
        embeddings = load_embeddings()

        vectorbase = load_vectorbase(embeddings)
        retriever = vectorbase.as_retriever(search_type="similarity_score_threshold", 
                    search_kwargs={"score_threshold": 0.7})

        #print(retriever.aget_relevant_documents("what are the goals of trc"))
        
        multi_retriever = MultiQueryRetriever.from_llm(
                    retriever=retriever, 
                    llm=llm
                )
        
        embeddings_filter = EmbeddingsFilter(embeddings=embeddings)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=embeddings_filter, base_retriever=multi_retriever
        )
        
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
                which might reference context in the chat history, formulate a standalone question \
                which can be understood without the chat history. Do NOT answer the question, \
                just reformulate it if needed and otherwise return it as is.
                """


        ### Contextualize question ###
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        

        print("reached retrievalchain")
        
        history_aware_retriever = create_history_aware_retriever(
            llm, compression_retriever, contextualize_q_prompt
        )


        ### Answer question ###
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know.\

        {context}"""


        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


        ### Statefully manage chat history ###

        # print ("STORE VALUE:", store)
        print("reached----------------209")


        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in store:
                print("reached----------------214")
                #store[session_id] = history.get_messages()
                store[session_id] = history
            return store[session_id]


        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        return conversational_rag_chain

    except Exception as e:
        print("Exception occurred in load_model_and_embeddings:", e)
        return None

class MyChatMessageHistory(BaseChatMessageHistory):
    def __init__(self):
        super().__init__()
        self.messages: List[BaseMessage] = []


    def add_messages(self, messages: Sequence[BaseMessage]):
        self.messages.extend(messages)

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []

# Create an instance of the custom chat message history

def array_to_chat_history(my_history, history_data):
    for entry in history_data:
        human_message = HumanMessage(content=entry['query'])
        ai_message = AIMessage(content=entry['response'])
        my_history.add_message(human_message)
        my_history.add_message(ai_message)


    return my_history
    
def run_chain(query, session_id, history_data):

    #embeddings = load_embeddings()
    #my_history = MyChatMessageHistory()
    my_history = ChatMessageHistory()

    updated_history = array_to_chat_history(my_history, history_data)

    qa = llm_chain(updated_history)

    #result = qa.invoke({"input": query, "chat_history": updated_history},config={"configurable": {"session_id": session_id}})
    result = qa.invoke({"input": query, "chat_history": updated_history},config={"configurable": {"session_id": session_id}})

    print(result)

    response = result["answer"]
    return response
