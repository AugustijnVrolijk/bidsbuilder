#!/usr/bin/env python3
"""
generate_api_rst.py

Recursively generates .rst files for all .py modules in your package
and updates api.rst with a toctree.
"""

import os

# -------------------------
# Argument parser
# -------------------------

# Path to your source Python package
SRC_DIR = "../src/bidsbuilder"
# Folder where .rst files will be generated
T_RST_DIR = "source"
# Path to the main api.rst file
API_RST = os.path.join(T_RST_DIR, "api.rst")
RST_DIR = os.path.join(T_RST_DIR, "_autogen")
# Make sure RST_DIR exists
os.makedirs(RST_DIR, exist_ok=True)

# Collect all .py files (ignore __init__.py)
py_files = []
for root, dirs, files in os.walk(SRC_DIR):
    # Skip hidden folders
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    for f in files:
        if f.endswith(".py") and f != "__init__.py":
            full_path = os.path.join(root, f)
            py_files.append(full_path)

# Map each .py file to a relative module path
module_rst_files = []

for py_path in py_files:
    # Compute module name (e.g., bidsbuilder.schema.checking)
    rel_path = os.path.relpath(py_path, SRC_DIR)
    module_name = rel_path.replace(os.sep, ".").replace(".py", "")
    rst_file_name = rel_path.replace(os.sep, "_").replace(".py", ".rst")
    rst_file_path = os.path.join(RST_DIR, rst_file_name)

    module_rst_files.append((module_name, rst_file_name))

    # Generate the .rst file
    with open(rst_file_path, "w", encoding="utf-8") as f:
        f.write(f"{module_name}\n")
        f.write("=" * len(module_name) + "\n\n")
        f.write(f".. automodule:: bidsbuilder.{module_name}\n")
        f.write("    :members:\n")
        f.write("    :undoc-members:\n")
        f.write("    :show-inheritance:\n")

# Generate api.rst with a toctree
with open(API_RST, "w", encoding="utf-8") as f:
    f.write("API Reference\n")
    f.write("=============\n\n")
    f.write(".. toctree::\n")
    f.write("   :maxdepth: 4\n\n")
    for _, rst_name in module_rst_files:
        f.write(f"   {rst_name}\n")

print(f"[INFO] Generated {len(module_rst_files)} .rst files in {RST_DIR}")
print(f"[INFO] Updated {API_RST}")
