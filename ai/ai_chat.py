#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, render_template, Response
import time, sys, json
from flask_wtf.csrf import CSRFProtect

# Append the db directory to the system path for module imports
sys.path.append('db')

from core.helper import handleDocument, prepare_context_from_files
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
def chat(prompt_id=None, history_id=None):
    config = getConfig()

    config['username'] = "alexander.fillips@gmail.com"
    config['chat_started'] = int(time.time())
    config['history'] = []
    config['latest_prompts'] = []

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
        #    prompt['system_message'] = context['data']
        config['messages'] = []
        config['messages'].append({
            'role': 'system',
            'content': prompt['system_message']
        })
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
def save_chat():
    username = request.form.get('username')
    chat_started = request.form.get('chat_started')
    messages = request.form.get('messages')

    chat_history = History.objects(username=username,
                                   chat_started=chat_started)
    if len(chat_history) == 1:
        chat_history = chat_history[0]
        chat_history.messages = messages
        chat_history.save()
        return 'Chat aktualisiert!'
    else:
        chat_history = History()
        chat_history.username = username
        chat_history.chat_started = chat_started
        chat_history.messages = messages
        chat_history.first_message = json.loads(messages)[1]['content']
        chat_history.save()
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
