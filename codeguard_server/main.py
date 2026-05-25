from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
import ast
import re

# הגדרה קריטית למניעת שגיאות 500 בשרתים (חובה לפני ייבוא pyplot)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

app = FastAPI()

def analyze_code_quality(file_content: str, filename: str):
    alerts = []
    metrics = {"too_long_funcs": 0, "missing_docs": 0, "unused_vars": 0, "hebrew_vars": 0}
    
    lines = file_content.splitlines()
    total_lines = len(lines)
    if total_lines > 200:
        alerts.append(f"File '{filename}' is too long ({total_lines} lines). Keep it under 200 lines.")

    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = node.end_lineno - node.lineno + 1
                if func_length > 20:
                    alerts.append(f"Function '{node.name}' in '{filename}' is too long ({func_length} lines).")
                    metrics["too_long_funcs"] += 1
                
                if ast.get_docstring(node) is None:
                    alerts.append(f"Function '{node.name}' in '{filename}' is missing a docstring.")
                    metrics["missing_docs"] += 1

                defined_vars = set()
                used_vars = set()
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Store):
                        defined_vars.add(sub_node.id)
                    elif isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Load):
                        used_vars.add(sub_node.id)
                
                unused_vars = defined_vars - used_vars
                for var in unused_vars:
                    alerts.append(f"Variable '{var}' in '{node.name}' ({filename}) is defined but never used.")
                    metrics["unused_vars"] += 1

            if isinstance(node, ast.Name):
                if re.search(r'[\u0590-\u05fe]', node.id):
                    alerts.append(f"Variable name '{node.id}' in '{filename}' contains Hebrew characters.")
                    metrics["hebrew_vars"] += 1
                    
    except SyntaxError:
        alerts.append(f"File '{filename}' has a syntax error.")

    return alerts, metrics

@app.post("/alerts")
async def receive_alerts(files: List[UploadFile] = File(...)):
    all_alerts = []
    for file in files:
        content = (await file.read()).decode("utf-8")
        file_alerts, _ = analyze_code_quality(content, file.filename)
        all_alerts.extend(file_alerts)
        
    return {"status": "success", "total_issues_found": len(all_alerts), "alerts": all_alerts}

@app.post("/analyze")
async def receive_analyze(files: List[UploadFile] = File(...)):
    combined_metrics = {"Too Long\nFunctions": 0, "Missing\nDocstrings": 0, "Unused\nVariables": 0, "Hebrew\nVariables": 0}
    
    for file in files:
        content = (await file.read()).decode("utf-8")
        _, file_metrics = analyze_code_quality(content, file.filename)
        combined_metrics["Too Long\nFunctions"] += file_metrics["too_long_funcs"]
        combined_metrics["Missing\nDocstrings"] += file_metrics["missing_docs"]
        combined_metrics["Unused\nVariables"] += file_metrics["unused_vars"]
        combined_metrics["Hebrew\nVariables"] += file_metrics["hebrew_vars"]

    # יצירת הגרף הוויזואלי
    plt.figure(figsize=(8, 4))
    categories = list(combined_metrics.keys())
    values = list(combined_metrics.values())
    
    # עיצוב וצבעים לעמודות הגרף
    plt.bar(categories, values, color=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'], edgecolor='grey')
    plt.title("Code Guard - Security & Quality Metrics", fontsize=14, fontweight='bold')
    plt.ylabel("Issues Count", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # שמירת הגרף ישירות לזיכרון השרת (RAM) כקובץ PNG בינארי
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=100)
    img_buf.seek(0)
    plt.close()  # שחרור הזיכרון של הגרף כדי למנוע קריסה בריצה הבאה
    
    return StreamingResponse(img_buf, media_type="image/png")