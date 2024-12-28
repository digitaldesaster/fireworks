import os

def parse_code_to_markdown(file_structure: dict, output_file: str) -> None:
    with open(output_file, 'w') as outfile:
        for section, path in file_structure.items():
            outfile.write(f"# {section}\n\n")
            
            # Check if path exists
            if not os.path.exists(path):
                outfile.write(f"Path not found: {path}\n\n")
                continue
                
            # Handle single file
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    outfile.write("```\n")
                    outfile.write(file.read())
                    outfile.write("\n```\n\n")
            # Handle directory
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    if '__pycache__' in root:
                        continue
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as dir_file:
                                outfile.write(f"## {file_path}\n\n")
                                outfile.write("```\n")
                                outfile.write(dir_file.read())
                                outfile.write("\n```\n\n")
                        except (UnicodeDecodeError, IOError):
                            outfile.write(f"## {file_path}\n\n")
                            outfile.write("```\nBinary or non-text file - skipped\n```\n\n")

if __name__ == "__main__":
    file_structure = {
        "app.py": "app.py",
        "tailwind.config.js": "tailwind.config.js",
        "templates": "templates",
        "core": "core"
    }
    parse_code_to_markdown(file_structure, "all_code.md")
