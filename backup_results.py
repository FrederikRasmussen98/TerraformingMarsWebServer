import os
import shutil
from datetime import datetime

def backup_results():
    # Define source file and backup directory
    source_file = "results.json"
    backup_dir = "backup"
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup file name with timestamp
    timestamp = datetime.now().strftime("%Y_%m_%d")
    backup_file = os.path.join(backup_dir, f"{timestamp}_results.json")
    
    # Copy the file
    print(os.getcwd())
    print(source_file)
    print(backup_file)
    shutil.copy(source_file, backup_file)
    print(f"Backup created: {backup_file}")

if __name__ == "__main__":
    backup_results()
