import os

def parse_code_to_markdown(file_structure: dict, output_file: str) -> None:
    # File extensions we want to include
    ALLOWED_EXTENSIONS = {'.py', '.js', '.html', '.css', '.md', '.json'}
    
    # Directories/files to skip
    SKIP_DIRS = {'__pycache__', 'core/documents', 'node_modules', '.git', 'temp', 'logs'}
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
            
            # Handle directory and subdirectories
            elif os.path.isdir(adjusted_path):
                outfile.write(f"# {section}\n\n")
                for root, dirs, files in os.walk(adjusted_path):
                    # Skip unwanted directories
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                    
                    for file in files:
                        if file in SKIP_FILES:
                            continue
                            
                        file_ext = os.path.splitext(file)[1]
                        if file_ext not in ALLOWED_EXTENSIONS:
                            continue
                            
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as dir_file:
                                content = dir_file.read().strip()
                                if content:  # Only write if file has content
                                    relative_path = os.path.relpath(file_path, start=os.path.join("..", path))
                                    outfile.write(f"## {relative_path}\n\n")
                                    outfile.write("```\n")
                                    outfile.write(content)
                                    outfile.write("\n```\n\n")
                        except (UnicodeDecodeError, IOError):
                            continue

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
            "config": "collection.config.json"
        }
        output_file = "all_code.md"
    
    parse_code_to_markdown(file_structure, output_file)

if __name__ == "__main__":
    generate_markdown(only_template=False)
    generate_markdown(only_template=True)
