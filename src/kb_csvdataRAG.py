from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
import boto3
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import RetrievalQA
from uuid import uuid4

def print_documents(documents):
    for index, doc in enumerate(documents, start=1):
       print("*"*100)
       print(doc)

default_retrieval_config ={
        "vectorSearchConfiguration":
                {
                    "numberOfResults": 5
                }
        }  

good_score_retrieval_config ={
        "vectorSearchConfiguration":
        {
            "numberOfResults": 10,
            "filter": {
                "andAll":[
                        {
                            "greaterThanOrEquals":
                                {
                                    "key": "Score",
                                    "value": 3
                                }
                        },
                         {
                            "greaterThan":
                                {
                                    "key": "Time",
                                    "value": 1273152420
                                }
                        }
                        ]
                    }
                
            }
        }       
bad_score_retrieval_config ={
        "vectorSearchConfiguration":
        {
            "numberOfResults": 10,
            "filter": {
                "andAll":[
                        {
                            "lessThan":
                                {
                                    "key": "Score",
                                    "value": 3
                                }
                        },
                         {
                            "greaterThan":
                                {
                                    "key": "Time",
                                    "value": 1273152420
                                }
                        }
                        ]
                    }
                
            }
        } 


kbi= "3YUYA3WYSC"
#kbi = "8Y8SHTFJQ9"

bedrock_kb_retriever = AmazonKnowledgeBasesRetriever(knowledge_base_id=kbi,
                                                     retrieval_config=good_score_retrieval_config,
                                                     region_name="us-east-1",
                                                     credentials_profile_name="default"
                                                    )

def as_lc_kb_retriever():
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        documents = bedrock_kb_retriever.invoke(q_)
        print_documents(documents)

def as_lc_kb_RAG():

    chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(),retriever=bedrock_kb_retriever,return_source_documents=True)
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        res  = chain.invoke({"query":q_})
        print(res['result'])
        print("\n SOURCES:")
        for index, doc in enumerate(res['source_documents'], start=1):
            print("_"*100)
            print(f"{doc.page_content[:200]} ...")
        print(doc.metadata)


def as_br_kb_retriever():

    client = boto3.client('bedrock-agent-runtime')
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        res = client.retrieve(
            knowledgeBaseId=kbi,
            retrievalConfiguration=good_score_retrieval_config,
            retrievalQuery={
                "text": q_
            }
        )

        for index, doc in enumerate(res['retrievalResults'], start=1):
            print("-"*150)
            print(f"{doc['content']}")
            print(f"{doc['metadata']}")


def as_br_kb_retriever_generate():

    client = boto3.client('bedrock-agent-runtime')
    session_id = str(uuid4())
    while True:
        q_ = input("(q to quit): ")
        if q_ == 'q':
            break
        res = client.retrieve_and_generate(
            input={
                "text": q_
            },
            retrieveAndGenerateConfiguration={
                "knowledgeBaseConfiguration" : {
                    "knowledgeBaseId":kbi,
                    "modelArn": "anthropic.claude-v2:1",
                    "retrievalConfiguration": good_score_retrieval_config
                },
                "type": "KNOWLEDGE_BASE"
            }
            #sessionId= "JHJMNBNMB67686"
            )

        print(res['output']['text'])
        print(f"Citations : {len(res['citations'])}")
        #inline for loop to iterate over citations array in res
        for index, citation in enumerate(res['citations'], start=1):
            #iterate retrievedReferences array are display metadata
            for retrievedref in citation['retrievedReferences']:
                print(f"{retrievedref['metadata']}")



#as_br_kb_retriever()
#as_br_kb_retriever_generate()
as_lc_kb_RAG()

