#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, render_template, Response, jsonify
import time, sys, json
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user

# Append the db directory to the system path for module imports
sys.path.append('db')

from core.helper import handleDocument, prepare_context_from_files, upload_file
from core.db_document import File, History, Model, Prompt

from core.db_connect import *

from ai.ai_llm_helper import llm_call

# Import the getConfig function from db_chat.py
#from db.db_chat import getConfig

# Create a Blueprint for the chat functionality
dms_chat = Blueprint('dms_chat', __name__)

# Initialize CSRF protection for the blueprint
csrf = CSRFProtect()


def getConfig():
    system_message = "Du bist ein hilfreicher Assistent! Antworte immer auf Deutsch! Wenn du Code generierst dann setze den Code in backticks"
    welcome_message = "Hallo wie kann ich helfen?"
    messages = []
    models = json.loads(Model.objects().to_json())
    print (models)

    return {
        "system_message": system_message,
        "welcome_message": welcome_message,
        'messages': messages,
        'models': models,
        'use_prompt_template': 'False'
    }


# Define the chat route
@dms_chat.route('/prompt/<prompt_id>')
@dms_chat.route('/history/<history_id>')
@dms_chat.route('/', methods=['GET', 'POST'])
@login_required
def chat(prompt_id=None, history_id=None):
    config = getConfig()

    # Add user information to config
    config['username'] = current_user.email
    config['user_id'] = str(current_user.id)
    config['is_admin'] = current_user.is_admin

    config['chat_started'] = int(time.time())
    config['history'] = []
    config['latest_prompts'] = []
    config['using_context'] = False
    config['context_files'] = []
    config['file_ids'] = []

    if prompt_id:
        prompt = json.loads(
            handleDocument('prompt', prompt_id, request, return_json=True))
        files = json.loads(File.objects(document_id=prompt['id']).to_json())
        
        #only pdf/txt files are supported for now
        context = prepare_context_from_files(files)
        if context['status'] == "ok":
            if prompt['system_message'].find("{context}") != -1:
                prompt['system_message'] = prompt['system_message'].replace(
                    "{context}", context['data'])
                config['using_context'] = True
                config['context_files'] = [f['name'] for f in files]
                config['file_ids'] = [f['_id']['$oid'] for f in files]

        config['messages'] = []
        
        # Add system message with file attachments if files exist
        system_message = {
            'role': 'system',
            'content': prompt['system_message']
        }
        if files:
            system_message['attachments'] = [{
                'type': 'file',
                'id': f['_id']['$oid'],
                'name': f['name'],
                'file_type': f['file_type'],
                'timestamp': int(time.time())
            } for f in files]
        config['messages'].append(system_message)
        
        # Add user prompt message
        config['messages'].append({
            'role': 'user',
            'content': prompt['prompt']
        })
        
        config['use_prompt_template'] = 'True'
        config['welcome_message'] = prompt['welcome_message']

    elif history_id:
        history = json.loads(
            handleDocument('history', history_id, request, return_json=True))
        config['chat_started'] = history['chat_started']
        config['messages'] = json.loads(history['messages'])
    else:
        chat_history = History.objects(user_id=str(current_user.id)).order_by('-id').limit(3)
        if chat_history:
            config['history'] = chat_history
        latest_prompts = Prompt.objects().order_by('-id').limit(3)
        if latest_prompts:
            config['latest_prompts'] = latest_prompts

    return render_template('/chat/chat.html', config=config)


@dms_chat.route('/stream', methods=['POST'])
def stream():
    data = request.get_json()
    response_stream = llm_call(data['messages'], data['model'])
    return Response(response_stream, mimetype='text/event-stream')


@dms_chat.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    chat_started = request.form.get('chat_started')
    messages = request.form.get('messages')
    
    print(f"[DEBUG] Saving chat for user {current_user.id} started at {chat_started}")
    print(f"[DEBUG] Messages to save: {messages}")

    chat_history = History.objects(user_id=str(current_user.id),
                                 chat_started=chat_started)
    print(f"[DEBUG] Found {len(chat_history)} existing chat(s)")
    
    if len(chat_history) == 1:
        print("[DEBUG] Updating existing chat")
        chat_history = chat_history[0]
        chat_history.messages = messages
        
        # Parse messages once
        parsed_messages = json.loads(messages)
        
        # Update first message if we find a user message and current first message is default
        if chat_history.first_message == "Neuer Chat":
            for msg in parsed_messages:
                if msg.get('role') == 'user' and isinstance(msg.get('content'), str):
                    chat_history.first_message = msg['content']
                    print(f"[DEBUG] Updated first message to: {msg['content']}")
                    break
        
        # Collect file IDs
        file_ids = []
        for msg in parsed_messages:
            if 'attachments' in msg:
                for attachment in msg['attachments']:
                    file_ids.append(attachment['id'])
        chat_history.file_ids = file_ids
        chat_history.save()
        return 'Chat aktualisiert!'
    else:
        print("[DEBUG] Creating new chat")
        chat_history = History()
        chat_history.user_id = str(current_user.id)
        chat_history.chat_started = chat_started
        chat_history.messages = messages
        chat_history.first_message = "Neuer Chat"  # Set default title
        
        # Parse messages once
        parsed_messages = json.loads(messages)
        
        # Set first message to first user message if one exists
        for msg in parsed_messages:
            if msg.get('role') == 'user' and isinstance(msg.get('content'), str):
                chat_history.first_message = msg['content']
                print(f"[DEBUG] Set first message to: {msg['content']}")
                break
        
        # Collect file IDs
        file_ids = []
        for msg in parsed_messages:
            if 'attachments' in msg:
                for attachment in msg['attachments']:
                    file_ids.append(attachment['id'])
        chat_history.file_ids = file_ids
        
        chat_history.save()
        print(f"[DEBUG] New chat created with first message: {chat_history.first_message}")
        return 'Neuer Chat erstellt!'


