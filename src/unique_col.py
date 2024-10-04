import pandas as pd
from itertools import combinations
import hashlib

# Load the CSV into a DataFrame
df = pd.read_csv('table.csv')

def hash_combination(row, columns):
    """Generate a hash for a given row based on the specified columns."""
    combined_values = ''.join([str(row[col]) for col in columns])
    return hashlib.md5(combined_values.encode()).hexdigest()

def find_minimal_unique_combinations(df, max_combo=4):
    """
    Find the minimal unique set of columns that identify rows uniquely using hash-based detection.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        max_combo (int): Maximum number of columns to combine.
        
    Returns:
        dict: A dictionary mapping each row index to its minimal unique combination of columns.
    """
    # Step 1: Rank columns by their individual uniqueness
    column_uniqueness = {col: df[col].nunique() for col in df.columns}
    sorted_columns = sorted(column_uniqueness, key=column_uniqueness.get, reverse=True)

    # Step 2: Generate combinations and compute hashes
    min_unique_columns = None
    min_column_length = float('inf')

    # Store the hash uniqueness score for each combination
    for r in range(1, max_combo + 1):
        for combo in combinations(sorted_columns, r):
            # Generate a hash for each row based on this column combination
            hash_set = set(df.apply(lambda row: hash_combination(row, combo), axis=1))

            # Check if this combination is unique for all rows
            if len(hash_set) == len(df):
                if len(combo) < min_column_length:
                    min_unique_columns = combo
                    min_column_length = len(combo)

    return min_unique_columns

# Find the minimal unique combination using hash-based optimization
minimal_unique_combination = find_minimal_unique_combinations(df)

# Display the minimal unique column combination
print(f"The smallest unique identifier set is: {minimal_unique_combination}")
