import os
import re

# Step 1: Modify Directory Search to only search the current folder and its subfolders
def find_files_by_extension(directory, extension):
    """
    Finds files with a given extension within the specified directory and its subdirectories.
    """
    files_found = {}
    for root, _, files in os.walk(directory):
        if root.startswith(directory):  # Ensure it only includes the current directory and subdirectories
            for file in files:
                if file.endswith(extension):
                    base_name = os.path.splitext(os.path.splitext(file)[0])[0]
                    files_found[base_name] = os.path.join(root, file)
        else:
            break  # Stop searching deeper if it's beyond the subdirectories of the specified directory
    return files_found

# Step 2: Refactor Animation Set Parsing to remove duplicates and list all animations, main character, and character variations
def process_animations_block(block):
    """
    Processes animation blocks, removes duplicates, and extracts animations.
    """
    lines = block.strip().split('\n')[1:]
    animations = set()  # Use a set to automatically remove duplicates
    for line in lines:
        animation = line.strip()
        if animation:
            animations.add(animation)
    return list(animations)  # Convert back to list to maintain compatibility


# Step 3: Implement logic to match .mb files against animation names and list any missing ones
def match_animations_to_mb_files(animations, mb_files):
    """
    Matches animations to .mb files and identifies any missing matches.
    """
    matched_files = {}
    missing_animations = []
    for anim in animations:
        if anim in mb_files:
            matched_files[anim] = mb_files[anim]
        else:
            missing_animations.append(anim)
    return matched_files, missing_animations

# Step 4: Adjust parsing for .ani.adb files to extract "character_bound.base"
def extract_src_from_ani_adbi_files(ani_adbi_files):
    """
    Parses .ani.adb files to extract "character_bound.base".
    """
    src_pattern = re.compile(r"<param numattr=0 4cc='BASE'.*?src=\"\$\S*\/([^\".]+_bound)\.base\">")
    src_values = set()
    for path in ani_adbi_files.values():
        with open(path, 'r') as file:
            content = file.read().replace('\n', ' ').replace('\r', '')
            matches = src_pattern.findall(content)
            src_values.update(matches)
    return src_values

# Note: Further steps will include handling .rtr.adbi files and CSV output formatting. These functions will be
# integrated and refined as part of the overall solution.


# Step 5: Handle .rtr.adbi files for extracting Maya rig source filename and path
def verify_and_parse_rtr_adbi_files(src_values, rtr_adbi_files):
    """
    Searches for character_bound.rtr.adbi files, extracts the Maya rig source filename and path,
    and handles missing files by issuing a warning.
    """
    src_pattern = re.compile(r"<param numattr=31 4cc='MAYA'.*?src=\"([^\"]*_bound.mb)\">", re.DOTALL)
    matched_files = {}
    missing_files = []
    for src_value in src_values:
        if src_value in rtr_adbi_files:
            path = rtr_adbi_files[src_value]
            with open(path, 'r') as file:
                content = file.read().replace('\n', ' ').replace('\r', '')
                match = src_pattern.search(content)
                if match:
                    matched_files[src_value] = match.group(1)
                else:
                    missing_files.append(src_value)
        else:
            missing_files.append(src_value)
    return matched_files, missing_files

# Note: The implementation of CSV output formatting is pending and will be the final step to complete the script's refactoring and enhancements.
# This function, along with the previously developed ones, will be integrated into a coherent solution that meets all the specified requirements.


def main():
    root_directory = os.getcwd()
    mb_files = find_files_by_extension(root_directory, '.mb')
    ani_adbi_files = find_files_by_extension(root_directory, '.ani.adbi')
    rtr_adbi_files = find_files_by_extension(root_directory, '.rtr.adbi')
    
    pattern_acs_name = r"ACSName\s*\{\s*\"(.*?)\"\s*\}"
    pattern_hierarchy_node = r"Hierarchy_Node\s*\{.*?Name\s*\"(.*?)\".*?\}"
    pattern_main_animations = r"Animations_Per_Body_Part\s*\{([\s\S]*?)\}"

    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.anim_set'):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r') as file:
                    content = file.read()
                    acs_name_match = re.search(pattern_acs_name, content, re.DOTALL)
                    if acs_name_match:
                        acs_name = acs_name_match.group(1)
                        hierarchy_nodes = re.findall(pattern_hierarchy_node, content, re.DOTALL)
                        if hierarchy_nodes:
                            main_character = hierarchy_nodes[0]
                            variations = hierarchy_nodes[1:]
                            
                            animations_match = re.search(pattern_main_animations, content, re.DOTALL)
                            if animations_match:
                                animations_block = animations_match.group(1)
                                animations = process_animations_block(animations_block)
                                
                                print(f"ACS Name: {acs_name}")
                                print(f"Main Character: {main_character}")
                                print(f"Variation Count: {len(variations)}")  # Print the count of variation characters
                                print(f"Animation Count: {len(animations)}")
                                for anim in animations:
                                    print(f"    {anim}")
                                match_animations_to_mb_files(animations, mb_files)

if __name__ == "__main__":
    main()


