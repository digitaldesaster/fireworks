import os

def parse_code_to_markdown(file_structure: dict, output_file: str) -> None:
    with open(output_file, 'w') as outfile:
        for section, path in file_structure.items():
            outfile.write(f"# {section}\n\n")
            
            # Adjust path to work in the parent directory
            adjusted_path = os.path.join("..", path)
            
            # Check if path exists
            if not os.path.exists(adjusted_path):
                outfile.write(f"Path not found: {adjusted_path}\n\n")
                continue
                
            # Handle single file
            if os.path.isfile(adjusted_path):
                with open(adjusted_path, 'r', encoding='utf-8', errors='ignore') as file:
                    outfile.write("```\n")
                    outfile.write(file.read())
                    outfile.write("\n```\n\n")
            # Handle directory and subdirectories
            elif os.path.isdir(adjusted_path):
                for root, _, files in os.walk(adjusted_path):
                    # Skip __pycache__ and core/documents folders
                    if '__pycache__' in root or 'core/documents' in root:
                        continue
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as dir_file:
                                relative_path = os.path.relpath(file_path, start=os.path.join("..", path))
                                outfile.write(f"## {relative_path}\n\n")
                                outfile.write("```\n")
                                outfile.write(dir_file.read())
                                outfile.write("\n```\n\n")
                        except (UnicodeDecodeError, IOError):
                            outfile.write(f"## {file_path}\n\n")
                            outfile.write("```\nBinary or non-text file - skipped\n```\n\n")

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
            "core": "core"
        }
        output_file = "all_code.md"
    
    parse_code_to_markdown(file_structure, output_file)

if __name__ == "__main__":
    generate_markdown(only_template=False)
    generate_markdown(only_template=True)
