import os
import re
import csv

def extract_hierarchy_node_names(file_path):
    names = [] 
    capture_names = False

    with open(file_path, 'r') as file:
        for line in file:
            if 'Child_Hierarchy_Nodes' in line.strip():
                capture_names = True
                continue
            if capture_names and 'Name' in line.strip():
                name_match = re.search(r'Name "([^"]+)"', line.strip())
                if name_match:
                    names.append(name_match.group(1))
    return names

def write_names_to_csv(directory_path, output_csv_file):
    with open(output_csv_file, 'w', newline='') as csvfile:
        fieldnames = ['File', 'Names Count', 'Names']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.anim_set'):
                    file_path = os.path.join(root, file)
                    names = extract_hierarchy_node_names(file_path)
                    #
                    writer.writerow({'File': file, 'Names Count': len(names), 'Names': ', '.join(names)})


directory_path = os.getcwd()
output_csv_file = 'rig_variations.csv' 
write_names_to_csv(directory_path, output_csv_file)
