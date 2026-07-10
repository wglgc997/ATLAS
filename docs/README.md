# Link Checker - Development Commands (V1)

This document contains the most common commands used during the development of the Link Checker project.

---

# Python Virtual Environment

## Create a virtual environment

Windows

```bash
python -m venv .venv
```

Linux / macOS

```bash
python3 -m venv .venv
```

---

## Activate the virtual environment

Windows (CMD)

```cmd
.venv\Scripts\activate.bat
```

Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

## Deactivate the virtual environment

```bash
deactivate
```

---

# Dependencies

## Install project dependencies

```bash
pip install -r requirements.txt
```

## Install a new package

```bash
pip install <package_name>
```

Example

```bash
pip install requests
```

---

## Update requirements.txt

```bash
pip freeze > requirements.txt
```

---

# Running the Application

## Scan a single URL

```bash
python main.py --url https://example.com
```

## Scan multiple URLs from a file

```bash
python main.py --file data/links.txt
```

## Set the request timeout

```bash
python main.py --url https://example.com --timeout 10
```

## Configure the number of worker threads

```bash
python main.py --file data/links.txt --threads 20
```

## Save results to a CSV file

```bash
python main.py --file data/links.txt --csv outputs/output.csv
```

## Display only broken links

```bash
python main.py --file data/links.txt --only-broken
```

---

# Dataset Cleaning

Run the dataset cleaning process

```bash
python dataset_clean.py outputs/output.csv
```

Specify an output file

```bash
python dataset_clean.py outputs/output.csv --output outputs/output_clean.csv
```

---

# Analytics

Analyze a CSV dataset

```bash
python analytics.py outputs/output_clean.csv
```

---

# Testing

Run all tests

```bash
pytest
```

Run tests with verbose output

```bash
pytest -v
```

Run a specific test file

```bash
pytest tests/test_checker.py
```

Run a single test

```bash
pytest tests/test_checker.py::test_check_link
```

Generate a coverage report

```bash
pytest --cov=src
```

---

# Code Formatting

Format the project

```bash
black .
```

Check formatting only

```bash
black --check .
```

---

# Ruff

Run static analysis

```bash
ruff check .
```

Automatically fix issues

```bash
ruff check . --fix
```

---

# Type Checking

Run MyPy

```bash
mypy src
```

---

# Git

Check repository status

```bash
git status
```

Stage all changes

```bash
git add .
```

Commit changes

```bash
git commit -m "Your commit message"
```

Push changes

```bash
git push
```

Pull the latest changes

```bash
git pull
```

Switch branches

```bash
git switch <branch-name>
```

Create and switch to a new branch

```bash
git switch -c feature/new-feature
```

---

# Project Structure

```
link-checker/
│
├── main.py
├── analytics.py
├── dataset_clean.py
├── requirements.txt
│
├── src/
├── tests/
├── outputs/
└── data/
```

---

# Typical Development Workflow

```text
Activate virtual environment
            │
            ▼
Install dependencies
            │
            ▼
Run Link Checker
            │
            ▼
Generate CSV output
            │
            ▼
Clean dataset
            │
            ▼
Run analytics
            │
            ▼
Execute tests
            │
            ▼
Run Black
            │
            ▼
Run Ruff
            │
            ▼
Run MyPy
            │
            ▼
Commit changes
            │
            ▼
Push to GitHub
```

---

# Pre-Commit Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Application runs successfully
- [ ] Tests passing
- [ ] `black .`
- [ ] `ruff check .`
- [ ] `mypy src`
- [ ] Commit created
- [ ] Changes pushed

---

# Future Versions

## V2

- FastAPI backend
- PostgreSQL
- SQLAlchemy
- React dashboard
- Docker
- Scheduled scans
- Email reports
- Scan history
- REST API
- Authentication