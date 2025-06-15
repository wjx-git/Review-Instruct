import json
import openai
import requests
from openai import OpenAI
import time
import os

# example, please put all model names into the list here
supported_models = ['gpt-4-turbo-preview']

API_MAX_RETRY = 5
API_RETRY_SLEEP = 30
API_ERROR_OUTPUT = "$ERROR$"

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# openai model
# with openai
def chat_completion_openai(model, conv, temperature, max_tokens=2048, n=1):
    """
    input:
        conv: the message [{'role': 'message'}]
    output:
        if n > 1: [str]
        if n = 1: str
    """
    output = API_ERROR_OUTPUT
    for retry_i in range(API_MAX_RETRY):
        try:
            response = openai_client.chat.completions.create(model=model,
                messages=conv,
                n=n,
                temperature=temperature,
                max_tokens=max_tokens)
            if n == 1:
                output = response.choices[0].message.content
            else:
                output = [response.choices[i].message.content for i in range(n)]
            break
        except openai.OpenAIError as e:
            print(f'{model} encountered error')
            print(type(e), e)
            if retry_i == API_MAX_RETRY - 1:
                raise e
            else:
                time.sleep(API_RETRY_SLEEP)
    return output



# map to api_utils
# please put all api calling functions here
def generate_response(model, conv, temperature = 0.1, max_tokens = 400, n = 1, model_name = None):
    if model_name is None:
        name = model.model_name
    else:
        name = model_name

    if name in supported_models:
        output = chat_completion_openai(name, conv, temperature = temperature, max_tokens = max_tokens, n = n)
        return output
    else:
        raise ValueError(f"Unsupported model: {model}")