import pandas as pd
import os

# Demo data
data = {
    'col1': [1, [2, 3, 4]],
    'col2': ['a', 'b']
}

df = pd.DataFrame(data)

# Folder path
f_path = r"C:\Users\augus\BCI_Stuff\Aspen"  # Replace with your actual folder path

# Output file path
out_file = os.path.join(f_path, 'test.tsv')

# Save as TSV with delimiter='\t'
df.to_csv(out_file, sep='\t', index=False)