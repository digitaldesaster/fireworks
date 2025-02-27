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
  # {'provider':'openai','model':'gpt-4o','name':'OpenAI - GPT-4o'},
  # {'provider':'openai','model':'gpt-4o-mini','name':'OpenAI - GPT-4o Mini'},
  {'provider':'perplexity','model':'sonar-deep-research','name':'US - Perplexity - Sonar Deep Research'},
  {'provider':'perplexity','model':'sonar-reasoning-pro','name':'US - Perplexity - Sonar Reasoning Pro'},
  {'provider':'perplexity','model':'sonar-reasoning','name':'US - Perplexity - Sonar Reasoning'},
  {'provider':'perplexity','model':'sonar-pro','name':'US - Perplexity - Sonar Pro'},
  {'provider':'perplexity','model':'sonar','name':'US - Perplexity - Sonar'},
  {'provider':'perplexity','model':'r1-1776','name':'US - Perplexity - DeepSeek R1'},
  {'provider':'azure','model':'gpt-4o-sweden-02','name':'EU - Azure - GPT-4o - Sweden'},
  {'provider':'azure','model':'gpt-4o-mini-sweden-02','name':'EU - Azure - GPT-4o Mini - Sweden'},
  # {'provider':'azure','model':'o1-mini','name':'EU Azure - o1-mini Sweden'},
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
