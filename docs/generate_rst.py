#!/usr/bin/env python3
"""
generate_api_rst.py

Recursively generates .rst files for all .py modules in your package
and updates api.rst with a toctree.
"""

import os
from pathlib import Path
# -------------------------
# Argument parser
# -------------------------

# Path to your source Python package
SRC_DIR = Path("../src/bidsbuilder")
MODULE_NAME = SRC_DIR.name
SRC_DIR = SRC_DIR.resolve()
# Folder where .rst files will be generated
T_RST_DIR = "source"
# Path to the main api.rst file
HOLD_DIR = "_autogen"
API_RST = os.path.join(T_RST_DIR, "api.rst")
RST_DIR = os.path.join(T_RST_DIR, HOLD_DIR)
# Make sure RST_DIR exists
os.makedirs(RST_DIR, exist_ok=True)

# Collect all .py files (ignore __init__.py)
py_files = []
for c_file in SRC_DIR.rglob("*.py"):
    # Skip hidden folders
    c_stem = c_file.stem
    if c_stem != "__init__":
            py_files.append(c_file)

if len(py_files) == 0:
    raise NotADirectoryError(f"{SRC_DIR} is not pointing to the correct dir. Please navigate to bidsbuilder/docs")

# Map each .py file to a relative module path
module_rst_files = []

for py_path in py_files:
    # Compute module name (e.g., bidsbuilder.schema.checking)
    rel_path = os.path.relpath(py_path, SRC_DIR)
    module_name = rel_path.replace(os.sep, ".").replace(".py", "")
    rst_file_name = f"{MODULE_NAME}.{module_name}"
    rst_file_path = os.path.join(RST_DIR, f"{rst_file_name}.rst")
    module_rst_files.append(rst_file_name)

    # Generate the .rst file
    with open(rst_file_path, "w", encoding="utf-8") as f:
        f.write(f"{rst_file_name}\n")
        f.write("=" * len(rst_file_name) + "\n\n")
        f.write(f".. automodule:: {rst_file_name}\n")
        f.write("    :members:\n")
        f.write("    :undoc-members:\n")
        f.write("    :show-inheritance:\n")
"""
# Generate api.rst with a toctree
with open(API_RST, "w", encoding="utf-8") as f:
    f.write("API Reference\n")
    f.write("=============\n\n")
    f.write(".. toctree:: _autogen\n")
    f.write("   :maxdepth: 4\n\n")
    for rst_name in module_rst_files:
        f.write(f"   {rst_name}\n")
"""
print(f"[INFO] Generated {len(module_rst_files)} .rst files in {RST_DIR}")
# print(f"[INFO] Updated {API_RST}")
