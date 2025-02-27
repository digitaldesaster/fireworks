from flask import Flask, render_template, request, session, jsonify, send_from_directory, abort, flash, redirect, url_for
from core import auth
from datetime import timedelta, datetime
import os
from flask_login import LoginManager, current_user, login_required
from core.db_user import User
from flask_wtf.csrf import CSRFProtect
import json
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

# Import functions from helper.py and db_helper.py
from core.helper import getList, handleDocument, deleteDocument, upload_file
from core.db_helper import getFile
from core.db_document import File, Prompt, getDefaults

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Add format_time_ago filter
@app.template_filter('format_time_ago')
def format_time_ago(date):
	if not date:
		return ""
	
	now = datetime.now()
	diff = now - date
	
	minutes = diff.total_seconds() / 60
	hours = minutes / 60
	days = diff.days
	
	if minutes < 1:
		return "just now"
	elif minutes < 60:
		return f"{int(minutes)}m ago"
	elif hours < 24:
		return f"{int(hours)}h ago"
	elif days == 1:
		return "yesterday"
	elif days < 7:
		return f"{days}d ago"
	else:
		return date.strftime('%d.%m.%Y')

# Import and register the chat blueprint
from ai.ai_chat import dms_chat
app.register_blueprint(dms_chat, url_prefix='/chat')

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
	try:
		return User.objects(id=user_id).first()
	except:
		return None

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
	# Add special handling for history documents
	if name == 'history' and id:
		# Get the history document
		default = getDefaults('history')
		if default:
			try:
				doc = default.collection.objects(_id=ObjectId(id)).first()
				if not doc or doc.user_id != str(current_user.id):
					flash('Access denied. You can only view your own history.', 'error')
					return redirect(url_for('list', collection='history'))
			except Exception as e:
				print(f"[DEBUG] Error accessing history document: {str(e)}")
				flash('Error accessing history document', 'error')
				return redirect(url_for('list', collection='history'))

	if return_format == 'json':
		result = handleDocument(name, id, request, return_json=True)
		# Ensure we're returning valid JSON
		if isinstance(result, str):
			return result
		return jsonify(result)
	else:
		return handleDocument(name, id, request)

# Route to delete a document
@app.route('/document/delete')
@login_required
def delete_document():
	print(f"[DEBUG] Delete request received with args: {request.args}")
	result = deleteDocument(request)
	print(f"[DEBUG] Delete result: {result}")
	return jsonify(result)

# Route to return a list of documents
@app.route('/list/<collection>')
@login_required
def list(collection):
	mode = request.args.get('mode')
	
	# Handle special collections
	if collection == 'history':
		# History is always filtered by current user
		return getList('history', request, return_json=(mode == 'json'))
	elif collection in ['user', 'users']:
		if not current_user.is_admin:
			flash('Access denied. Only administrators can view the user list.', 'error')
			return redirect(url_for('index'))
		return getList('user', request, return_json=(mode == 'json'))
		
	return getList(collection, request, return_json=(mode == 'json'))

# Route to download a file
@app.route('/download_file/<file_id>')
@login_required
def download_file(file_id):
	try:
		data = getFile(file_id)
		if data['status'] == 'ok':
			file_data = json.loads(data['data'])
			file_obj = File.objects(id=file_id).first()
			
			# Check if user has permission to access this file
			if not file_obj.can_access(current_user):
				flash('Access denied. You can only access your own files.', 'error')
				return redirect(url_for('index'))
				
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

@app.route('/d/<collection>/<id>')
@login_required
def view_document(collection, id):
	if collection == 'user':
		if not current_user.can_view_user(id):
			flash('Access denied. You can only view your own profile.', 'error')
			return redirect(url_for('list', collection='user'))
	return handleDocument(collection, id, request)

if __name__ == '__main__':
	app.run(debug=True)

