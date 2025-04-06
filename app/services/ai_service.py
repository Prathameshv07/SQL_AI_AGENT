import os
import re
import time
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from app.database import get_langchain_db

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_schema_info():
    """Returns the database schema for error reporting"""
    return """
    ### **Sales Database `sales_schema`**  

    #### **Table: `customers`**  
    _Stores customer details._  
    - **`customer_id` (INT) PRIMARY KEY NOT NULL** → Unique identifier for each customer.  
    - **`customer_name` (VARCHAR(100)) NULL** → Full name of the customer.  
    - **`gender` (CHAR(1)) NULL** → Gender of the customer (`M` for Male, `F` for Female, etc.).  
    - **`age` (INT) NULL** → Age of the customer.  
    - **`city` (VARCHAR(100)) NULL** → City where the customer resides.  
    - **`join_date` (DATE) NULL** → Date when the customer joined the platform.  

    ---

    #### **Table: `products`**  
    _Stores product details._  
    - **`product_id` (INT) PRIMARY KEY NOT NULL** → Unique identifier for each product.  
    - **`product_name` (VARCHAR(100)) NULL** → Name of the product.  
    - **`category` (VARCHAR(50)) NULL** → Category or type of the product (e.g., Electronics, Furniture, Clothing, Sports).  
    - **`price` (DECIMAL(10,2)) NULL** → Price of the product per unit.  

    ---

    #### **Table: `sales`**  
    _Stores sales transaction details._  
    - **`sale_id` (INT) PRIMARY KEY NOT NULL** → Unique identifier for each sale transaction.  
    - **`customer_id` (INT) NULL** → Foreign key referencing `customers(customer_id)`, indicating who made the purchase.  
    - **`product_id` (INT) NULL** → Foreign key referencing `products(product_id)`, indicating which product was sold.  
    - **`sale_date` (DATE) NULL** → Date when the sale occurred.  
    - **`sale_amount` (DECIMAL(10,2)) NULL** → Total amount of the sale (computed as `quantity_sold * price`).  
    - **`quantity_sold` (INT) NULL** → Number of units of the product sold in the transaction.  
    - **`region` (VARCHAR(50)) NULL** → Geographical region where the sale occurred  (e.g., South, West, North, East).  

    ---

    ### **Foreign Key Relationships**  
    - **`sales.customer_id` → `customers.customer_id`** (Each sale is associated with one customer.)  
    - **`sales.product_id` → `products.product_id`** (Each sale involves one product.)
    """

