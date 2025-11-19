import os
from datetime import datetime
from utils import load_json_file, save_json_file

def backup_results():
    # Define source file and backup directory
    source_file = "results.json"
    backup_dir = "backup"
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup file name with timestamp
    timestamp = datetime.now().strftime("%Y_%m_%d")
    backup_file = os.path.join(backup_dir, f"{timestamp}_results.json")
    
    # Load and save using utility functions
    data = load_json_file(source_file, [])
    save_json_file(backup_file, data)
    print(f"Backup created: {backup_file}")

if __name__ == "__main__":
    backup_results()
