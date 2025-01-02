#Total unique rig, animation, duped animation, missing mb files for animation
#Duped count is beyond me
#Source folder
#AnimSet name (main key)
#ACS Name: grab for validation dont print it
#Main Character Name: is the Parent of any variants
#Extracted rig_bound name from matching .rtr.adbi file for Main Character:
#Character Variation Count: 
#Character Variation names
#Animation Count: 
#Animation Names list
#Matched Animation MB files: actual maya animations 
#Missing Animation MB files
#Animtion sets that share amnimations
#

import os
import re
import csv
import sys

# generic
def find_files_by_extension(directory, extension):
    files_found = {}
    directory = os.path.abspath(directory)  # Convert to absolute path
    print(directory)
    for root, _, files in os.walk(directory):
        if not root.startswith(directory):
            continue

        for file in files:
            if file.endswith(extension):
                base_name = os.path.splitext(os.path.splitext(file)[0])[0]
                files_found[base_name] = os.path.join(root, file)
    return files_found

def process_animations_block(block):
    lines = block.strip().split('\n')[1:]
    return [line.strip() for line in lines if line.strip()]

def match_animations_to_mb_files(animations, mb_files):
    matched_files = []
    unmatched_animations = []
    for anim in animations:
        found_match = False
        for key, file_path in mb_files.items():
            base_filename = os.path.splitext(os.path.basename(key))[0]
            if anim == base_filename:
                matched_files.append(file_path)
                found_match = True
                break
        if not found_match:
            unmatched_animations.append(anim)
    return matched_files, unmatched_animations

def extract_model_references(content, anim_set_name):
    model_references = []
    pattern_hierarchy_node = re.compile(r"Hierarchy_Node\s*{([^}]*)}", re.DOTALL)
    pattern_model = re.compile(r"Model\s+\"\$\/[^\"]+\/([^\/]+_bound)\.CMDL\"")

    #print(f"Extracting model references for {anim_set_name}")
    hierarchy_nodes = pattern_hierarchy_node.findall(content)
    #print(f"Found {len(hierarchy_nodes)} hierarchy nodes")

    for i, node_content in enumerate(hierarchy_nodes, start=1):
        #print(f"Processing hierarchy node {i}")
        model_matches = pattern_model.finditer(node_content)
        for model_match in model_matches:
            model_reference = model_match.group(1)
            print(f"Found model reference: {anim_set_name} - {model_match.group(0)}")
            model_references.append((anim_set_name, model_reference))

        child_count_match = re.search(r"Child_Hierarchy_Nodes\s+(\d+)", node_content)
        if child_count_match and int(child_count_match.group(1)) > 0:
            child_count = int(child_count_match.group(1))
            print(f"Found {child_count} child hierarchy nodes, recursing")
            model_references.extend(extract_model_references(node_content, anim_set_name))

    print(f"Extracted {len(model_references)} model references for {anim_set_name}")
    return model_references

def match_model_references(anim_sets_info, mb_files):
    for anim_set in anim_sets_info:
        model_ref_paths = []
        for model_ref in anim_set.get('model_references', []):
            for key, file_path in mb_files.items():
                base_filename = os.path.splitext(os.path.basename(key))[0]
                if model_ref[1] == base_filename:
                    model_ref_paths.append(file_path)
                    break

        anim_set['model_ref_paths'] = model_ref_paths

    return anim_sets_info

def process_anim_set(filepath, pattern_acs_name, pattern_hierarchy_node, pattern_main_animations):
    anim_set_info = {}
    anim_set_name = os.path.splitext(os.path.basename(filepath))[0]

    with open(filepath, 'r') as file:
        content = file.read()

    acs_name_match = re.search(pattern_acs_name, content, re.DOTALL)
    acs_name = acs_name_match.group(1) if acs_name_match else ""

    hierarchy_nodes = re.findall(pattern_hierarchy_node, content, re.DOTALL)
    if not hierarchy_nodes:
        print(f"Warning: No Hierarchy_Nodes found in {filepath}.")
        return None

    main_character = hierarchy_nodes[0] if hierarchy_nodes else "N/A"
    variations = hierarchy_nodes[1:] if len(hierarchy_nodes) > 1 else []

    animations_match = re.search(pattern_main_animations, content, re.DOTALL)
    animations = process_animations_block(animations_match.group(1)) if animations_match else []

    model_references = []
    animation_names = []

    for hierarchy_node in hierarchy_nodes:
        animations_match = re.search(r"Animations_Per_Body_Part\s*\{([^}]+)\}", hierarchy_node, re.DOTALL)
        if animations_match:
            animations_block = animations_match.group(1).strip()
            if animations_block.isdigit() and int(animations_block) == 0:
                print(f"No animations found in {filepath}")
                return None 
            else:
                animation_name = re.search(r"\w+", animations_block).group()
                animation_names.append(animation_name)

    model_references = extract_model_references(content, anim_set_name)



    anim_set_info = {
        'anim_set_name': anim_set_name,
        'acs_name': acs_name,
        'main_character': main_character,
        'variations': variations,
        'model_references': model_references,
        'animation_count': len(animations),
        'animations': animations,
        'animation_names': animation_names
    }

    return anim_set_info