def _create_prompt(query, error_msg=None):
    """Create a unified prompt for SQL generation with optional error feedback"""
    # Base prompt with schema and query
    prompt = f"""
    You are an expert SQL query generator for MySQL databases. Your goal is to accurately convert natural language queries into efficient, optimized, and error-free MySQL SQL queries that comply with `only_full_group_by` mode.  

    ## **Database Schema**
    {get_schema_info()}

    ## **Task**
    Convert the following user query into a **correct, optimized, and executable MySQL SQL query**:

    "{query}"
    """
    
    # Add error feedback if provided
    if error_msg:
        prompt += f"""
        
        ## **Error Feedback**
        The previous attempt to generate SQL for this query failed with the following error:
        **{error_msg}**
        
        Please ensure your response addresses this specific issue.
        """
    
    # Add thinking steps to encourage careful analysis
    prompt += """
    ## **Step-by-Step Analysis Process**
    Before generating the final SQL query, follow these thinking steps:
    
    1. **Analyze the request carefully**:
       - What tables are needed?
       - What columns need to be selected?
       - Are there any filters or conditions?
       - Is aggregation or grouping needed?
       
    2. **Check for specific requirements**:
       - Is the user requesting NOT to use LIMIT or GROUP BY?
       - Are there any performance considerations?
       - Are there specific sorting requirements?
       
    3. **Match requirements to schema**:
       - Verify all tables and columns referenced exist in the schema
       - Ensure proper joins between tables
       
    4. **Consider query efficiency**:
       - Are there simpler ways to write this query?
       - Will the query be performant on large datasets?
       
    5. **Final verification**:
       - Does the query exactly match what was requested?
       - Does it follow all MySQL syntax rules?
       - Does it avoid using LIMIT/GROUP BY when specifically requested not to?
    """
    
    # Add rules and guidelines with stronger emphasis on LIMIT and GROUP BY
    prompt += """

    ---

    ## ** Important Rules & Guidelines**
    ### **1️. Output Restrictions**
    **Return ONLY the SQL query**.  
    **Do NOT include:**   
    - Any prefixes like `"SQLQuery:"`, `"Here is your query:"`, `"SELECT statement:"`, or similar.  
    - Markdown code blocks (e.g., ```sql ... ```) or backticks around the query.  
    - Any explanations, comments, or additional text.

    ---

    ### **2️. Column & Table Formatting**
    **Correct:** Use column/table names **as-is** without extra formatting unless necessary.  
    **Incorrect:** Do NOT wrap column names in single/double quotes (e.g., `"customer_id"`, `'customer_id'`).  
    **Use backticks (`) ONLY if needed** (e.g., for reserved keywords or spaces).  

    Example:  
    `SELECT id, first_name FROM users;`  
    `SELECT 'id', 'first_name' FROM 'users';`  

    ---

    ### **3️. SQL Syntax Rules (MySQL-Specific)**
    - **Use MySQL-compatible syntax** (avoid PostgreSQL-specific or other SQL dialects).  
    - **String values** must be enclosed in **single quotes `'...'`** (e.g., `WHERE category = 'Electronics'`).  
    - **Numeric values** should NOT have quotes (e.g., `WHERE age = 30`).  
    - **Date values** should be formatted correctly (e.g., `WHERE sale_date = '2023-01-01'`).  

    ---

    ### **4️. Ensuring Correct Query Structure**
    **Use `JOIN` instead of subqueries when applicable** for better performance.  
    **Ensure correct usage of aggregation functions (SUM, COUNT, AVG, etc.).**  
    **COMPLY with MySQL's `only_full_group_by` mode:**  
    - Every **non-aggregated column** in `SELECT` **MUST be in `GROUP BY`**.  
    - If `GROUP BY` is **not allowed**, use **window functions (`OVER(PARTITION BY ...)`)**.  
    **Use `ORDER BY` for sorting when needed.**  

    ---

    ### **5. CRITICAL RESTRICTIONS - READ CAREFULLY:**
    - **DO NOT use `LIMIT` unless explicitly requested** in the user query. Many queries don't need it.
    - **DO NOT use `GROUP BY` if the user specifically requests not to use it.**
    - **DO NOT return redundant columns** that aren't needed to satisfy the query.
    - **NEVER assume default values** like limits or sorting that weren't specifically requested.
    - **BE CAREFUL with dates** - use proper MySQL date functions, not string operations.
    - **VERIFY column types in the schema** before using them in functions.
    - **CHECK for NULL value handling** where appropriate.
    - **ENSURE joins won't create unexpected data duplication**.
    - **USE appropriate predicates** that match the indexing strategy.
    - **DO NOT use database-specific extensions** that might not be supported.

    ---

    ### **6. Things to keep in mind before generating SQL query:**
    - Take time to analyze what the query is asking for. Speed is not important - accuracy is.
    - Verify each column and table used exists in the schema.
    - Follow exactly what the user asks for - do not add extra filters or limits unless specified.
    - Consider data volume and performance implications of your query design.
    - When multiple approaches are possible, use the one that's most efficient and standard.
    - If the user mentions not to use a specific SQL feature (like LIMIT or GROUP BY), that's a strict requirement.
    """
    
    # Add test cases if there's no error feedback
    # (to save token usage when we're already in error recovery mode)
    if not error_msg:
        prompt += """  

        ---

        ## ** Test Cases for Different Query Types**
        ### **1️. Simple Selection**
        **Input:** "List unique product categories."  
        **Output:** `SELECT DISTINCT category FROM products;`  

        ### **2️. Aggregation with GROUP BY**
        **Input:** "What is the total sales by year?"  
        **Output:** `SELECT YEAR(s.sale_date) AS sale_year, SUM(s.sale_amount) AS total_sales FROM sales s GROUP BY YEAR(s.sale_date) ORDER BY sale_year;`  

        ### **3️. Aggregation without GROUP BY (Using Window Functions)**
        **Input:** "What is the sale amount by sale year with respect to category, gender, age, sorted by ascending product_id without using GROUP BY?"  
        **Output:**  
        SELECT 
            YEAR(s.sale_date) AS sale_year, 
            p.category, 
            c.gender, 
            c.age, 
            SUM(s.sale_amount) OVER (PARTITION BY YEAR(s.sale_date), p.category, c.gender, c.age) AS total_sales 
        FROM sales s 
        JOIN products p ON s.product_id = p.product_id 
        JOIN customers c ON s.customer_id = c.customer_id 
        ORDER BY p.product_id ASC;

        ### **4. Query without LIMIT example**
        **Input:** "Show all sales in January 2023 sorted by amount"
        **Output:** `SELECT * FROM sales WHERE MONTH(sale_date) = 1 AND YEAR(sale_date) = 2023 ORDER BY sale_amount DESC;`

        ### **5. Common mistake example - using LIMIT when not requested**
        **Input:** "Show me sales from the East region"
        **INCORRECT Output:** `SELECT * FROM sales WHERE region = 'East' LIMIT 10;`
        **CORRECT Output:** `SELECT * FROM sales WHERE region = 'East';`
        """
    
    return prompt

