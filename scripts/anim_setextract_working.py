import os
import re

# Function to find and store .mb files
def find_mb_files(directory):
    mb_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mb'):
                base_name = os.path.splitext(file)[0]
                mb_files[base_name] = os.path.join(root, file)
    return mb_files

# Function to process animations text block into a list of animations
def process_animations_block(block):
    lines = block.strip().split('\n')
    original_count = lines[0].strip() if lines and lines[0].isdigit() else "Unknown"
    animations = [line.strip() for line in lines[1:] if line.strip()] if lines and lines[0].isdigit() else [line.strip() for line in lines if line.strip()]
    return original_count, animations

# Function to match animations against .mb files
def match_animations_to_mb_files(animations, mb_files):
    matching_files = []
    misnamed_files = []

    for animation in animations:
        if animation in mb_files:
            matching_files.append(mb_files[animation])
        else:
            misnamed_files.append(animation)

    return matching_files, misnamed_files

# Main processing starts here
root_directory = os.getcwd()
mb_files = find_mb_files(root_directory)
pattern_acs_name = r"ACSName\s*\{\s*\"(.*?)\"\s*\}"
pattern_main_animations = r"Animations_Per_Body_Part\s*\{([\s\S]*?)\}"

acs_details = {}

for dirpath, dirnames, filenames in os.walk(root_directory):
    for filename in filenames:
        if filename.endswith('.anim_set'):
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r') as file:
                content = file.read()

                acs_name_match = re.search(pattern_acs_name, content, re.DOTALL)
                if acs_name_match:
                    acs_name = acs_name_match.group(1)
                    animations_match = re.search(pattern_main_animations, content, re.DOTALL)
                    if animations_match:
                        animations_block = animations_match.group(1)
                        original_count, animations = process_animations_block(animations_block)
                        matching_files, misnamed_files = match_animations_to_mb_files(animations, mb_files)

                        # Store details
                        acs_details[acs_name] = {
                            'original_count': original_count,
                            'animations': animations,
                            'matching_files': matching_files,
                            'misnamed_files': misnamed_files
                        }

# Output the detailed information
for acs_name, details in acs_details.items():
    print(f"ACS Name: {acs_name}")
    print(f"Original Animation Count: {details['original_count']}")
    print("Animations:")
    for anim in details['animations']:
        print(f"    {anim}")
    print("Matching .mb Files:")
    for file in details['matching_files']:
        print(f"    {file}")
    print("Misnamed Animations:")
    for anim in details['misnamed_files']:
        print(f"    {anim}")
