# Flask App with Tailwind CSS

This guide will walk you through setting up a Flask application integrated with Tailwind CSS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Set Up Your Project Directory](#1-set-up-your-project-directory)
3. [Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
4. [Install Flask](#3-install-flask)
5. [Install Tailwind CSS](#4-install-tailwind-css)
6. [Initialize and Configure Tailwind CSS](#5-initialize-and-configure-tailwind-css)
7. [Set Up Input CSS](#6-set-up-input-css)
8. [Install Prettier](#7-install-prettier)
9. [Install Tailwind Typography](#8-install-tailwind-typography)
10. [Create and Configure package.json](#9-create-and-configure-packagejson)
11. [Create Your Flask Application](#10-create-your-flask-application)
12. [Create HTML Template](#11-create-html-template)
13. [Compile Tailwind CSS](#12-compile-tailwind-css)
14. [Create Prettier Configuration](#13-create-prettier-configuration)
15. [Install and Run Browser-Sync](#14-install-and-run-browser-sync)
16. [Configure Visual Studio Code Tasks](#14-configure-visual-studio-code-tasks)
17. [Run Your Flask Application](#14-run-your-flask-application)

## Prerequisites

Ensure you have the following installed:

- Python 3.10+
- pip
- npm

## Step-by-Step Installation

### 1. Set Up Your Project Directory

Create a new directory for your Flask project and navigate into it:

```bash
mkdir flask_app
cd flask_app
```

### 2. Create and Activate a Virtual Environment

Create and activate the virtual environment:

- **macOS and Linux:**

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

### 3. Install Flask

Install Flask within the virtual environment:

```bash
pip3 install flask
```

### 4. Install Tailwind CSS

Run the following command to install the project dependencies:

```bash
npm install -D tailwindcss
```

### 5. Initialize and Configure Tailwind CSS

####Initialize Tailwind CSS configuration:

```bash
npx tailwindcss init
```

####Configure `tailwind.config.js` for your Flask app:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

### 6. Set Up Input CSS

Create a CSS file for Tailwind CSS at `static/src/input.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 7. Install Prettier

Install Prettier globally:

```bash
npm install -g prettier prettier-plugin-tailwindcss
```

### 8. Install Tailwind Typography

Install Tailwind Typography:

```bash
npm install @tailwindcss/typography
```

### 9. Create and Configure `package.json`

Create a `package.json` file with the following content to manage Tailwind CSS and other dependencies:

```json
{
  "devDependencies": {
    "tailwindcss": "^3.4.10"
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
}
```

### 10. Create Your Flask Application

Create a `main.py` file with the following content:

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### 11. Create HTML Template

Create the main HTML file at `templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Flask App</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='src/output.css') }}"
    />
  </head>
  <body class="flex items-center justify-center h-screen">
    <div class="container mx-auto">
      <h1 class="text-3xl font-bold text-center">Hello World</h1>
      <!-- Add your content here -->
    </div>
  </body>
</html>
```

### 12. Compile Tailwind CSS

To compile your Tailwind CSS into a usable file:

####For a one-time build:

```bash
npm run build:css
```

####To watch for changes:

```bash
npm run watch:css
```

### 13. Create Prettier Configuration

Create a `.prettierrc.json` file for Prettier with the following content:

```json
{}
```

### 14. Install and Run Browser-Sync

To install Browser-Sync globally:

```bash
npm install -g browser-sync
```

Run Browser-Sync:

```bash
browser-sync start --no-notify --proxy '127.0.0.1:5000' --files 'static/src/_.css, templates/_.html' --delay 300
```

### 14. Configure Visual Studio Code Tasks

Create a `.vscode/tasks.json` file with the following content:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Flask",
      "type": "shell",
      "command": ".venv/bin/python main.py",
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Watch CSS with TailwindCSS",
      "type": "shell",
      "command": "npx tailwindcss -i static/src/input.css -o static/src/output.css --minify --watch",
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Start Browser-Sync",
      "type": "shell",
      "command": "browser-sync start --no-notify --proxy '127.0.0.1:5000' --files 'static/src/_.css, templates/_.html' --delay 300",
      "isBackground": true,
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
        "isDefault": true
      }
    }
  ]
}
```

### 14. Run Your Flask Application

Run your Flask application:

```bash
python3 main.py
```

Your Flask app should now be running at `http://127.0.0.1:5000/`, displaying the "Hello World" message styled with Tailwind CSS.