# @dms_chat.route('/chat/list_chat_history', methods=['GET'])
# def list_chat_history_endpoint():
#     chat_history = list_chat_history()
#     print(chat_history)
#     return render_template('/chat/chat_history.html',
#                            chat_history=chat_history)


@dms_chat.route('/load_ui/<template>')
def load_ui(template):
    return render_template(template)

@dms_chat.route('/upload', methods=['POST'])
@login_required
def upload_chat_file():
    try:
        if 'file' not in request.files:
            print("[DEBUG] No file part in request")
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            print("[DEBUG] No file selected")
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
            
        print(f"[DEBUG] Processing upload for file: {file.filename}")
        result = upload_file(file)
        print(f"[DEBUG] Upload result: {result}")
        
        if result.get('status') == 'ok':
            # Add file metadata to the response
            result['attachment'] = {
                'type': 'file',
                'id': result['file_id'],
                'name': result['filename'],  # Use filename from response
                'file_type': result['file_type'],  # Use file_type from response
                'timestamp': int(time.time())
            }
            print(f"[DEBUG] Returning successful response: {result}")
            return jsonify(result)
        else:
            print(f"[DEBUG] Upload failed: {result.get('message', 'Unknown error')}")
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        return jsonify({'status': 'error', 'message': error_msg}), 500

@dms_chat.route('/nav_items', methods=['GET'])
def get_nav_items():
    # Get latest history items for current user only, ordered by last modified date
    history = History.objects(user_id=str(current_user.id)).order_by('-modified_date', '-id').limit(15)
    # Get latest prompts
    prompts = Prompt.objects().order_by('-id').limit(5)
    
    return jsonify({
        'history': json.loads(history.to_json()),
        'prompts': json.loads(prompts.to_json())
    })

@dms_chat.route('/delete_all_history', methods=['POST'])
@login_required
def delete_all_history():
    try:
        # Get base path for constructing absolute paths
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        print(f"[DEBUG] Base path for deletion: {base_path}")
        
        # Get all prompts' file IDs to preserve them
        all_prompts = Prompt.objects()
        preserved_file_ids = set()
        for prompt in all_prompts:
            # Get files associated with this prompt
            prompt_files = File.objects(document_id=str(prompt.id))
            for file in prompt_files:
                preserved_file_ids.add(str(file.id))
        print(f"[DEBUG] Found {len(preserved_file_ids)} files to preserve from prompts")
        
        # Delete all history documents for the current user
        histories = History.objects(user_id=str(current_user.id))
        print(f"[DEBUG] Found {histories.count()} history documents for user {current_user.id}")
        deleted_count = 0
        failed_count = 0
        preserved_count = 0
        
        for history in histories:
            try:
                print(f"[DEBUG] Processing history document: {history.id}")
                print(f"[DEBUG] File IDs to process: {history.file_ids}")
                
                # Process associated files first
                for file_id in history.file_ids:
                    try:
                        # Skip if file is used by a prompt
                        if file_id in preserved_file_ids:
                            print(f"[DEBUG] Preserving file {file_id} as it's used by a prompt")
                            preserved_count += 1
                            continue
                            
                        file_doc = File.objects(id=file_id).first()
                        if file_doc:
                            # Check if user has permission to delete this file
                            if not file_doc.can_access(current_user):
                                print(f"[DEBUG] Access denied for file deletion: {file_id}")
                                continue
                                
                            # Construct absolute path using the relative path stored in DB
                            file_path = os.path.join(base_path, file_doc.path, f"{str(file_id)}.{file_doc.file_type}")
                            print(f"[DEBUG] Attempting to delete file: {file_path}")
                            
                            # Delete file from disk if it exists
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"[DEBUG] Successfully deleted file from disk: {file_path}")
                            
                            # Delete file document from database
                            file_doc.delete()
                            print(f"[DEBUG] Successfully deleted file document from database: {file_id}")
                    except Exception as e:
                        print(f"[DEBUG] Error deleting file {file_id}: {str(e)}")
                        failed_count += 1
                
                # Delete the history document
                history.delete()
                deleted_count += 1
                print(f"[DEBUG] Successfully deleted history: {history.id}")
                
            except Exception as e:
                print(f"[DEBUG] Error processing history {history.id}: {str(e)}")
                failed_count += 1
                continue
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully deleted {deleted_count} history documents. Preserved {preserved_count} prompt files. Failed to delete {failed_count} items.',
            'deleted_count': deleted_count,
            'preserved_count': preserved_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        print(f"[DEBUG] Error in delete_all_history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error deleting history: {str(e)}'
        }), 500
