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

    config['username'] = current_user.email
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
        config['username'] = history['username']
        config['messages'] = json.loads(history['messages'])
    else:
        chat_history = History.objects().order_by('-id').limit(3)
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
    username = request.form.get('username')
    chat_started = request.form.get('chat_started')
    messages = request.form.get('messages')
    
    print(f"[DEBUG] Saving chat for user {username} started at {chat_started}")
    print(f"[DEBUG] Messages to save: {messages}")

    chat_history = History.objects(username=username,
                                   chat_started=chat_started)
    print(f"[DEBUG] Found {len(chat_history)} existing chat(s)")
    
    if len(chat_history) == 1:
        print("[DEBUG] Updating existing chat")
        chat_history = chat_history[0]
        chat_history.messages = messages
        file_ids = []
        for msg in json.loads(messages):
            if 'attachments' in msg:
                for attachment in msg['attachments']:
                    file_ids.append(attachment['id'])
        chat_history.file_ids = file_ids
        chat_history.save()
        return 'Chat aktualisiert!'
    else:
        print("[DEBUG] Creating new chat")
        chat_history = History()
        chat_history.username = username
        chat_history.chat_started = chat_started
        chat_history.messages = messages
        
        # Parse messages once
        parsed_messages = json.loads(messages)
        
        # First try to find a user message
        first_message_found = False
        for msg in parsed_messages:
            # Only look for actual user messages, not system or file context messages
            if msg.get('role') == 'user' and isinstance(msg.get('content'), str) and not msg.get('isFileContext'):
                chat_history.first_message = msg['content']
                first_message_found = True
                print(f"[DEBUG] Found user message as first message: {msg['content']}")
                break
                
        # If no user message found, then fall back to file upload
        if not first_message_found:
            # Look for the first system message with attachments
            for msg in parsed_messages:
                if msg.get('role') == 'system' and msg.get('attachments'):
                    for attachment in msg['attachments']:
                        if attachment.get('name'):
                            chat_history.first_message = f"File uploaded: {attachment['name']}"
                            print(f"[DEBUG] Using file upload as first message: {chat_history.first_message}")
                            break
                    if chat_history.first_message:
                        break
        
        # Collect file IDs from all messages
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
    history = History.objects(username=current_user.email).order_by('-modified_date', '-id').limit(15)
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
        
        # Delete all history documents for the current user
        histories = History.objects(username=current_user.email)
        print(f"[DEBUG] Found {histories.count()} history documents for user {current_user.email}")
        deleted_count = 0
        failed_count = 0
        
        for history in histories:
            print(f"[DEBUG] Processing history document: {history.id}")
            print(f"[DEBUG] File IDs to delete: {history.file_ids}")
            
            for file_id in history.file_ids:
                print(f"[DEBUG] Processing file ID: {file_id}")
                file_doc = File.objects(id=file_id).first()
                
                if file_doc:
                    print(f"[DEBUG] Found file document: {file_doc.to_json()}")
                    try:
                        # Construct absolute path using the relative path stored in DB
                        file_path = os.path.join(base_path, file_doc.path, f"{str(file_id)}.{file_doc.file_type}")
                        print(f"[DEBUG] Full file path for deletion: {file_path}")
                        
                        # Try to delete the file from disk
                        if os.path.exists(file_path):
                            print(f"[DEBUG] File exists at {file_path}, attempting deletion")
                            try:
                                os.remove(file_path)
                                print(f"[DEBUG] Successfully deleted file from disk: {file_path}")
                            except Exception as e:
                                print(f"[DEBUG] Error deleting file from disk: {str(e)}")
                                failed_count += 1
                        else:
                            print(f"[DEBUG] File not found on disk at {file_path}")
                        
                        # Always try to delete the database record
                        try:
                            file_doc.delete()
                            print(f"[DEBUG] Successfully deleted file document from database")
                            deleted_count += 1
                        except Exception as e:
                            print(f"[DEBUG] Error deleting file document from database: {str(e)}")
                            failed_count += 1
                            
                    except Exception as e:
                        print(f"[DEBUG] Error processing file {file_id}: {str(e)}")
                        failed_count += 1
                else:
                    print(f"[DEBUG] No file document found for ID: {file_id}")
        
        # Delete all history documents after handling files
        try:
            result = histories.delete()
            print(f"[DEBUG] Deleted {result} history documents")
        except Exception as e:
            print(f"[DEBUG] Error deleting history documents: {str(e)}")
            raise
        
        status_message = f'Successfully deleted {deleted_count} files'
        if failed_count > 0:
            status_message += f' ({failed_count} deletions failed)'
        status_message += f' and {result} history documents'
        
        return jsonify({
            'status': 'success',
            'message': status_message,
            'deleted_files': deleted_count,
            'failed_deletions': failed_count,
            'deleted_histories': result
        })
    except Exception as e:
        print(f"[DEBUG] Top-level error in delete_all_history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
