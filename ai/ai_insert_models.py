#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_document import Model
from core.db_connect import *

models = [
  {'provider':'openai','model':'gpt-4o','name':'gpt-4o'},
  {'provider':'openai','model':'gpt-4o-mini','name':'gpt-4o-mini'},
  # {'provider':'openai','model':'gpt-4-turbo-preview','name':'gpt-4-turbo'},
  # {'provider':'together','model':'meta-llama/Llama-2-70b-chat-hf','name':'meta-llama-2-70b'},
  # {'provider':'anthropic','model':'claude-3-haiku-20240307','name':'claude-3-haiku'},
  # {'provider':'anthropic','model':'claude-3-opus-20240229','name':'claude-3-opus'},
  #  {'provider':'anthropic','model':'claude-3-5-sonnet-20240620','name':'claude-3.5-sonnet'},
  #  {'provider':'deepseek','model':'deepseek-chat','name':'deepseek-chat'},
   {'provider':'perplexity','model':'llama-3.1-sonar-large-128k-online','name':'perplexity-llama-3.1-online'},
  ]

# Delete existing models
Model.objects.delete()

# Current timestamp for creation date
now = datetime.datetime.now()

# Insert models with only creation audit fields
for model_data in models:
    model = Model(
        provider=model_data['provider'],
        model=model_data['model'],
        name=model_data['name'],
        created_date=now,
        created_by='system'
    )
    # Use save(force_insert=True) to ensure it's treated as a new document
    model.save(force_insert=True)

print("Models inserted successfully with creation audit fields.")
