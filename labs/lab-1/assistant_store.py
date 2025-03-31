import os
import json
import requests
import time
from openai import AzureOpenAI

#read .env variables
from dotenv import load_dotenv
load_dotenv()

# print("AZURE_OPENAI_API_KEY:", os.getenv("AZURE_OPENAI_API_KEY"))
print("AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))


client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key= os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-05-01-preview"
)

# Read vector store ID and model name from .env
vector_store_id = os.getenv("VECTOR_STORE_ID")
model_name = os.getenv("MODEL_NAME")

assistant = client.beta.assistants.create(
  model=model_name,  # Use model name from .env
  instructions="",
  tools=[{"type": "file_search"}],
  tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
  temperature=1,
  top_p=1
)

##
# Create a thread
thread = client.beta.threads.create()

# Add a user question to the thread
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="what happened in ukraine?" # Replace this with your prompt
)

# Print the content of the created message
print(message.content[0].text.value)  # Access and print the value

# Run the thread
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)

# Looping until the run completes or fails
while run.status in ['queued', 'in_progress', 'cancelling']:
  time.sleep(1)
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )

if run.status == 'completed':
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    # Extract and print the content of each message
    for message in messages.data:
        if message.role == 'assistant':  # Only print the assistant's response
            for content_block in message.content:
                if content_block.type == 'text':  # Ensure it's a text block
                    print(content_block.text.value)
elif run.status == 'requires_action':
    # the assistant requires calling some functions
    # and submit the tool outputs back to the run
    pass
else:
    print(run.status)