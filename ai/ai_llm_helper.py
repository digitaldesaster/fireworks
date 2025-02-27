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

        # Check if the model is an O1 model (o1-mini, o1-preview, etc.)
        is_o1_model = model['model'].startswith('o1-')
        
        # Handle O1 models - they don't support system messages or streaming
        if is_o1_model:
            # O1 models don't support system messages, so convert system to user if present
            prepared_messages = messages.copy()
            if len(prepared_messages) > 0 and prepared_messages[0]['role'] == 'system':
                prepared_messages[0]['role'] = 'user'
            
            # O1 models don't support streaming, so always use non-streaming approach
            response = client.chat.completions.create(
                model=model['model'],
                messages=prepared_messages,
                stream=True
            )
            # Handle non-streaming O1 response
            content = response.choices[0].message.content
            yield content.encode('utf-8')
            yield " ".encode('utf-8')
            
            # Extract detailed usage data from the response
            try:
                usage_data = {
                    'completion_tokens': response.usage.completion_tokens,
                    'prompt_tokens': response.usage.prompt_tokens,
                    'total_tokens': response.usage.total_tokens
                }
                
                # Add detailed token information if available
                if hasattr(response.usage, 'completion_tokens_details'):
                    usage_data['completion_tokens_details'] = {
                        'reasoning_tokens': getattr(response.usage.completion_tokens_details, 'reasoning_tokens', 0)
                    }
                
                # Add content filter results if available
                if hasattr(response.choices[0], 'content_filter_results'):
                    usage_data['content_filter_results'] = response.choices[0].content_filter_results
                
                yield f"###STOP###{json.dumps(usage_data)}".encode('utf-8')
            except Exception as e:
                print(f"Error extracting usage data: {e}")
                yield "###STOP###null".encode('utf-8')
        else:
            # Use streaming for non-O1 models
            response = client.chat.completions.create(
                model=model['model'],
                messages=messages,
                stream=True
            )
            
            accumulated_text = ""
            citations = []
            usage_data = {}
            
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
                        # Try to get data from model_dump or fallback to dictionary
                        try:
                            response_data = line.model_dump()
                            if 'citations' in response_data:
                                citations = response_data['citations']
                        except AttributeError:
                            # If model_dump is not available, build usage data from what we've collected
                            response_data = {}
                        
                        # Build the final usage data
                        final_usage_data = {}
                        
                        # Traditional usage info
                        if hasattr(line, 'usage'):
                            try:
                                usage_info = line.usage.model_dump()
                                final_usage_data.update(usage_info)
                            except AttributeError:
                                # Fallback for when model_dump is not available
                                if hasattr(line.usage, 'completion_tokens'):
                                    final_usage_data['completion_tokens'] = line.usage.completion_tokens
                                if hasattr(line.usage, 'prompt_tokens'):
                                    final_usage_data['prompt_tokens'] = line.usage.prompt_tokens
                                if hasattr(line.usage, 'total_tokens'):
                                    final_usage_data['total_tokens'] = line.usage.total_tokens
                        
                        # Add citations if found
                        if citations:
                            final_usage_data['citations'] = citations
                            
                        yield f"###STOP###{json.dumps(final_usage_data)}".encode('utf-8')
                    except Exception as e:
                        print(f"Error in final response processing: {e}")
                        yield "###STOP###null".encode('utf-8')

def prepare_messages_for_o1(messages):
    """
    Prepares messages for O1 models which don't support system messages.
    Converts any system message to a user message or prepends it to the first user message.
    """
    prepared_messages = []
    system_content = None
    
    # Extract system message if present
    for msg in messages:
        if msg['role'] == 'system':
            system_content = msg['content']
        else:
            prepared_messages.append(msg)
    
    # If there was a system message, prepend it to the first user message
    if system_content and prepared_messages:
        for i, msg in enumerate(prepared_messages):
            if msg['role'] == 'user':
                # Prepend system content to the first user message
                prepared_messages[i]['content'] = f"System: {system_content}\n\nUser: {msg['content']}"
                break
    
    # If no user message was found but we have a system message, convert system to user
    if system_content and not prepared_messages:
        prepared_messages.append({
            'role': 'user',
            'content': f"System: {system_content}\n\nRespond to this system instruction."
        })
    
    return prepared_messages

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
        elif model['provider']=='perplexity':
            client = OpenAI(api_key=perplexity_api_key,base_url='https://api.perplexity.ai')
        elif model['provider']=='openai':
            client = OpenAI(api_key=openai_api_key)
        elif model['provider']=='azure':
            client = AzureOpenAI(azure_endpoint=azure_endpoint,api_key=azure_api_key,api_version=azure_api_version)

        # Check if the model is an O1 model and handle system messages
        is_o1_model = model['model'].startswith('o1-')
        if is_o1_model:
            prepared_messages = prepare_messages_for_o1(messages)
            response = client.chat.completions.create(
                model=model['model'],
                messages=prepared_messages,
                stream=False
            )
        else:
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