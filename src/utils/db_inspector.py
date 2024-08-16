from sqlalchemy import create_engine, inspect

def print_db_schema(db_path: str = 'your_database.db'):
    """
    Connect to the database and print the schema.
    
    Args:
        db_path (str): The path to the DuckDB database file.
    """
    # Create an engine connected to the DuckDB database
    engine = create_engine(f'duckdb:///{db_path}')

    # Use SQLAlchemy's Inspector to get information about the database schema
    inspector = inspect(engine)

    # Get the list of all tables in the database
    tables = inspector.get_table_names()

    print(f"Database schema for {db_path}:")
    print("=" * 40)
    
    # Loop through each table and print its columns
    for table_name in tables:
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  Column: {column['name']} | Type: {column['type']}")

if __name__ == "__main__":
    # Call the function with your database path
    print_db_schema('your_database.db')
