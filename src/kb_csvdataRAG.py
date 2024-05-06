from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
import boto3
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import RetrievalQA

def print_documents(documents):
    for index, doc in enumerate(documents, start=1):
       print("*"*100)
       print(doc)
default_retrieval_config ={
        "vectorSearchConfiguration":
                {
                    "numberOfResults": 10
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
                                    "value": 4
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

#documents = bedrock_kb_retriever.invoke("What are nasty user reviews ?")
#print_documents(documents)

chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(),retriever=bedrock_kb_retriever,return_source_documents=True)
res  = chain.invoke({"query":"what is most popular tea brand?"})
print(res['result'])
print("\n SOURCES:")
for index, doc in enumerate(res['source_documents'], start=1):
    print("*"*100)
    print(f"{doc.page_content[:100]} ...")
    print(doc.metadata)

'''
client = boto3.client('bedrock-agent-runtime')
res = client.retrieve(
    knowledgeBaseId="3YUYA3WYSC",
    retrievalConfiguration=good_score_retrieval_config,
    retrievalQuery={
        "text": "What are some positive chicken dish reviews ?"
    }
)

print(res)
'''

