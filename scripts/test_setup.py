test_setup.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("✅ All packages imported successfully!")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")

# Test basic functionality
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
print("✅ Pandas DataFrame created successfully!")
print(df.head())