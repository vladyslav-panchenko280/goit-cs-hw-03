def safe_execute(cursor, query, params=None, error_message=None):
    """Safely execute SQL query with error handling
    
    Args:
        cursor: Database cursor
        query: SQL query string
        params: Query parameters (optional)
        error_message: Custom error message (optional)
        
    Returns:
        True if successful, False otherwise
        
    Usage:
        safe_execute(cursor, "INSERT INTO users (name) VALUES (%s)", ("John",), "Failed to insert user")
    """
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return True
    except Exception as e:
        if error_message:
            print(f"{error_message}: {e}")
        else:
            print(f"Query execution error: {e}")
        return False

