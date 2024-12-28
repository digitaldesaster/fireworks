## Prerequisites

Ensure you have the following installed:

- Python 3.10+
- pip
- npm

### 1. Open VSCode

Create a new folder for your project and open it. start a terminal in VSCode

### 2. Clone the Flask Tailwind Installer Repository into the new folder

```bash
gh repo clone digitaldesaster/flask_tailwind_installer .
```

### 3. Create and Activate a Virtual Environment

Create and activate the virtual environment and open the project in VSCode

- **macOS and Linux:**

```bash
python3 -m venv .venv
```

activate the virtual environment in VSCode

```bash
source .venv/bin/activate
```

### 4. Install the rest of the dependencies

use the install.py script to install the rest of the dependencies

```bash
python3 install.py
```

### 5. Start the Flask Server, Browser-Sync and the TailwindCSS Watcher

press cmd + shift + p and and run Start All to start the flask server, browser-sync and the tailwindcss watcher

or start them seperately:

- Start Flask
- Start Browser-Sync
- Watch CSS with TailwindCSS

### 6. Remove the .git folder

```bash
sudo rm -rf .git
```

### 7. prepare the git repository

```bash
git init
touch .gitignore
echo "node_modules/" >> .gitignore
echo ".venv/" >> .gitignore
echo ".env" >> .gitignore
echo "package-lock.json" >> .gitignore
echo ".DS_Store" >> .gitignore
git add .
git commit -m "Initial commit"
git branch -M main
```

### 8. Initialize a new Git Repository

```bash
gh repo create my_new_project --public --source=. --remote=origin
```

### 9. Push the changes to the remote repository

```bash
git push -u origin main
```
