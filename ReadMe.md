## Prerequisites

Ensure you have the following installed:

- Python 3.10+
- pip
- npm

### 1. Open VSCode

Create a new folder for your project and open it. Start a terminal in VSCode.

### 2. Clone the Flask Tailwind Installer Repository into the New Folder

```bash
git clone https://github.com/digitaldesaster/fireworks.git .
```

### 3. Create and Activate a Virtual Environment

Create and activate the virtual environment and open the project in VSCode.

```bash
python3 -m venv .venv
```

Activate the virtual environment in VSCode:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 4. Install Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 5. Install and Initialize Tailwind CSS

```bash
npm install -D tailwindcss
npx tailwindcss init
npm i -D @iconify/tailwind @iconify/json
```

### 6. Create Folder /core/documents

```bash
mkdir core/documents
sudo chown -R www-data:www-data /var/www/tests_alex/fireworks/core/documents
sudo chmod -R 775 /var/www/tests_alex/fireworks/core/documents
```

### 7. Start the Flask Server, Browser-Sync, and the TailwindCSS Watcher

Press `cmd + shift + p` and run "Start All" to start the Flask server, Browser-Sync, and the TailwindCSS watcher.

Or start them separately:

- Start Flask
- Start Browser-Sync
- Watch CSS with TailwindCSS

### 8. Remove the .git Folder

```bash
sudo rm -rf .git
```

### 9. Prepare the Git Repository

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

### 10. Initialize a New Git Repository

```bash
gh repo create my_new_project --public --source=. --remote=origin
```

### 11. Push the Changes to the Remote Repository

```bash
git push -u origin main
```
