import sys
import os

# Add your project directory to Python path
sys.path.insert(0, '/var/www/tests_alex/fireworks')
sys.path.insert(0, '/var/www/tests_alex/fireworks/core')

# Set environment variables if needed
from dotenv import load_dotenv
project_folder = os.path.expanduser('/var/www/tests_alex/fireworks')
load_dotenv(os.path.join(project_folder, '.env'))

# Import the Flask application
from app import app as application