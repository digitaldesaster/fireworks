from flask import Flask, render_template, request, session
from core import auth
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '5765765ASDFHR746gDHEdjhkkjhe'  # Change this to a secure secret key

# Set session timeout to 60,000 minutes (about 41 days)
@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=60000)

@app.before_request
@auth.login_required
def check_auth():
	pass

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

def index():
	return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
