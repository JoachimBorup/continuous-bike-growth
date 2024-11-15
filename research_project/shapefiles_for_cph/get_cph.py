
# move all files in subfoler files to ../../../../bikenwgrowth_external/data/copenhagen/"
import os
import shutil

def moveFiles():
    # Define source and destination paths
    source_folder = 'shapefiles_for_cph/files'  # Adjust as needed
    destination_folder = '../../bikenwgrowth_external/data/copenhagen/'
    
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return
    
    # Check if the destination folder exists; create it if not
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"Created destination folder: {destination_folder}")
    
    # Iterate through all files in the source folder
    for file_name in os.listdir(source_folder):
        source_file_path = os.path.join(source_folder, file_name)
        destination_file_path = os.path.join(destination_folder, file_name)
        
        # Check if it's a file (and not a subfolder)
        if os.path.isfile(source_file_path):
            shutil.copy(source_file_path, destination_file_path)
            print(f"Moved: {source_file_path} -> {destination_file_path}")
    
    print("All files moved successfully.")

# Call the function
moveFiles()