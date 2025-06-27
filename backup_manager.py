#Only tqdm is a third-party package
from tqdm import tqdm
import os
import shutil
import datetime
import time
from pathlib import Path

#source_folders will be a list containing folders from the current laptop whereas backup_path will be a string converted into a Path object indicating where they should be backedup on the old laptop
class BackupManager:
    def __init__(self, source_folders, backup_path):
        self.source_folders = source_folders
        self.backup_path = Path(backup_path)
    
    #Testing network connection
    def check_network_path(self):
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                test_path = Path(self.backup_path)
                test_path.exists()
                return True
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    print(f"\nLost connection to backup device. Gave up after {max_retries} attempts to reconnect.")
                    response = input("Enter 'retry' to try again, or any other key to exit.")
                    if response.lower() == 'retry':
                        retry_count -= 1
                    else:
                        raise Exception("Backup aborted.")
                else:
                    print(f"\nConnection attempt failed. Retrying in 30 seconds.")
                    time.sleep(30)
        return False


    #Creating a timestamped backup folder
    def create_timestamped_backup_folder(self):
        timestamp = datetime.datetime.now().strftime('%Y_%m_%d__%H%M%S')
        backup_dir = self.backup_path / f'backup_{timestamp}'
        try:
            self.check_network_path()
            backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created backup directory folder: {backup_dir}")
            return backup_dir
        except Exception as e:
            print(f"Error creating backup directory: {e}")
            raise
    
    #Helper method to get list of backup folders
    def get_backup_folders(self):
        backup_folders = []
        for item in self.backup_path.iterdir():
            if item.is_dir() and item.name.startswith('backup_'):
                backup_folders.append(item)
        return backup_folders

    #Finding the latest backup folder (so as to see what has changed since)
    def get_latest_backup(self):
        try:
            backup_folders = self.get_backup_folders()
            return max(backup_folders, key=lambda x: x.stat().st_mtime)
        except Exception as e:
            print(f"Error finding latest backup: {e}")
            return None
    
    def update_backup(self):
        new_backup_dir = self.create_timestamped_backup_folder()
        latest_backup = self.get_latest_backup()
        #Counting number of files for progress bar
        total_files = sum(len(files) for folder in self.source_folders for _, _, files in os.walk(folder))
        #Creating the progress bar
        with tqdm(total=total_files, desc="Backing up files") as pbar:
            #Converts source_folders to path objects
            for source_folder in self.source_folders:
                source_path = Path(source_folder)
                #For all folders and files inside a current laptop source folder, apply same file path/folder structure to old laptop backup folder.
                for root, dirs, files in os.walk(source_folder):
                    current_dir = Path(root)
                    rel_path = current_dir.relative_to(source_path)
                    backup_dir = new_backup_dir / rel_path
                    self.check_network_path()
                    try:
                        backup_dir.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        print(f"Error creating directory {backup_dir}: {e}")
                        continue
                    #Determine which files are new or changed based on size and modification time
                    for file in files:
                        source_file = current_dir / file
                        backup_file = backup_dir / file
                        need_to_copy = True
                        if latest_backup:
                            old_backup_file = latest_backup / rel_path / file
                            if old_backup_file.exists():
                                source_stat = source_file.stat()
                                old_stat = old_backup_file.stat()
                                if (source_stat.st_mtime == old_stat.st_mtime and source_stat.st_size == old_stat.st_size):
                                    need_to_copy = False
                        #Copy files and their metadata from source to backup
                        try:
                            if need_to_copy:
                                self.check_network_path()  
                                shutil.copy2(source_file, backup_file)
                        #Print error message if copy fails
                        except Exception as e:
                            print(f"Error copying {source_file}: {e}")
                        #Update the progress bar for each files copied successfully or unsuccessfully
                        finally:
                            pbar.update(1)
        #Always two there are. No more, no less.
        try:
            backup_folders = self.get_backup_folders()
            backup_folders.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_backup in backup_folders[2:]:
                self.check_network_path()
                shutil.rmtree(old_backup)
                print(f"Removed old backup: {old_backup}")
            #Confirmation of backup completion and location 
            print(f"\nBackup completed successfully to: {new_backup_dir}")
            if len (backup_folders) > 2:
                print(f"Removed {len(backup_folders) - 2} old backup(s)")
            #Confirmation of the 2 most recent backups
            print(f"Maintaining the two most recent backups:")
            for recent_backup in backup_folders[:2]:
                print(f"- {recent_backup}")
        #Reporting any errors if appropriate
        except Exception as e:
            print(f"\nError during backup cleanup: {e}")
            return False
    

if __name__ == "__main__":
    #Defining paths to source_folders
    user_path = os.path.expanduser('~')
    source_folders = [
        os.path.join(user_path, 'Documents'),
        os.path.join(user_path, 'Pictures'),
        os.path.join(user_path, 'Videos'),
        os.path.join(user_path, 'Music')
    ]

    #Temporary test destination for backup copies
    backup_destination = r"\\BackupDevice\Backups"

    #Creating an instance of the BackupManager class
    backup_manager = BackupManager(source_folders, backup_destination)
    backup_manager.update_backup()






