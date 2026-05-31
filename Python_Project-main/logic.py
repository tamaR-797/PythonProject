import os
import shutil
import requests

# הגדרת נתיבי תיקיות ה-WIT
WIT_DIR = ".wit"
STAGING_DIR = os.path.join(WIT_DIR, "staging")


def init():
    """מאתחל מאגר WIT חדש ומייצר את תיקיית ה-staging"""
    if os.path.exists(WIT_DIR):
        print("Error: Already a WIT repository.")
        return
    os.makedirs(STAGING_DIR, exist_ok=True)
    print(f"Initialized empty WIT repository in {os.path.abspath(WIT_DIR)}")


def add(path):
    """מעתיק קובץ או תיקייה אל אזור ה-staging"""
    if not os.path.exists(WIT_DIR):
        print("Error: Not a WIT repository. Run 'init' first.")
        return

    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return

    # יצירת נתיב היעד בתוך תיקיית ה-staging
    destination = os.path.join(STAGING_DIR, os.path.basename(path))

    if os.path.isdir(path):
        if os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(path, destination)
    else:
        shutil.copy2(path, destination)

    print(f"Added '{path}' to staging area.")


def push():
    """שולח את הקבצים מ-staging לשרת ומנקה אותו בסיום מוצלח"""
    if not os.path.exists(WIT_DIR):
        print("Error: Not a WIT repository. Run 'init' first.")
        return

    url_alerts = "http://127.0.0.1:8000/alerts"
    url_analyze = "http://127.0.0.1:8000/analyze"

    # סריקה ואיסוף רק של קבצי פייתון מתוך תיקיית ה-Staging
    py_files = []
    for root, dirs, files in os.walk(STAGING_DIR):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))

    if not py_files:
        print("Nothing to push. Staging area has no Python (.py) files.")
        return

    print(f"Found {len(py_files)} Python file(s) in staging. Sending to CodeGuard...")

    files_payload = []
    opened_files = []
    success_flag = False

    try:
        # פתיחת כל הקבצים לקריאה בינארית לצורך שליחה ברשת
        for file_path in py_files:
            f = open(file_path, 'rb')
            opened_files.append(f)
            rel_name = os.path.relpath(file_path, STAGING_DIR)
            files_payload.append(('files', (rel_name, f)))

        # פנייה ראשונה: קבלת פירוט האזהרות הטקסטואליות לטרמינל
        response_alerts = requests.post(url_alerts, files=files_payload)
        print("\n--- CODEGUARD ALERTS ---")
        print("Server Response:", response_alerts.json())

        # איפוס סמן הקריאה בקבצים הפתוחים לצורך שליחה מחדש בבקשה השנייה
        for f in opened_files:
            f.seek(0)

        # פנייה שנייה: קבלת קובץ תמונת הגרף הסטטיסטי (PNG) ושמירתו
        print("\nGenerating visual metrics chart (PNG)...")
        response_analyze = requests.post(url_analyze, files=files_payload)

        if response_analyze.status_code == 200:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_chart_path = os.path.join(current_dir, "code_quality_metrics.png")

            # מנגנון חסין: אם הקובץ נעול על ידי ווינדוס, ניצור קובץ ממוספר במקום לקרוס
            counter = 1
            while True:
                try:
                    with open(output_chart_path, "wb") as chart_file:
                        chart_file.write(response_analyze.content)
                    break  # הצלחנו לכתוב, יוצאים מהלולאה
                except (OSError, PermissionError):
                    # אם הקובץ נעול, ננסה שם כמו code_quality_metrics_1.png
                    output_chart_path = os.path.join(current_dir, f"code_quality_metrics_{counter}.png")
                    counter += 1

            filename_saved = os.path.basename(output_chart_path)
            print(f" 📊 Success: Visual chart saved as '{filename_saved}' in your repository!")
            success_flag = True
        else:
            print("Failed to generate chart. Server returned status:", response_analyze.status_code)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Is FastAPI running?")
    finally:
        # סגירה מסודרת של כל הקבצים הפתוחים בזיכרון של מערכת ההפעלה כדי שווינדוס ישחרר אותם
        for f in opened_files:
            f.close()

    # רק אחרי שהקבצים נסגרו באופן סופי, ננקה את ה-Staging
    if success_flag:
        try:
            for item in os.listdir(STAGING_DIR):
                item_path = os.path.join(STAGING_DIR, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print(" 🧹 Staging area cleared successfully.")
        except Exception as e:
            print(f"Warning: Could not clear staging area: {e}")