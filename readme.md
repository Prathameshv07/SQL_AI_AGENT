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

4. Create your `.env` file from the template and fill in your Gemini API key and MySQL credentials:
```bash
cp .env.example .env
```

5. Create the database and load the sample data (products, customers and sales tables):
```bash
mysql -u root -p -e "CREATE DATABASE sales;"
mysql -u root -p sales < sample_data_all_quoted.sql
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
SQL_AI_AGENT/
├── app/
│   ├── services/
│   │   ├── ai_service.py        # Gemini / LangChain natural-language → SQL with error-feedback retries
│   │   └── sql_service.py       # Executes SQL and formats results
│   ├── database.py              # MySQL + LangChain SQLDatabase connections
│   ├── main.py                  # FastAPI entry point
│   └── models.py                # Pydantic request/response models
├── static/                      # CSS and client-side JavaScript
├── templates/index.html         # Web UI
├── sample_data_all_quoted.sql   # Schema + sample data
├── .env.example                 # Environment variable template
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

## Citation

If you use or build on this project, please cite it. GitHub's **"Cite this repository"** button (generated from [`CITATION.cff`](CITATION.cff)) provides APA and BibTeX formats.

```bibtex
@software{vaidya_sqlaiagent_2025,
  author = {Vaidya, Prathamesh Sarjerao},
  title  = {SQL AI Agent: Natural-Language to SQL Querying with Gemini},
  year   = {2025},
  url    = {https://github.com/Prathameshv07/SQL_AI_AGENT}
}
```

## License

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

© 2025 Prathamesh Sarjerao Vaidya. This work is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/). You may share and adapt it for **non-commercial** purposes, provided you **give appropriate credit** and indicate any changes. See [LICENSE](LICENSE) for details.
