from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
from typing import List
import ast
import re

app = FastAPI()


def analyze_code_quality(file_content: str, filename: str):
    alerts = []
    metrics = {"too_long_funcs": 0, "missing_docs": 0, "unused_vars": 0, "hebrew_vars": 0}

    lines = file_content.splitlines()
    total_lines = len(lines)
    if total_lines > 200:
        alerts.append(f"File '{filename}' is too long ({total_lines} lines).")

    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = node.end_lineno - node.lineno + 1
                if func_length > 20:
                    alerts.append(f"Function '{node.name}' in '{filename}' is too long.")
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
                    alerts.append(f"Variable '{var}' in '{node.name}' is defined but never used.")
                    metrics["unused_vars"] += 1

            if isinstance(node, ast.Name):
                if re.search(r'[\u0590-\u05fe]', node.id):
                    alerts.append(f"Variable name '{node.id}' contains Hebrew characters.")
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
    combined_metrics = {"Too Long Functions": 0, "Missing Docstrings": 0, "Unused Variables": 0, "Hebrew Variables": 0}

    for file in files:
        content = (await file.read()).decode("utf-8")
        _, file_metrics = analyze_code_quality(content, file.filename)
        combined_metrics["Too Long Functions"] += file_metrics["too_long_funcs"]
        combined_metrics["Missing Docstrings"] += file_metrics["missing_docs"]
        combined_metrics["Unused Variables"] += file_metrics["unused_vars"]
        combined_metrics["Hebrew Variables"] += file_metrics["hebrew_vars"]

    # יצירת גרף עמודות טקסטואלי (ASCII Bar Chart) חסין שגיאות
    report = "==================================================\n"
    report += "         CODEGUARD QUALITY METRICS REPORT        \n"
    report += "==================================================\n\n"

    for key, val in combined_metrics.items():
        bar = "█" * val  # מייצר עמודה ויזואלית לפי כמות השגיאות
        report += f"{key:<22} | {bar} ({val})\n"

    report += "\n=================================================="

    return PlainTextResponse(report)