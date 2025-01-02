import os
import re
import csv

def write_anim_set_details(csv_writer, title, anim_set_aggregate):
    csv_writer.writerow([title])
    csv_writer.writerow(['ANIM_SET File', 'Animation Files', 'Existing Maya Source Files', 'Rig base used in this file', 'Existing Maya rig source file'])
    for anim_set, details in anim_set_aggregate.items():
        animations = '; '.join(details['animations'])
        mb_files = '; '.join(details['mb_files'])
        rig_bases = '; '.join(set(details['rig_bases']))  # 
        rig_source_files = '; '.join(set(details['rig_source_files']))  # 
        csv_writer.writerow([anim_set, animations, mb_files, rig_bases, rig_source_files])
    csv_writer.writerow([])  # 

def find_and_extract_lines():
    current_dir = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    root_folder_name = os.path.basename(current_dir)
    output_csv_file = os.path.join(current_dir, f"{root_folder_name}_data_summary.csv").replace('\\', '/')

    mb_files = {}
    artr_adbi_values = {}
    cinema_anim_set_aggregate = {}
    regular_anim_set_aggregate = {}
    unique_animations = set()
    unique_rigs = set()

    # Scan for .mb and .artr.adbi files
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            file_path = os.path.join(root, file).replace('\\', '/')
            if file.endswith('.mb'):
                mb_base_name = os.path.splitext(file)[0]
                mb_files[mb_base_name] = file_path
            elif file.endswith('.artr.adbi'):
                ani_base_name = os.path.splitext(os.path.basename(file_path))[0].replace('.artr', '')
                with open(file_path, 'r') as f:
                    for line in f:
                        if "<param numattr=0 4cc='BASE' aid" in line:
                            src_index = line.find('src="$')
                            if src_index != -1:
                                end_quote_index = line.find('"', src_index + 6)
                                extracted_value = line[src_index+5:end_quote_index] if end_quote_index != -1 else line[src_index+5:].strip()
                                base_name = extracted_value.split('/')[-1].replace('.base', '')
                                artr_adbi_values[ani_base_name] = extracted_value
                                unique_rigs.add(base_name)
                                break

    # .anim_set files processing
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.anim_set'):
                anim_set_file_path = os.path.join(root, file).replace('\\', '/')
                anim_set_dict = {'animations': [], 'mb_files': [], 'rig_bases': [], 'rig_source_files': []}
                has_cinematic = False  # Flag for cinema check

                with open(anim_set_file_path, 'r') as f:
                    for line in f:
                        match = re.search(r'Animation_Source_Filename\s+"([^"]+)"', line)
                        if match:
                            ani_file = match.group(1)
                            ani_file_name = os.path.basename(ani_file)
                            ani_base_name = os.path.splitext(ani_file_name)[0]
                            expected_mb_filename = f"{ani_base_name}.mb"
                            mb_file_path = mb_files.get(ani_base_name, f"Missing source Maya file: {expected_mb_filename}")
                            extracted_rig = artr_adbi_values.get(ani_base_name, 'N/A')
                            corresponding_rig_mb = mb_files.get(os.path.splitext(os.path.basename(extracted_rig))[0], 'N/A')

                            if "cinematic" in mb_file_path:  # Checking for "cinematic" in path
                                has_cinematic = True
                            
                            unique_animations.add(ani_file_name)
                            anim_set_dict['animations'].append(ani_file_name)
                            anim_set_dict['mb_files'].append(mb_file_path)
                            anim_set_dict['rig_bases'].append(extracted_rig)
                            anim_set_dict['rig_source_files'].append(corresponding_rig_mb if corresponding_rig_mb != 'N/A' else 'Missing source rig file')

                # Classify the anim_set based on the has_cinematic flag
                if has_cinematic:
                    cinema_anim_set_aggregate[anim_set_file_path] = anim_set_dict
                else:
                    regular_anim_set_aggregate[anim_set_file_path] = anim_set_dict

    # Write output to CSV
    with open(output_csv_file, 'w', newline='') as csv_out:
        csv_writer = csv.writer(csv_out)
        csv_writer.writerow(['Summary'])
        csv_writer.writerow(['Total ANIM_SET Files', len(cinema_anim_set_aggregate) + len(regular_anim_set_aggregate)])
        csv_writer.writerow(['Total Unique Animations', len(unique_animations)])
        csv_writer.writerow(['Total Rig Bases', len(unique_rigs)])
        csv_writer.writerow([])

        # Write details for cinema and regular animation sets using the function
        write_anim_set_details(csv_writer, 'Cinematic ANIM_SET Files', cinema_anim_set_aggregate)
        write_anim_set_details(csv_writer, 'Regular ANIM_SET Files', regular_anim_set_aggregate)

find_and_extract_lines()