def calculate_totals(anim_sets_info, animation_counts):
    totals = {}
    
    total_animations = sum(len(anim_set['animations']) for anim_set in anim_sets_info)
    duplicate_animations = sum(count['count'] - 1 for count in animation_counts.values() if count['count'] > 1)
    unique_animation_count = total_animations - duplicate_animations
    
    totals['total_animations'] = total_animations
    totals['duplicate_animations'] = duplicate_animations
    totals['unique_animation_count'] = unique_animation_count
    
    # dupes
    for anim_set_info in anim_sets_info:
        anim_set_info['duplicate_animation_count'] = sum(1 for animation in anim_set_info['animations'] if animation_counts[animation]['count'] > 1)
    
    # unique rigs
    unique_rigs = set()
    for anim_set in anim_sets_info:
        unique_rigs.update(ref[1] for ref in anim_set.get('model_references', []))
    
    totals['unique_rig_count'] = len(unique_rigs)
    
    return totals          

def export_to_csv(anim_sets_by_folder, animation_counts, totals, subfolder, filename_prefix='anim_sets_info'):
    filename = f"{filename_prefix}_{subfolder}.csv"
    total_headers = [
        'Total Animations',
        'Duplicate Animations',
        'Unique Animation Count',
        'Unique Rig Count'
    ]

    anim_set_headers = [
        'Anim Set Name',
        #'ACS Name',
        'Main Character',
        'Character Variation Count',
        'Variations',
        'Rigs(ModelRef)',
        'Model Ref Path',
        'Animation Count',
        'Duplicate Animation Count',
        'Animations',
        'Matched Animation MB files',
        'Missing Animation MB files',
        'Duplicate Animations',
        'Animation Sets with Duplicates'
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(total_headers)
        writer.writerow([
            totals['total_animations'],
            totals['duplicate_animations'],
            totals['unique_animation_count'],
            totals['unique_rig_count']
        ])

        writer.writerow([]) 

        # anim set headers
        writer.writerow(['Source Folder'] + anim_set_headers)

        # sort into folders
        for folder, anim_sets in sorted(anim_sets_by_folder.items()):
            for anim_set in anim_sets:
                duplicate_animations = [animation for animation in anim_set['animations'] if animation_counts[animation]['count'] > 1]
                animation_sets_with_duplicates = [animation_counts[animation]['anim_sets'] for animation in duplicate_animations]

                model_references_str = ', '.join([ref[1] for ref in anim_set.get('model_references', [])])
                model_ref_paths_str = ', '.join(anim_set.get('model_ref_paths', []))

                writer.writerow([
                    folder,
                    anim_set.get('anim_set_name', ''),
                    #anim_set.get('acs_name', ''),
                    anim_set.get('main_character', ''),
                    len(anim_set.get('variations', [])),
                    ', '.join(anim_set.get('variations', [])),
                    model_references_str,
                    model_ref_paths_str,
                    len(anim_set.get('animations', [])),
                    anim_set.get('duplicate_animation_count', 0),
                    ', '.join(anim_set.get('animations', [])),
                    ', '.join(anim_set.get('matched_mb_files', [])),
                    ', '.join(anim_set.get('missing_mb_files', [])),
                    ', '.join(duplicate_animations),
                    ', '.join([', '.join(anim_sets) for anim_sets in animation_sets_with_duplicates]),
                ])

def main(root_directory):
    print(root_directory)
    mb_files = find_files_by_extension(root_directory, '.mb')
    anim_sets_info = []
    anim_sets_by_folder = {}

    pattern_acs_name = r"ACSName\s*\{\s*\"(.*?)\"\s*\}"
    pattern_hierarchy_node = r"Hierarchy_Node\s*\{.*?Name\s*\"(.*?)\".*?\}"
    pattern_main_animations = r"Animations_Per_Body_Part\s*\{([\s\S]*?)\}"

    animation_counts = {}

    # Get the list of immediate subdirectories in the root directory
    subdirs = [d for d in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory, d))]

    for subdir in subdirs:
        subdir_path = os.path.join(root_directory, subdir)
        for dirpath, dirnames, filenames in os.walk(subdir_path):
            depth = dirpath[len(subdir_path):].count(os.sep)
            if depth > 1:
                dirnames.clear()
            
            for filename in filenames:
                if filename.endswith('.anim_set'):
                    filepath = os.path.join(dirpath, filename)
                    print(f"Processing {filename} in {dirpath}")
                    anim_set_info = process_anim_set(filepath, pattern_acs_name, pattern_hierarchy_node, pattern_main_animations)
                    animations = anim_set_info['animations']
                    anim_set_name = anim_set_info['anim_set_name']
                    for animation in animations:
                        if animation in animation_counts:
                            animation_counts[animation]['count'] += 1
                            animation_counts[animation]['anim_sets'].append(anim_set_name)
                        else:
                            animation_counts[animation] = {
                                'count': 1,
                                'anim_sets': [anim_set_name]
                            }
                    anim_sets_info.append(anim_set_info)

                    folder_name = subdir

                    if folder_name not in anim_sets_by_folder:
                        anim_sets_by_folder[folder_name] = []
                    anim_sets_by_folder[folder_name].append(anim_set_info)

    # Calculate totals and duplicate_animation_count for each anim_set_info
    totals = calculate_totals(anim_sets_info, animation_counts)

    for anim_set in anim_sets_info:
        match_model_references(anim_sets_info, mb_files)
        matched_mb_files, missing_mb_files = match_animations_to_mb_files(anim_set['animations'], mb_files)
        anim_set['matched_mb_files'] = matched_mb_files
        anim_set['missing_mb_files'] = missing_mb_files

    export_to_csv(anim_sets_by_folder, animation_counts, totals, os.path.basename(root_directory))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the root directory as a command-line argument.")
        sys.exit(1)

    root_directory = sys.argv[1]
    main(root_directory)

