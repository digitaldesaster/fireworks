from dotenv import load_dotenv
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ai_llm_helper import llm_call
from core.db_document import History, Prompt, File, Model, Example, User

messages = [
    {"role": "system", "content": "Du bist ein hilfreicher Assistent"},
    {"role": "user", "content": "Hallo"}
]

model = {'provider': 'deepseek', 'model': 'deepseek-chat', 'name': 'deepseek-chat'}

#response = llm_call(messages, model, stream=False)
#print(response)

# History.objects().delete()
# Prompt.objects().delete()
# File.objects().delete()

user = User.objects(email='alexander.fillips@gmail.com').first()
user.role = 'admin'
user.save()