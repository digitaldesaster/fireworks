from dotenv import load_dotenv
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ai_llm_helper import llm_call
from core.db_document import History, Prompt, File, Model, Example, User

messages = [
    {"role": "system", "content": "Du bist ein Experte für Geschichte. Antworte immer in deutscher Sprache."},
    {"role": "user", "content": "Wer war Ada Lovelace?"}
]

# for model in Model.objects():
#     print (model.to_json())

#model = {'provider':'azure','model':'gpt-4o-mini-sweden-02','name':'EU - Azure - GPT-4o Mini - Sweden', 'region':'EU','model_family':'gpt4o'}
#model = {'provider':'azure','model':'gpt-4o-sweden-02','name':'EU - Azure - GPT-4o - Sweden', 'region':'EU','model_family':'gpt4o'}
#model = {'provider':'azure','model':'o1-mini','name':'EU Azure - o1-mini Sweden', 'region':'EU','model_family':'o1'}
#model = {'provider':'perplexity','model':'sonar-deep-research','name':'US - Perplexity - Sonar Deep Research', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar-reasoning-pro','name':'US - Perplexity - Sonar Reasoning Pro', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar-reasoning','name':'US - Perplexity - Sonar Reasoning', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar-pro','name':'US - Perplexity - Sonar Pro', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar','name':'US - Perplexity - Sonar', 'region':'US','model_family':'sonar'}
model = {'provider':'perplexity','model':'r1-1776','name':'US - Perplexity - DeepSeek R1', 'region':'US','model_family':'deepseek'}

#Stream response handling
response = llm_call(messages, model)
for chunk in response:
    print(chunk)

# History.objects().delete()
# Prompt.objects().delete()
# File.objects().delete()

# user = User.objects(email='').first()
# user.role = 'admin'
# user.save()