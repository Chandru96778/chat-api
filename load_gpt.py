import boto3
from botocore.exceptions import ClientError
import json
import os
from openai import AzureOpenAI
import langchain_openai
from langchain_openai import AzureChatOpenAI, AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings





def get_secret():
    secret_name = "trc/azure/openai"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
            return text_secret_data
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            return binary_secret_data
        # Your code goes here.

def load_llm():

  text_secret_data = get_secret()
  json_data = json.loads(text_secret_data)
  # print(json_data["Key1"])
  os.environ["AZURE_OPENAI_API_KEY"] = json_data["Key1"]
  os.environ["AZURE_OPENAI_ENDPOINT"] = "https://azrzzzatopenai.openai.azure.com/"

  # os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
  os.environ["OPENAI_API_VERSION"] = "2023-05-15"



  llm = AzureChatOpenAI(
      deployment_name="TRC-RFP-GEN-AI",
      temperature= 1)
  
  return llm

def load_embeddings():
    text_secret_data = get_secret()
    json_data = json.loads(text_secret_data)
    # print(json_data["Key1"])
    os.environ["AZURE_OPENAI_API_KEY"] = json_data["Key1"]
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://azrzzzatopenai.openai.azure.com/"

    # os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"



    

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="TRC-RFP-GEN-AI-Embedding-ADA",
        openai_api_version="2023-05-15"
    )
        
    
    return embeddings



import os
from openai import AzureOpenAI

def load_openai():

  text_secret_data = get_secret()
  json_data = json.loads(text_secret_data)
  # print(json_data["Key1"])
  os.environ["AZURE_OPENAI_API_KEY"] = json_data["Key1"]
  os.environ["AZURE_OPENAI_ENDPOINT"] = "https://azrzzzatopenai.openai.azure.com/"

  os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"

      
  client = AzureOpenAI(
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
      api_version=os.getenv("OPENAI_API_VERSION"),
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
      )

  # completion = client.completions.create(
  #     model="TRC-RFP-GEN-AI",
  #     prompt=prompt
  # )

  return client




