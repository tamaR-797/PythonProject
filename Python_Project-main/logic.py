import os
import shutil
import uuid
from datetime import datetime

WIT_DIR = ".wit"
STAGING_DIR = os.path.join(WIT_DIR, "staging")
COMMITS_DIR = os.path.join(WIT_DIR, "commits")

def get_ignore_list():
    ignore = {WIT_DIR, ".witignore", ".venv", ".idea", "__pycache__", "wit.py", "logic.py"}
    if os.path.exists(".witignore"):
        with open(".witignore", "r") as f:
            for line in f:
                if line.strip():
                    ignore.add(line.strip())
    return ignore

def init():
    if not os.path.exists(WIT_DIR):
        os.makedirs(STAGING_DIR)
        os.makedirs(COMMITS_DIR)
        print("Initialized empty WIT repository in .wit/")
    else:
        print("WIT repository already exists.")

def add(path):
    if not os.path.exists(WIT_DIR):
        print("Error: Not a WIT repository. Run 'init' first.")
        return

    ignore_list = get_ignore_list()

    def add_to_staging(src):
        if os.path.basename(src) in ignore_list:
            return
        target = os.path.join(STAGING_DIR, src)
        if os.path.isdir(src):
            if not os.path.exists(target):
                os.makedirs(target)
            for item in os.listdir(src):
                add_to_staging(os.path.join(src, item))
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(src, target)

    if path == ".":
        for item in os.listdir():
            add_to_staging(item)
    else:
        add_to_staging(path)
    print(f"Added {path} to staging area.")

def commit(message="No message provided"):
    if not os.path.exists(STAGING_DIR) or not os.listdir(STAGING_DIR):
        print("Nothing to commit, staging area is empty.")
        return

    commit_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_path = os.path.join(COMMITS_DIR, commit_id)

    shutil.copytree(STAGING_DIR, commit_path)

    #  שמירת המטא-דאטה
    with open(os.path.join(commit_path, ".metadata"), "w") as f:
        f.write(f"Message: {message}\n")
        f.write(f"Timestamp: {timestamp}\n")

    # ניקוי תיקיית ה-staging
    #  עוברים על כל מה שיש ב-staging ומוחקים אותו
    for item in os.listdir(STAGING_DIR):
        item_path = os.path.join(STAGING_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)  # מחיקת תיקייה
        else:
            os.remove(item_path) 

    print(f"Created commit {commit_id}: {message}")
    print("Staging area cleared.")


def status():
    if not os.path.exists(WIT_DIR):
        print("Not a WIT repository.")
        return

    ignore_list = get_ignore_list()
    staged_files = []
    for root, dirs, files in os.walk(STAGING_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), STAGING_DIR)
            staged_files.append(rel_path)

    # מציאת קבצים בתיקיית העבודה שאינם ב-Staging
    working_files = []
    for root, dirs, files in os.walk("."):
        if any(ignored in root for ignored in ignore_list): continue
        for file in files:
            if file in ignore_list: continue
            rel_path = os.path.relpath(os.path.join(root, file), ".")
            working_files.append(rel_path)

    untracked = [f for f in working_files if f not in staged_files]

    print("--- Status ---")
    print("Files staged for commit:")
    for f in staged_files: print(f"  (staged): {f}")

    print("\nUntracked files (use 'wit add' to track):")
    for f in untracked: print(f"  (untracked): {f}")


def checkout(commit_id):
    # הגנה: בדיקה אם יש קבצים ב-Staging לפני המעבר
    if os.path.exists(STAGING_DIR) and os.listdir(STAGING_DIR):
        print("Error: You have uncommitted changes in staging. Commit or clear them before checkout.")
        return

    source_commit = os.path.join(COMMITS_DIR, commit_id)
    if not os.path.exists(source_commit):
        print(f"Error: Commit {commit_id} not found.")
        return

    ignore_list = get_ignore_list()
    # ניקוי תיקיית עבודה
    for item in os.listdir():
        if item not in ignore_list:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)

    # שחזור מהקומיט
    for item in os.listdir(source_commit):
        if item == ".metadata": continue
        src_item = os.path.join(source_commit, item)
        if os.path.isdir(src_item):
            shutil.copytree(src_item, item)
        else:
            shutil.copy2(src_item, item)

    print(f"Switched to commit {commit_id}.")