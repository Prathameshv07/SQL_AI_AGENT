# SQL AI Agent

This application converts natural language queries into SQL statements, executes them against a MySQL database, and returns the results in a structured format.

## Features

- Convert plain English questions into SQL queries
- Execute SQL queries against a MySQL database
- Display results in a user-friendly tabular format
- Error handling and query validation
- Example queries for easy testing

## Demo & Documentation

- 🎥 [Video Preview](https://drive.google.com/file/d/1x8-_YekQqEjl30rIAgeDmb2fF0PX14nr/view)
- 📄 [Project Documentation](https://drive.google.com/file/d/1GalI8UisA_3kZiSZfOA_S0GkIvQ0pE5-/view)

## Prerequisites

- Python 3.8+
- MySQL/SQL Workbench
- Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Prathameshv07/SQL_AI_AGENT.git
cd SQL_AI_AGENT
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Set up the database:
```sql
CREATE DATABASE sales;
USE sales;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY NOT NULL,
    customer_name VARCHAR(100),
    gender CHAR(1),
    age INT,
    city VARCHAR(100),
    join_date DATE
);

CREATE TABLE products (
    product_id INT PRIMARY KEY NOT NULL,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE sales (
    sale_id INT PRIMARY KEY NOT NULL,
    customer_id INT,
    product_id INT,
    sale_date DATE,
    sale_amount DECIMAL(10, 2),
    quantity_sold INT,
    region VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert sample data
INSERT INTO customers VALUES 
(1, 'John Doe', 'M', 30, 'New York', '2022-01-01'),
(2, 'Jane Smith', 'F', 28, 'Mumbai', '2022-02-15'),
(3, 'Bob Johnson', 'M', 35, 'London', '2022-03-20');

INSERT INTO products VALUES
(1, 'Laptop', 'Electronics', 999.99),
(2, 'Smartphone', 'Electronics', 699.99),
(3, 'Headphones', 'Electronics', 129.99),
(4, 'Coffee Maker', 'Appliances', 59.99),
(5, 'Running Shoes', 'Clothing', 89.99);

INSERT INTO sales VALUES
(1, 1, 1, '2023-01-15', 999.99, 1, 'North America'),
(2, 2, 3, '2023-01-20', 259.98, 2, 'Asia'),
(3, 3, 2, '2023-02-05', 699.99, 1, 'Europe'),
(4, 1, 4, '2023-02-10', 59.99, 1, 'North America'),
(5, 2, 5, '2023-03-01', 89.99, 1, 'Asia');
```

## Running the Application

1. Start the FastAPI server:
```bash
python -m app.main
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Example Queries

- List total sales per product.
- Find customers who purchased in more than one category.
- Show all sales recorded in January 2023.
- Retrieve names of customers who bought Electronics.
- What are the top 3 cities by number of customers?
- Identify products never sold.
- List customers who joined in 2022 and made at least one purchase.

## Project Structure

```
SQL AI AGENT/
├── app/
│   ├── services/
│   │   ├── ai_service.py       # Handles communication with the AI (Gemini) API
│   │   └── sql_service.py      # Manages SQL cursor operations and query execution
│   ├── database.py             # Establishes and manages database connections
│   ├── main.py                 # Entry point for running the FastAPI application
│   └── models.py               # Contains data models (Pydantic or ORM models)
├── static/
│   ├── css/
│   │   └── styles.css          # Styles for the frontend
│   └── js/
│       └── script.js           # Client-side JavaScript for dynamic behavior
├── templates/
│   └── index.html              # Main HTML template for rendering the UI
├── .env                        # Environment variables (e.g., DB credentials, API keys)
├── readme.md                   # Project instruction
├── documentation.pdf           # Project documentation
└── requirements.txt            # Python dependencies required for the project
```

## License

[![License: CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/)

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License**.  
You are free to **use, share, and adapt** the material for **non-commercial and educational purposes**, as long as proper **credit is given** and any changes are noted.

Learn more: [http://creativecommons.org/licenses/by-nc/4.0/](http://creativecommons.org/licenses/by-nc/4.0/)
