import sys
import json
sys.path.append('/var/www/tests_alex/chroma_testing')
sys.path.append('/var/www/tests_alex/fireworks/ai')

from chroma_search import search_collection
from prompt_builder import get_prompt
from ai_llm_helper import llm_call


model = {'provider':'azure','model':'gpt-4o-mini-sweden-02','name':'EU - Azure - GPT-4o Mini - Sweden', 'region':'EU','model_family':'gpt4o'}
#model = {'provider':'azure','model':'gpt-4o-sweden-02','name':'EU - Azure - GPT-4o - Sweden', 'region':'EU','model_family':'gpt4o'}
#model = {'provider':'azure','model':'o1-mini','name':'EU Azure - o1-mini Sweden', 'region':'EU','model_family':'o1'}
#model = {'provider':'perplexity','model':'sonar-deep-research','name':'US - Perplexity - Sonar Deep Research', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar-reasoning-pro','name':'US - Perplexity - Sonar Reasoning Pro', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar-reasoning','name':'US - Perplexity - Sonar Reasoning', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar-pro','name':'US - Perplexity - Sonar Pro', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'sonar','name':'US - Perplexity - Sonar', 'region':'US','model_family':'sonar'}
#model = {'provider':'perplexity','model':'r1-1776','name':'US - Perplexity - DeepSeek R1', 'region':'US','model_family':'deepseek'}



#question = 'Kann ADAudit Plus mir dabei helfen, Änderungen an Active Directory-Objekten zu überwachen?'

# for result in search_collection(question)['results']:
#     print (result)

#print (get_prompt(question))

question="Mit welchem Produkt kann ich Sox-Compliance einhalten?"

data = json.loads(get_prompt(question))

#print (data['messages'])

response = llm_call(data['messages'], model,stream=False)
print (response)



