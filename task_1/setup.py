from pathlib import Path
from utils import get_db_connection

SQL_DIR = Path(__file__).parent / 'sql'

def read_sql_file(file_path):
    """Read SQL file and return its content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def execute_sql_file(connection, file_path):
    """Execute SQL from file"""
    sql_script = read_sql_file(file_path)
    cursor = connection.cursor()
    try:
        cursor.execute(sql_script)
        connection.commit()
        print(f"Successfully executed: {file_path.name}")
    except Exception as e:
        connection.rollback()
        print(f"Error executing {file_path.name}: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main function to execute SQL files"""
    sql_files = [
        'init.sql',
    ]
    
    connection = get_db_connection()
    try:
        for sql_file in sql_files:
            file_path = SQL_DIR / sql_file
            if file_path.exists():
                execute_sql_file(connection, file_path)
            else:
                print(f"Warning: {sql_file} not found, skipping...")
        
        print("\nAll SQL scripts executed successfully!")
    except Exception as e:
        print(f"\nFatal error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()