import os
import requests
import shutil

# הגדרת נתיבי תיקיות ה-WIT (ודאו שזה תואם להגדרות שלכן בשאר הפרויקט)
WIT_DIR = ".wit"
STAGING_DIR = os.path.join(WIT_DIR, "staging")

def push():
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
            output_chart_name = "code_quality_metrics.png"
            with open(output_chart_name, "wb") as chart_file:
                chart_file.write(response_analyze.content)
            print(f" 📊 Success: Visual chart saved as '{output_chart_name}' in your repository!")
            
            # ניקוי וריקון אוטומטי של תיקיית ה-Staging לאחר שהכל עבר בהצלחה
            for item in os.listdir(STAGING_DIR):
                item_path = os.path.join(STAGING_DIR, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print(" 🧹 Staging area cleared successfully.")
            
        else:
            print("Failed to generate chart. Server returned status:", response_analyze.status_code)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Is FastAPI running?")
    finally:
        # סגירה מסודרת של כל הקבצים הפתוחים בזיכרון של מערכת ההפעלה
        for f in opened_files:
            f.close()