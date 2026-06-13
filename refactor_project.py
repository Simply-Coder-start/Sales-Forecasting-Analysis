import os
import shutil

BASE_DIR = r"d:\Sales Forecasting Analysis"

def safe_rename(old_name, new_name):
    old_path = os.path.join(BASE_DIR, old_name)
    new_path = os.path.join(BASE_DIR, new_name)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        print(f"Renamed {old_name} -> {new_name}")

def safe_mkdir(dirname):
    path = os.path.join(BASE_DIR, dirname)
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created {dirname}/")

def safe_move(src_rel, dst_rel):
    src = os.path.join(BASE_DIR, src_rel)
    dst = os.path.join(BASE_DIR, dst_rel)
    if os.path.exists(src):
        # ensure destination dir exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        print(f"Moved {src_rel} -> {dst_rel}")

print("Starting Refactor...")

# 1 & 2. Create dirs & Move files
safe_mkdir("reports")
safe_mkdir("docs")

safe_move(r"rossmann-store-sales\eda_report.html", r"reports\eda_report.html")
safe_move("final_academic_report.md", r"reports\final_academic_report.md")
safe_move("viva_presentation_slides.md", r"docs\viva_presentation_slides.md")

# Create dummy architecture.png
with open(os.path.join(BASE_DIR, "docs", "architecture.png"), "wb") as f:
    pass

# 3. Rename dirs
safe_rename("rossmann-store-sales", "data")
safe_rename("app", "streamlit_app")
safe_rename("portfolio_notebooks", "notebooks")

# 4. Search and Replace
replacements = {
    "rossmann-store-sales": "data",
    "portfolio_notebooks": "notebooks",
    "app/pages": "streamlit_app/pages",
    "app.utils": "streamlit_app.utils"
}

for root, dirs, files in os.walk(BASE_DIR):
    if ".git" in root or "__pycache__" in root or ".gemini" in root:
        continue
        
    for file in files:
        if file.endswith(".py") or file.endswith(".ipynb") or file.endswith(".md") or file.endswith(".json"):
            if file == "refactor_project.py":
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

print("Refactoring complete.")
