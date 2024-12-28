import os
import subprocess
import json
import sys

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error message: {e}")
        sys.exit(1)

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def main():
    # Install Flask
    run_command('pip3 install flask')

    # Install Tailwind CSS
    run_command('npm install -D tailwindcss')

    # Initialize Tailwind CSS
    run_command('npx tailwindcss init')

    # Create directories
    create_directory('static/src')
    create_directory('static/css')
    create_directory('templates')
    create_directory('.vscode')

    # Create files
    create_file('tailwind.config.js', '''
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [],
};
''')

    create_file('static/src/input.css', '''
@tailwind base;
@tailwind components;
@tailwind utilities;
''')

    create_file('package.json', json.dumps({
        "devDependencies": {
            "tailwindcss": "^3.4.10",
            "browser-sync": "^2.29.3"
        },
        "scripts": {
            "build:css": "npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --minify",
            "watch:css": "npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --minify --watch"
        },
        "dependencies": {
            "@tailwindcss/typography": "^0.5.15",
            "prettier": "^3.3.3",
            "prettier-plugin-tailwindcss": "^0.6.6"
        }
    }, indent=2))

    create_file('main.py', '''
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
''')

    create_file('templates/index.html', '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Flask App</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/output.css') }}"
    />
  </head>
  <body class="flex items-center justify-center h-screen">
    <div class="container mx-auto">
      <h1 class="text-3xl font-bold text-center">Hello World</h1>
      <!-- Add your content here -->
    </div>
  </body>
</html>
''')

    create_file('.prettierrc.json', '{}')

    create_file('.vscode/tasks.json', json.dumps({
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Start Flask",
                "type": "shell",
                "command": ".venv/bin/python main.py",
                "isBackground": True,
                "problemMatcher": []
            },
            {
                "label": "Watch CSS with TailwindCSS",
                "type": "shell",
                "command": "npx tailwindcss -i static/src/input.css -o static/css/output.css --minify --watch",
                "isBackground": True,
                "problemMatcher": []
            },
            {
                "label": "Start Browser-Sync",
                "type": "shell",
                "command": "npx browser-sync start --no-notify --proxy '127.0.0.1:5000' --files 'static/src/*.css, templates/*.html' --delay 300",
                "isBackground": True,
                "problemMatcher": []
            },
            {
                "label": "Start All",
                "dependsOn": [
                    "Start Flask",
                    "Watch CSS with TailwindCSS",
                    "Start Browser-Sync"
                ],
                "problemMatcher": [],
                "group": {
                    "kind": "build",
                    "isDefault": True
                }
            }
        ]
    }, indent=2))

    # Install project dependencies
    run_command('npm install')

    # Build CSS
    run_command('npm run build:css')

    print("Setup complete! Your Flask app with Tailwind CSS is ready.")
    print("To run your app:")
    print("1. Activate the virtual environment: source .venv/bin/activate")
    print("2. Run Flask: python main.py")
    print("3. In a separate terminal, run: npm run watch:css")
    print("4. In another terminal, run: npx browser-sync start --no-notify --proxy '127.0.0.1:5000' --files 'static/src/*.css, templates/*.html' --delay 300")

if __name__ == "__main__":
    main()