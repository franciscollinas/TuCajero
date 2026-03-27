import os
import re
from pathlib import Path

ui_dir = Path(r"c:\Users\UserMaster\Documents\Proyectos\TuCajeroPOS\tucajero\ui")
main_file = Path(r"c:\Users\UserMaster\Documents\Proyectos\TuCajeroPOS\tucajero\main.py")

def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Fix imports from utils.theme
    # sometimes it's multiline, so we can just replace 'btn_success' and 'btn_style'
    content = re.sub(r',\s*btn_success', '', content)
    content = re.sub(r',\s*btn_style', '', content)
    content = re.sub(r'btn_success,\s*', '', content)
    content = re.sub(r'btn_style,\s*', '', content)

    # 2. Replace usages
    content = content.replace('btn_success()', 'btn_primary()')
    
    # 3. Replace btn_style(...) with btn_secondary() or btn_primary()
    # It takes arguments like btn_style("accent"), btn_style("warning") etc.
    content = re.sub(r'btn_style\([^)]*\)', 'btn_secondary()', content)
    content = content.replace('btn_style()', 'btn_secondary()')

    # 4. Remove inline styles purely setting colors on buttons
    # Example: button.setStyleSheet("background-color: transparent;")
    # We will try to find btn.setStyleSheet("...") and if it's a known button style we replace it
    # But usually it's better to just manually check those.
    # We will remove instances like `setStyleSheet("background: transparent; border: none;")` matching button-like variables?
    # Or we can just find `.setStyleSheet(...)` on specific buttons.
    
    # Let's fix specific seen patterns:
    # `setStyleSheet("background: transparent;")`
    # Let's write the modified content back
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Modified {file_path.name}")

for py_file in ui_dir.glob("*.py"):
    fix_file(py_file)
if main_file.exists():
    fix_file(main_file)

print("Done automatic replacements.")
