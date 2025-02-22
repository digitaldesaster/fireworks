import os

def parse_code_to_markdown(file_structure: dict, output_file: str) -> None:
    # File extensions we want to include
    ALLOWED_EXTENSIONS = {'.py', '.js', '.html', '.css', '.md', '.json'}
    
    # Directories/files to skip
    SKIP_DIRS = {'__pycache__', 'node_modules', '.git', 'temp', 'logs', 'css', 'js/lib'}
    SKIP_FILES = {'.DS_Store', '.gitignore', '.env'}

    with open(output_file, 'w') as outfile:
        for section, path in file_structure.items():
            # Adjust path to work in the parent directory
            adjusted_path = os.path.join("..", path)
            
            # Check if path exists
            if not os.path.exists(adjusted_path):
                continue
                
            # Handle single file
            if os.path.isfile(adjusted_path):
                file_ext = os.path.splitext(adjusted_path)[1]
                if file_ext in ALLOWED_EXTENSIONS:
                    outfile.write(f"# {section}\n\n")
                    with open(adjusted_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read().strip()
                        if content:  # Only write if file has content
                            outfile.write("```\n")
                            outfile.write(content)
                            outfile.write("\n```\n\n")
            
            # Handle directory
            elif os.path.isdir(adjusted_path):
                for root, dirs, files in os.walk(adjusted_path):
                    # Skip blacklisted directories
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                    
                    # For static directory, only include the chat folder
                    if 'static' in root:
                        dirs[:] = [d for d in dirs if d == 'chat']
                    
                    for file in files:
                        if file not in SKIP_FILES:
                            file_ext = os.path.splitext(file)[1]
                            if file_ext in ALLOWED_EXTENSIONS:
                                file_path = os.path.join(root, file)
                                relative_path = os.path.relpath(file_path, adjusted_path)
                                
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read().strip()
                                    if content:  # Only write if file has content
                                        outfile.write(f"## {relative_path}\n\n")
                                        outfile.write("```\n")
                                        outfile.write(content)
                                        outfile.write("\n```\n\n")

def generate_markdown(only_template: bool = False):
    if only_template:
        file_structure = {
            "tailwind.config.js": "tailwind.config.js",
            "templates": "templates"
        }
        output_file = "templates.md"
    else:
        file_structure = {
            "app.py": "app.py",
            "tailwind.config.js": "tailwind.config.js",
            "templates": "templates",
            "core": "core",
            "ai": "ai",
            "config": "collection.config.json",
            "static": "static"
        }
        output_file = "all_code.md"
    
    parse_code_to_markdown(file_structure, output_file)

if __name__ == "__main__":
    generate_markdown(only_template=False)
    generate_markdown(only_template=True)
