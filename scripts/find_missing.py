import os
import re

def find_and_substitute_linked_files(ma_file):
    linked_files = []
    substituted_content = ""

    print(f"Parsing {ma_file}...")

    # Read the .ma file
    with open(ma_file, 'r') as file:
        content = file.read()

        # Regular expression to match file paths
        file_pattern = re.compile(r'(setAttr\s+"\.ftn"\s+-type\s+"string"\s+")([^"]+)(")')

        # Find file paths
        for line in content.split('\n'):
            file_match = file_pattern.search(line)
            if file_match:
                file_path = file_match.group(2)
                file_name = os.path.basename(file_path)
                linked_files.append(file_name)
                print(f"Found file: {file_name}")
                substituted_content += line + '\n'
            else:
                substituted_content += line + '\n'

    print("Parsing completed.")
    return linked_files, substituted_content

def search_files(root_folder, file_list):
    found_files = {}

    print(f"\nSearching for the following files in {root_folder} and subfolders:")
    for file in file_list:
        print(file)

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file in file_list:
                found_files[file] = os.path.join(root, file)
                print(f"Found file: {file}")

    return found_files

def substitute_file_paths(content, found_files):
    substituted_content = ""

    # Regular expression to match file paths
    file_pattern = re.compile(r'(setAttr\s+"\.ftn"\s+-type\s+"string"\s+")([^"]+)(")')

    # Substitute file paths with the correct path
    for line in content.split('\n'):
        file_match = file_pattern.search(line)
        if file_match:
            file_name = os.path.basename(file_match.group(2))
            if file_name in found_files:
                substituted_line = file_match.group(1) + found_files[file_name] + file_match.group(3)
                substituted_content += substituted_line + '\n'
            else:
                substituted_content += line + '\n'
        else:
            substituted_content += line + '\n'

    return substituted_content

# Example usage
ma_file_path = 'test.ma'
current_folder = os.path.dirname(os.path.abspath(__file__))

linked_files, original_content = find_and_substitute_linked_files(ma_file_path)

print("\nLinked files:")
for file in linked_files:
    print(file)

found_files = search_files(current_folder, linked_files)

if found_files:
    print("\nFound files:")
    for file, path in found_files.items():
        print(f"{file}: {path}")

    # Substitute file paths in the original content with the correct path
    substituted_content = substitute_file_paths(original_content, found_files)

    # Save the modified .ma file with "_fix.ma" suffix
    fixed_ma_file_path = os.path.splitext(ma_file_path)[0] + "_fix.ma"
    with open(fixed_ma_file_path, 'w') as file:
        file.write(substituted_content)
        print(f"\nModified .ma file saved as: {fixed_ma_file_path}")
else:
    print("\nNo linked files found in the current folder and subfolders.")