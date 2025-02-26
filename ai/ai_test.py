from dotenv import load_dotenv
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ai_llm_helper import llm_call
from core.db_document import History, Prompt, File, Model, Example, User

messages = [
    {"role": "system", "content": "Du bist ein hilfreicher Assistent"},
    {"role": "user", "content": "Wann spielt der FC Bayern?"}
]

#model = {'provider':'azure','model':'gpt-4o-sweden-02','name':'gpt-4o-sweden-02'}
#model = {'provider':'openai','model':'gpt-4o-mini','name':'gpt-4o-mini'}
model = {'provider':'perplexity','model':'sonar-pro','name':'Perplexity - Sonar Reasoning Pro'}
#model = {'provider':'anthropic','model':'claude-3-5-sonnet-20240620','name':'claude-3.5-sonnet'}

#Stream response handling
response = llm_call(messages, model, stream=True)
for chunk in response:
    print(chunk)

# History.objects().delete()
# Prompt.objects().delete()
# File.objects().delete()

# user = User.objects(email='').first()
# user.role = 'admin'
# user.save()