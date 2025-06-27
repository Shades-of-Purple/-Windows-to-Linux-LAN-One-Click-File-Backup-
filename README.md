# Windows-to-Linux LAN One-Click File Backup
A Python script that automates a complete file backup over a local wifi network, specifically designed to backup Windows user folders to a Linux backup server running Samba.

## Features
* Just one click to run the script and initiate a backup for all files in the specified folders.
* Progress bar shows percent completed while backing up files.
* Error messages are generated for files with overly long paths, providing transparency when a file cannot be transferred.

* Network connectivity issues are handled by automatically attempting to reconnect five times before asking the user in the terminal if the script should try connecting again.
* Only the two most recent backups are retained.
* Tracks file changes to avoid unnecessarily backing up files already backed up.
