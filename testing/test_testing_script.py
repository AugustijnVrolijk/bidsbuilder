import pandas as pd
import os

# Demo data
data = {
    'col1': [1, [2, 3, 4]],
    'col2': ['a', 'b']
}

df = pd.DataFrame(data)

# --- Per-column list delimiters ---
# Define how to join lists for each column (defaults to comma if not specified)
list_delimiters = {
    'col1': ';',   # Use semicolon inside col1 lists
    'col2': ','    # Could define something different for col2 if needed
}

def stringify_lists(cell, col_name):
    """Convert lists into strings using column-specific delimiter."""
    if isinstance(cell, list):
        delim = list_delimiters.get(col_name, ',')
        return delim.join(map(str, cell))
    return cell

# Apply conversion
for col in df.columns:
    df[col] = df[col].apply(lambda x: stringify_lists(x, col))

# Folder path
f_path = r"C:\Users\augus\BCI_Stuff\Aspen"  # Replace with your actual folder path

# Output file path
out_file = os.path.join(f_path, 'test.tsv')

# Save as TSV with tab delimiter
df.to_csv(out_file, sep='\t', index=False)