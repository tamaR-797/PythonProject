🛠 WIT - Python Version Control System
WIT is a lightweight version control system (VCS) written in Python. The project simulates the core operations of Git, allowing users to track changes to files in a simple and efficient way via the command line.

🏗 System architecture
The project was built with strict attention to separation of concerns:

wit.py (The Interface): Responsible for the user interface (CLI) using the click library. It serves as the "skeleton" of commands and guides the user to execute the logic.

logic.py (The Engine): Contains all the technical implementation - file management, recursive copies, creating unique commits and version recovery.

📋 Available commands
To initialize the project and run it, type in the command line:
pip install -r requirements.txt
1. Initialize the system (init)
Creates the infrastructure required for system operation: a .wit folder that includes the Staging area and the commit folder.

Bash
python wit.py init
2. Add files (add)
Copies files or entire folders into the Staging area.

The system supports recursive addition.

The system ignores files defined in .witignore or system files (such as venv).

Bash
python wit.py add <path_to_file_or_folder>
# Or to add the entire current folder:
python wit.py add .
3. Create a version (commit)
Saves the current state of the Staging as a permanent version.

Uniqueness: Each commit receives a short unique identifier (ID) generated using a UUID.

Automatic cleanup: After the commit, the staging area is cleaned up to prevent duplicates.

Optional: You can add a message describing the change.

Bash
python wit.py commit -m "Your descriptive message"
# Or without a message (will use the default):
python wit.py commit
4. Check status
Shows which files are currently waiting in Staging and have not yet been committed.

Bash
python wit.py status
5. Checkout
Allows you to "go back in time". The command deletes the current working files and restores them exactly as they were in the specific commit selected.

Bash
python wit.py checkout <commit_id>
🛠 Requirements and installation
Make sure you have Python installed (version 3.7 or higher).

Install the project's only dependency:

Bash
pip install click
Make sure that the wit.py and logic.py files are always in the same folder.

⚙️ Ignore Settings (.witignore)
You can create a file named .witignore in the main folder. Any file or folder name written in it (one line per name) will not be entered into the version control system when executing the add command.

🔍 Example Scenarios
Step 1: Initialize the repository
Bash
python wit.py init
# Output: Initialized empty WIT repository in .wit/
Step 2: Add files to staging
Bash
# Create a file
echo "Hello World" > hello.txt
# Add it
python wit.py add hello.txt
# Output: Added hello.txt to staging area.
Step 3: Check status
Bash
python wit.py status
# Output:
# --- Status ---
# Files staged for commit:
# (staged): hello.txt
# Untracked files:
# (none)
Step 4: Create a commit
Bash
python wit.py commit -m "Initial commit"
# Output: Created commit a1b2c3d4: Initial commit
# Staging area cleared.
Step 5: Checkout (Going back in time)
Bash
python wit.py checkout a1b2c3d4
# Output: Switched to commit a1b2c3d4.

Developed by Computer Science students (Tamar Rothen, Shira Shemesh, Ayla Samson) - 2nd year😀.
