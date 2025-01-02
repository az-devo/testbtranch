import os
import subprocess

extraction_script = "find_anim_sets.py"

def traverse_and_extract(root_directory, max_depth):
    for dirpath, dirnames, filenames in os.walk(root_directory):
        depth = dirpath.count(os.sep) - root_directory.count(os.sep)

        if depth == max_depth:
            print(f"Processing directory: {dirpath}")

            # Call the main extraction script using subprocess and pass the directory path as an argument
            subprocess.run(["python", extraction_script, dirpath])

            # Remove the processed directory from dirnames to avoid further traversal
            dirnames[:] = []

def main():
    root_directory = "g:\_tmp\Characters"
    max_depth = 2  # Specify the desired depth

    traverse_and_extract(root_directory, max_depth)

if __name__ == "__main__":
    main()