def clean_sql_response(text):
    """Clean the response text to extract only the SQL query"""
    # Strip any whitespace
    text = text.strip()
    
    # Remove common prefixes
    prefixes = ["SQLQuery:", "SQL Query:", "Here's the SQL query:", "Here is your query:", 
                "Query:", "SELECT statement:", "SQL:", "MySQL Query:", "Final SQL Query:"]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text.replace(prefix, "", 1).strip()
    
    # Remove markdown code blocks
    if text.startswith("```sql"):
        text = text.replace("```sql", "", 1).strip()
    elif text.startswith("```mysql"):
        text = text.replace("```mysql", "", 1).strip()
    elif text.startswith("```"):
        text = text.replace("```", "", 1).strip()
    
    if text.endswith("```"):
        text = text[:-3].strip()
    
    # Remove any trailing or leading backticks that might remain
    text = text.strip('`')
    
    # Remove any HTML-like tags that might appear
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove any leading numbers that might be used for step numbering
    text = re.sub(r'^[\d\.]+\s+', '', text)
    
    return text.strip()

def analyze_query_intent(query_text):
    """Analyze user query for specific restrictions or requirements"""
    query_lower = query_text.lower()
    restrictions = {
        "no_limit": any(term in query_lower for term in ["without limit", "no limit", "don't use limit", "do not use limit"]),
        "no_group_by": any(term in query_lower for term in ["without group by", "no group by", "don't use group by", "do not use group by"]),
        "needs_sorting": any(term in query_lower for term in ["sort", "order", "rank", "highest", "lowest", "top", "bottom", "ascending", "descending"]),
        "needs_joining": len(re.findall(r'(customers?|products?|sales?)', query_lower)) > 1,
    }
    return restrictions

def validate_sql_query(sql_query, original_query):
    """Validate the generated SQL query with enhanced checks"""
    sql_lower = sql_query.lower()
    query_intent = analyze_query_intent(original_query)
    
    # Check if it's empty
    if not sql_query:
        raise Exception("Generated SQL query is empty")
    
    # Check if it has basic SQL structure
    if not any(keyword in sql_lower for keyword in ['select', 'insert', 'update', 'delete']):
        raise Exception("Failed to generate valid SQL query - missing SQL keywords")
    
    # Enhanced validation based on query intent
    if query_intent["no_limit"] and "limit" in sql_lower:
        raise Exception("Query was generated with LIMIT despite instructions not to use it")
    
    if query_intent["no_group_by"] and "group by" in sql_lower:
        raise Exception("Query was generated with GROUP BY despite instructions not to use it")
    
    # Check if the query unnecessarily uses LIMIT when not requested
    if "limit" in sql_lower and not any(term in original_query.lower() for term in ["limit", "top", "first", "last", "recent", "newest", "latest", "few"]):
        raise Exception("Query unnecessarily uses LIMIT when not requested in the original query")
    
    # Check for balance of parentheses
    if sql_query.count('(') != sql_query.count(')'):
        raise Exception("Unbalanced parentheses in generated SQL")
    
    # Check for common syntax issues
    if "where like" in sql_lower:
        raise Exception("Invalid syntax: 'WHERE LIKE' without column name")
        
    # Check for obvious column errors based on schema
    schema_columns = {
        "customers": ["customer_id", "customer_name", "gender", "age", "city", "join_date"],
        "products": ["product_id", "product_name", "category", "price"],
        "sales": ["sale_id", "customer_id", "product_id", "sale_date", "sale_amount", "quantity_sold", "region"]
    }
    
    # Look for columns that look similar but might be typos
    for table, columns in schema_columns.items():
        table_pattern = fr'\b{table}\b|\b{table[:-1]}\b'  # Match plural or singular
        if re.search(table_pattern, sql_lower):
            # Look for potential column typos
            potential_columns = re.findall(r'[a-z_]+_(?:id|name|date|amount)', sql_lower)
            for col in potential_columns:
                # Check if similar but not exact match to any schema column
                if col not in [c for cols in schema_columns.values() for c in cols] and any(lev_dist(col, c) <= 2 for c in [c for cols in schema_columns.values() for c in cols]):
                    raise Exception(f"Potential column typo: '{col}' not found in schema")
    
    return True

