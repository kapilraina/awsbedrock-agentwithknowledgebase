from langchain_aws import BedrockLLM
from langchain_aws import ChatBedrock
from langchain.memory import ChatMessageHistory

from langchain_community.embeddings.bedrock import BedrockEmbeddings

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import RetrievalQA
import boto3
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain.agents.agent_toolkits.conversational_retrieval.tool import create_retriever_tool

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
import boto3
from uuid import uuid4

parameters = {
    "max_new_tokens": 100,
    "num_return_sequences": 1,
    "top_k": 50,
    "top_p": 0.95,
    "do_sample": False,
    "return_full_text": True,
    "temperature": 0.2,
}

llm_titan = BedrockLLM(credentials_profile_name="default",
                    model_id="amazon.titan-text-express-v1",
                    region_name="us-east-1")

model_kwargs_claude = {"temperature": 0, "top_k": 10}
chat_claude = ChatBedrock(model_id="anthropic.claude-v2", 
                          region_name="us-east-1",
                          credentials_profile_name="default",
                          verbose=False,
                          model_kwargs=model_kwargs_claude)


embeddings_bedrock = BedrockEmbeddings(credentials_profile_name="default",
                                       region_name="us-east-1"
                                       )

bedrock_kb_retriever = AmazonKnowledgeBasesRetriever(knowledge_base_id="BCVTY5BVYX",
                                                     retrieval_config={"vectorSearchConfiguration":{"numberOfResults": 5}},
                                                     region_name="us-east-1",
                                                     credentials_profile_name="default"
                                                    )

tool = create_retriever_tool(
                bedrock_kb_retriever,
                "History_of_The_world",
                "Use to know about history of the world",
                )

'''
Use AWS Bedrock knowledgebase purely as a semantic search function, with no LLM dependency on retrievaal
'''
def raw_knowledgebase():
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        documents = bedrock_kb_retriever.invoke(q_)
        print_documents(documents)

'''
Use AWS Bedrock knowledge base as Retriever to augment in a RAG use-case. Here RAG is implemented as a lanchain QA chain.
Knowledge base datasource setup creates the pipeline for knowledge documents to be synced for embedding in OpenSearch.
'''

def knowledgebase_RAG():
    chain = RetrievalQA.from_chain_type(llm=chat_claude,retriever=bedrock_kb_retriever,return_source_documents=True)
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        res  = chain.invoke({"query":q_})
        print(res['result'])
        print("\n SOURCES:")
        for index, doc in enumerate(res['source_documents'], start=1):
            print("*"*100)
            print(f"{doc.page_content[:100]} ...")
            print(doc.metadata)


'''
Use AWS Bedrock knowledge base retriever as one of the tool in Agentic framework (langchain ReAact Agent here).
Includes external websearch tool and knowledge base retriever tools for agent executor to orchestrate.
needs SERPER_API_KEY
'''
def knowledgebase_retriever_Agentic():
    retriever_tool = create_retriever_tool(bedrock_kb_retriever,"World History,revolutions, religions, religious history, Reative Architecture, DDD, Microservices, Domain Driven Design, CQRS, Reactive Manifesto",
                                           "World History,revolutions, religions, religious history, Reative Architecture, DDD, Microservices, Domain Driven Design, CQRS, Reactive Manifesto")
    #Google Search API
    search = GoogleSerperAPIWrapper(k=2)
    search_tool = Tool(name="GoogleSearch", func=search.run, description="Use to search on google for a maximum of 2 times")
    alltools = [ retriever_tool,search_tool]

    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(chat_claude, alltools, prompt)
    memory = ChatMessageHistory(session_id="chat-history")
    agent_executor = AgentExecutor(agent=agent, tools=alltools,handle_parsing_errors=True,verbose=False)
    agent_with_chat_history = RunnableWithMessageHistory(
                    agent_executor,
                    lambda session_id: memory,
                    input_messages_key="input",
                    history_messages_key="chat_history",
                )
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        res = agent_with_chat_history.invoke({"input": q_},
                    config={"configurable": {"session_id": "JHJMNBNMB67686"}})
        print(res['output'])
    
'''
Use Bedrock Agent via AWS SDK. The Agent is configured to hanlde user session and maintains state and memory. So client doesnt have to do it.
'''
def bedrock_Agent():
    client = boto3.client('bedrock-agent-runtime')
    session_id = str(uuid4())
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        res = client.invoke_agent(agentAliasId="TMYXHNPEKI",agentId="MWNIEHJPHT",sessionId=session_id,inputText=q_)
        eventstream  = res['completion']
        for event in eventstream:
            print(event['chunk'])



def print_documents(documents):
    for index, doc in enumerate(documents, start=1):
       print("*"*100)
       print(doc)





#raw_knowledgebase()
#knowledgebase_RAG()
#knowledgebase_retriever_Agentic()
bedrock_Agent()