import pandas as pd
from itertools import combinations

# Load the CSV into a DataFrame (Assuming 'table.csv' is the file)
df = pd.read_csv('table.csv')

def find_minimal_unique_combinations(df, max_combo=4):
    """
    Finds the minimal unique set of columns that identify rows uniquely.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        max_combo (int): Maximum number of columns to combine.
        
    Returns:
        dict: A dictionary mapping each row index to its minimal unique combination of columns.
    """
    # Dictionary to store the minimal unique column combinations for each row
    row_to_key = {}

    # Step 1: Rank columns by their individual uniqueness
    column_uniqueness = {col: df[col].nunique() for col in df.columns}
    sorted_columns = sorted(column_uniqueness, key=column_uniqueness.get, reverse=True)

    # Step 2: Generate all possible combinations of columns
    for r in range(1, max_combo + 1):
        for combo in combinations(sorted_columns, r):
            # Check if the combination is already sufficient for any row
            if all(idx in row_to_key for idx in range(len(df))):
                return row_to_key

            # Get the rows that this combination can uniquely identify
            unique_values = df[list(combo)].duplicated(keep=False)
            for idx, is_duplicate in enumerate(unique_values):
                if not is_duplicate and idx not in row_to_key:
                    row_to_key[idx] = combo

    return row_to_key

# Run the optimized function to find minimal unique column combinations
minimal_unique_keys = find_minimal_unique_combinations(df)

# Display the unique identifiers for each row
for row_idx, columns in minimal_unique_keys.items():
    print(f"Row {row_idx} can be uniquely identified by columns: {columns}")
