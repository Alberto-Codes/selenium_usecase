from py_keys import get_keys
import pandas as pd

# Step 1: Load your data into a DataFrame
df = pd.read_csv("table.csv")

# Step 2: Use Py-Keys to get initial candidate keys
initial_keys = get_keys(df)
print("Initial candidate keys:", initial_keys)

# Step 3: Filter down using custom logic for minimal unique sets
minimal_keys = []  # This will store the refined set of minimal unique keys

# Sort by length to ensure minimal sets are found first
sorted_keys = sorted(initial_keys, key=len)

# Step 4: Check for sub-key relationships and only keep minimal ones
for key in sorted_keys:
    if not any(set(key).issubset(set(other)) for other in minimal_keys):
        minimal_keys.append(key)

print("Minimal unique key combinations:", minimal_keys)
