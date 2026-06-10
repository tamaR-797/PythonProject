# CodeGuard-WIT: Static Code Analysis & Version Control System

An integrated system combining a local version control tool (CLI) with a centralized server for software quality assurance and static code analysis, built on a client-server architecture.

---

## 📂 Project Files Explained

The project consists of two main directories that communicate with each other over the network:

### 1. Local Client Directory (`Python_Project-main`)
This is the workspace where the developer manages their source code:
* **`wit.py`**: The Command Line Interface (CLI). This file captures your terminal commands (such as `init`, `add`, `push`) and routes them to the appropriate application logic.
* **`logic.py`**: The "brain" of the client application. This file contains the `push()` function. It scans the staging directory, collects Python files, transmits them over the network to the server using two distinct HTTP POST requests, downloads the dynamic chart image, and clears the staging area upon success.
* **`test.py`**: Your validation test file. It contains intentional code flaws (e.g., Hebrew variable names, long functions, and unused variables) to verify that the analysis engine detects anomalies correctly.

### 2. Centralized Analysis Server Directory (`codeguard_server`)
This is the backend service that inspects code quality and generates reporting structures:
* **`main.py`**: The server application built with **FastAPI**. It receives incoming source files from the WIT client, parses their structural layout using the **AST** (Abstract Syntax Tree) module without executing the code, uncovers rule violations, and renders a visual bar chart (PNG) utilizing **Matplotlib** running in a headless `Agg` background context.

---

## 🛡️ Static Analysis Rules

The server's AST engine parses the source code to flag five structural and stylistic issues:
1. **File Length**: Any source file exceeding 200 total lines triggers an alert (overly long files degrade overall system maintainability).
2. **Function Length**: Every function definition block (`ast.FunctionDef`) is measured from its declaration line to its termination. Functions exceeding 20 lines trigger a warning.
3. **Missing Docstring**: The system utilizes `ast.get_docstring` to check whether an introductory documentation block (`"""docstring"""`) is defined at the start of each function body.
4. **Unused Variables**: Within each function scope, the module differentiates between variables defined in an assignment context (`ast.Store`) and those retrieved for execution (`ast.Load`). Any variable initialized but never referenced is reported as dead code.
5. **Hebrew Character Detection**: Variable identifiers (`ast.Name`) are scanned using a Regular Expression (**Regex**) mapping to the Hebrew Unicode spectrum `[\u0590-\u05fe]` to enforce universal, international naming standards.

---

## 🛠️ Prerequisites & Installation

Before spinning up the application, ensure you have Python 3.10 or higher installed, then install the necessary dependencies via your terminal:

```bash
pip install fastapi uvicorn python-multipart matplotlib requests
cd C:\Users\localadmin\Documents\GitHub\PythonProject\codeguard_server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
cd C:\Users\localadmin\Documents\GitHub\PythonProject\Python_Project-main
python wit.py add test.py
python wit.py push
