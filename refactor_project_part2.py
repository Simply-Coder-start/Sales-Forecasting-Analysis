import os
import shutil

BASE_DIR = r"d:\Sales Forecasting Analysis"

# Attempt to copy portfolio_notebooks to notebooks
old_notebooks = os.path.join(BASE_DIR, "portfolio_notebooks")
new_notebooks = os.path.join(BASE_DIR, "notebooks")

if os.path.exists(old_notebooks) and not os.path.exists(new_notebooks):
    try:
        shutil.copytree(old_notebooks, new_notebooks)
        print("Copied portfolio_notebooks to notebooks.")
    except Exception as e:
        print(f"Error copying notebooks: {e}")

replacements = {
    "rossmann-store-sales": "data",
    "portfolio_notebooks": "notebooks",
    "app/pages": "streamlit_app/pages",
    "app.utils": "streamlit_app.utils",
    "app/main": "streamlit_app/main"
}

print("Starting Search and Replace...")

for root, dirs, files in os.walk(BASE_DIR):
    if ".git" in root or "__pycache__" in root or ".gemini" in root or "portfolio_notebooks" in root:
        continue
        
    for file in files:
        if file.endswith(".py") or file.endswith(".ipynb") or file.endswith(".md") or file.endswith(".json"):
            if file.startswith("refactor_project"):
                continue
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                changed = False
                for old_str, new_str in replacements.items():
                    if old_str in content:
                        content = content.replace(old_str, new_str)
                        changed = True
                        
                if changed:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated references in {file}")
            except Exception as e:
                pass

print("Part 2 Refactoring complete.")
