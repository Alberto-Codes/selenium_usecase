import pandas as pd
from itertools import combinations

# Load the CSV into a DataFrame
df = pd.read_csv('your_file.csv')

# Calculate the degree of uniqueness for each column
unique_ratios = {col: df[col].nunique() / len(df) for col in df.columns}

# Sort columns based on uniqueness ratio in descending order
sorted_columns = sorted(unique_ratios, key=unique_ratios.get, reverse=True)

# Function to find the minimal combination of columns for uniqueness
def find_minimal_unique_combination(dataframe, columns):
    # Iterate through combinations of columns from size 1 up to the number of columns
    for r in range(1, len(columns) + 1):
        for combo in combinations(columns, r):
            # Check if this combination of columns is unique
            if dataframe.duplicated(subset=list(combo)).sum() == 0:
                return combo  # Return the first minimal unique combination

# Identify the minimal unique set of columns using the sorted columns
minimal_unique_columns = find_minimal_unique_combination(df, sorted_columns)

# Display the uniqueness ranking and the minimal combination
print(f"Column Uniqueness Ranking: {unique_ratios}")
print(f"The smallest unique identifier set is: {minimal_unique_columns}")
