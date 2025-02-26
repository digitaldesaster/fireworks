import os,json,sys
from openai import OpenAI
from openai import AzureOpenAI
import anthropic

from dotenv import load_dotenv
load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
together_api_key=os.getenv("TOGETHER_API_KEY")
anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
perplexity_api_key=os.getenv("PERPLEXITY_API_KEY")

azure_api_version = os.getenv('AZURE_API_VERSION_SE_02')
azure_api_key = os.getenv('AZURE_API_KEY_MN_SE_02')
azure_endpoint = os.getenv('AZURE_API_BASE_MN_SE_02')
azure_deployment = os.getenv('AZURE_API_MODEL_MN_SE_02')

#Notice: I was not able to have a function with streaming (using yield) and no streaming (return) at the same time.

def llm_call_stream(messages, model):
    if model['provider'] == 'anthropic':
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=model['model'],
            max_tokens=1000,
            temperature=0,
            system=messages[0]['content'],
            messages=messages[1:],
            stream=True
        )
        input_tokens = 0
        output_tokens = 0
        accumulated_text = ""
        for line in response:
            print(line.type)
            if line.type == 'message_start':
                input_tokens = line.message.usage.input_tokens
            elif line.type == 'message_delta':
                output_tokens = line.usage.output_tokens
            elif line.type == 'content_block_delta':
                if line.delta.text:
                    accumulated_text += line.delta.text
                    yield line.delta.text.encode('utf-8')
        if accumulated_text:
            yield " ".encode('utf-8')
        yield f"###STOP###{json.dumps({'prompt_tokens': input_tokens, 'completion_tokens': output_tokens, 'total_tokens': input_tokens + output_tokens})}".encode('utf-8')
    else:
        if model['provider']=='together':
            client = OpenAI(api_key=together_api_key,base_url='https://api.together.xyz/v1')
        elif model['provider']=='deepseek':
            client = OpenAI(api_key=deepseek_api_key,base_url='https://api.deepseek.com')
        elif model['provider']=='perplexity':
            client = OpenAI(api_key=perplexity_api_key,base_url='https://api.perplexity.ai')
        elif model['provider']=='openai':
            client = OpenAI(api_key=openai_api_key)
        elif model['provider']=='azure':
            client = AzureOpenAI(azure_endpoint=azure_endpoint,api_key=azure_api_key,api_version=azure_api_version)

        response = client.chat.completions.create(
            model=model['model'],
            messages=messages,
            stream=True
        )

        accumulated_text = ""
        citations = []
        for line in response:
            # Skip empty chunks or chunks without choices
            if not hasattr(line, 'choices') or len(line.choices) == 0:
                continue
                
            # Handle content if present
            if hasattr(line.choices[0], 'delta') and hasattr(line.choices[0].delta, 'content'):
                if line.choices[0].delta.content:
                    accumulated_text += line.choices[0].delta.content
                    yield line.choices[0].delta.content.encode('utf-8')
            
            # Handle completion
            if hasattr(line.choices[0], 'finish_reason') and line.choices[0].finish_reason in ['eos', 'stop']:
                if accumulated_text:
                    yield " ".encode('utf-8')
                try:
                    response_data = line.model_dump()
                    if 'citations' in response_data:
                        citations = response_data['citations']
                        print("Citations found:", citations)  # Print citations when found
                    usage_data = line.usage.model_dump()
                    usage_data['citations'] = citations
                    yield f"###STOP###{json.dumps(usage_data)}".encode('utf-8')
                except:
                    yield "###STOP###null".encode('utf-8')

def llm_call_no_stream(messages, model):
    if model['provider'] == 'anthropic':
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=model['model'],
            max_tokens=1000,
            temperature=0,
            system=messages[0]['content'],
            messages=messages[1:],
            stream=False
        )
        return response.content[0].text
    else:
        if model['provider']=='together':
            client = OpenAI(api_key=together_api_key,base_url='https://api.together.xyz/v1')
        elif model['provider']=='deepseek':
            client = OpenAI(api_key=deepseek_api_key,base_url='https://api.deepseek.com')
        elif model['provider']=='openai':
            client = OpenAI(api_key=openai_api_key)
        elif model['provider']=='azure':
            client = AzureOpenAI(azure_endpoint=azure_endpoint,api_key=azure_api_key,api_version=azure_api_version)

        response = client.chat.completions.create(
            model=model['model'],
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content

def llm_call(messages, model, stream=True):
    if stream:
        return llm_call_stream(messages, model)
    return llm_call_no_stream(messages, model)