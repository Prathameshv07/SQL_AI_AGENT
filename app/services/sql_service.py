from app.database import get_db_connection
import mysql.connector
from typing import List, Dict, Any
import re

def sanitize_sql_query(sql_query: str) -> str:
    """Remove any markdown formatting or code blocks from the SQL query"""
    # Remove markdown SQL formatting if present
    sql_query = sql_query.strip()
    if sql_query.startswith("```sql"):
        sql_query = sql_query.replace("```sql", "", 1).strip()
    if sql_query.startswith("```"):
        sql_query = sql_query.replace("```", "", 1).strip()
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3].strip()
    
    # Remove any inline comments
    sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    
    return sql_query

def execute_sql_query(sql_query: str) -> List[Dict[str, Any]]:
    """Execute SQL query and return results as a list of dictionaries"""
    try:
        # Sanitize the SQL query
        sanitized_query = sanitize_sql_query(sql_query)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(sanitized_query)
        results = cursor.fetchall()
        
        # Process datetime and other non-serializable objects
        processed_results = []
        for row in results:
            processed_row = {}
            for key, value in row.items():
                if isinstance(value, (bytes, memoryview)):
                    processed_row[key] = str(value)
                else:
                    processed_row[key] = value
            processed_results.append(processed_row)
        
        # Close connections
        cursor.close()
        conn.close()
        
        return processed_results
    except mysql.connector.Error as e:
        raise Exception(f"SQL execution error: {str(e)}")