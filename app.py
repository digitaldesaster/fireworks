from flask import Flask, render_template, request, session, jsonify, send_from_directory, abort
from core import auth
from datetime import timedelta
import os
from flask_login import LoginManager, current_user, login_required
from core.db_user import User
from flask_wtf.csrf import CSRFProtect
import json

# Import functions from helper.py and db_helper.py
from core.helper import getList, handleDocument, deleteDocument
from core.db_helper import getFile

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialize Flask-Login with proper session durations
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # For "Remember me"
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)    # For "Remember me"
app.config['REMEMBER_COOKIE_SECURE'] = False                   # Set to True in production with HTTPS
app.config['REMEMBER_COOKIE_HTTPONLY'] = True                  # No JavaScript access

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return User.objects(email=user_id).first()

@app.route('/register', methods=['GET', 'POST'])
def register():
	return auth.do_register(request)

@app.route('/login', methods=['GET', 'POST'])
def login():
	return auth.do_login(request)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	return auth.do_logout()

# Route for the home page
@app.route("/")
@app.route("/index")
@login_required
def index():
	return render_template("index.html")

# Route to handle and update a document
@app.route('/d/<name>', methods=['POST', 'GET'])
@app.route('/d/<name>/<id>', methods=['POST', 'GET'])
@app.route('/d/<name>/<id>/<return_format>', methods=['POST', 'GET'])
@login_required
def doc(name, id='', return_format='html'):
	if return_format == 'json':
		return handleDocument(name, id,request, return_json=True)
	else:
		return handleDocument(name, id,request)

# Route to delete a document
@app.route('/document/delete')
@login_required
def delete_document():
	print(f"[DEBUG] Delete request received with args: {request.args}")
	result = deleteDocument(request)
	print(f"[DEBUG] Delete result: {result}")
	return jsonify(result)

# Route to return a list of documents
@app.route('/list/<name>')
@login_required
def list(name):
	# Check if JSON mode is requested via query parameter
	mode = request.args.get('mode')
	if mode == 'json':
		return getList(name, request, return_json=True)
	return getList(name, request)

# Route to download a file
@app.route('/download_file/<file_id>')
@login_required
def download_file(file_id):
	try:
		data = getFile(file_id)
		if data['status'] == 'ok':
			file_data = json.loads(data['data'])
			path = file_data['path']
			filename = f"{file_id}.{file_data['file_type'].lower()}"
			original_filename = file_data['name']
			
			print(f"[DEBUG] Attempting to send file: {path}/{filename}")
			return send_from_directory(
				path, 
				filename,
				as_attachment=True,
				download_name=original_filename
			)
		else:
			print(f"[DEBUG] File not found: {file_id}")
			abort(404)
	except Exception as e:
		print(f"[DEBUG] Error in download_file: {str(e)}")
		abort(500)

if __name__ == '__main__':
	app.run(debug=True)