def lev_dist(a, b):
    """Calculate Levenshtein distance between strings"""
    # Simple implementation for detecting similar but not identical column names
    if len(a) < len(b):
        return lev_dist(b, a)
    if not b:
        return len(a)
    
    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

async def _generate_sql_with_gemini(prompt, temperature=0.0):
    """Generate SQL using Gemini model with specified temperature"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,  # More deterministic output
            "top_k": 40,    # More deterministic output
            "max_output_tokens": 1024,
        }
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Extract SQL query from response and clean thoroughly
        sql_query = clean_sql_response(response.text)
        
        return sql_query
    except Exception as e:
        # Return error message for handling
        return f"error: {str(e)}"

async def convert_nl_to_sql(query: str) -> str:
    """Convert natural language to SQL using LangChain and Gemini with fallback"""
    try:
        # Get database connection for LangChain
        db = get_langchain_db()
        
        # Create Gemini model with low temperature for more deterministic results
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.0  # Reduced to make output more consistent
        )
        
        # Create SQL chain
        sql_chain = create_sql_query_chain(llm, db)
        
        # Generate SQL from natural language
        sql_query = sql_chain.invoke({"question": query})
        
        # Clean up the response thoroughly
        sql_query = clean_sql_response(sql_query)
        
        # Validate the SQL query
        validate_sql_query(sql_query, query)
        
        return sql_query
    except Exception as e:
        # Try the simple method as fallback
        prompt = _create_prompt(query)
        simple_result = await _generate_sql_with_gemini(prompt)
        
        # If simple method also returns an error, pass it through
        if simple_result.startswith("error:"):
            return simple_result
        
        # Validate the fallback result
        try:
            validate_sql_query(simple_result, query)
        except Exception as validation_error:
            return f"error: {str(validation_error)}"
        
        return simple_result

async def convert_nl_to_sql_with_feedback(query: str, error_msg=None, max_retries=3) -> dict:
    """
    Convert natural language to SQL with intelligent feedback-based retry
    Returns dict with status, sql (if successful), error (if failed), and retry_count
    """
    retry_count = 0
    status = "processing"
    current_error = error_msg
    sql_result = None
    temperature_schedule = [0.0, 0.1, 0.2]  # Gradually increase temperature on retries
    
    while retry_count < max_retries and status != "success":
        try:
            # If this is a retry with error feedback
            if retry_count > 0 or current_error:
                # Create prompt with error feedback
                prompt = _create_prompt(query, current_error)
                # Use temperature schedule based on retry count
                temp = temperature_schedule[min(retry_count, len(temperature_schedule)-1)]
                sql_result = await _generate_sql_with_gemini(prompt, temperature=temp)
            else:
                # First try with standard method
                sql_result = await convert_nl_to_sql(query)
            
            # If it returned an error string, raise it as an exception
            if isinstance(sql_result, str) and sql_result.startswith("error:"):
                raise Exception(sql_result[7:])  # Remove "error: " prefix
                
            # Validate the SQL result
            validate_sql_query(sql_result, query)
            
            # If we get here, the query is valid
            status = "success"
            
        except Exception as e:
            retry_count += 1
            current_error = str(e)
            
            # Make error message more specific for better feedback
            if "LIMIT" in current_error:
                current_error = f"Error: You are using LIMIT unnecessarily. The query does not need a LIMIT clause. Please remove it and try again. Original error: {current_error}"
            elif "GROUP BY" in current_error:
                current_error = f"Error: You are using GROUP BY when specifically asked not to. Please use window functions (OVER PARTITION BY) instead. Original error: {current_error}"
            
            if retry_count >= max_retries:
                status = "failed"
            else:
                status = "retrying"
                # Wait briefly before retry (optional)
                time.sleep(0.5)
    
    return {
        "status": status,
        "sql": sql_result if status == "success" else None,
        "error": current_error,
        "retry_count": retry_count,
        "query": query,
        "schema": get_schema_info()
    }
