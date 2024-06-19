import bs4
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def check_vectorstore():

def llm_chain():
    try:
        
        print("reached------------->")
        
        # vectorstore = Chroma(persist_directory="chroma_db",
        #                     collection_name = "trc_pages_collection",  
        #                     embedding_function=st.session_state['embeddings'])
        
        print("--------------------->vectorstore", st.session_state["vectorestore_web"])
        
        llm = load_llm()

        print("--------------------->llm", llm)


        retriever = st.session_state["vectorestore_web"].as_retriever(search_type="similarity_score_threshold", 
                    search_kwargs={"score_threshold": 0.7})
        
        print("----------------->kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", retriever.get_relevant_documents("who is the CIO,CEO,CFO of TRC Companies?"))
        
        multi_retriever = MultiQueryRetriever.from_llm(
                    retriever=st.session_state["vectorestore_web"].as_retriever(search_type="similarity_score_threshold", 
                    search_kwargs={"score_threshold": 0.7}), llm=llm
                )
        print("reached----------------147")
        
        embeddings = load_embeddings()
        print("reached----------------150")
        embeddings_filter = EmbeddingsFilter(embeddings=embeddings)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=embeddings_filter, base_retriever=multi_retriever
        )
        print("reached----------------155")

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
        print("reached----------------173")

        history_aware_retriever = create_history_aware_retriever(
            llm, compression_retriever, contextualize_q_prompt
        )

        print("reached----------------179")


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

        print("reached----------------200")


        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


        ### Statefully manage chat history ###
        store = {}

        # print ("STORE VALUE:", store)
        print("reached----------------209")


        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in store:
                print("reached----------------214")
                store[session_id] = ChatMessageHistory()
            return store[session_id]


        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )


    #     print("-------->228",conversational_rag_chain.invoke(  
    # {"question": "I am interviewing for a senior leadership position at TRC Companies. Give me some background on the company's CEO, CIO and CFO"},
    # config={"configurable": {"session_id": '1234sbs'}}
# ))

        # print("------ retriver----->",compression_retriever.get_relevant_documents(query = "I am interviewing for a senior leadership position at TRC Companies. Give me some background on the company's CEO, CIO and CFO"))
        return conversational_rag_chain
    except Exception as e:
        print("Exception occurred in load_chain:", e)