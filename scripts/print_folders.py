import os

def print_subdirectories(max_depth=None):
    root_directory = os.getcwd()
    
    for dirpath, dirnames, filenames in os.walk(root_directory):
        # Calculate the depth of the current subdirectory
        depth = dirpath[len(root_directory):].count(os.sep)
        
        # Skip the root directory
        if depth > 0:
            # Print the current subdirectory
            print(dirpath)
        
        # Check if the maximum depth is specified and reached
        if max_depth is not None and depth >= max_depth:
            dirnames.clear()  # Don't search deeper subdirectories

# Example usage
print_subdirectories()