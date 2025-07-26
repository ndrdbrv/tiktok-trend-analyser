# Snowflake Database Connection Setup

This project provides a clean interface to connect to your Snowflake database and run queries from Cursor.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database Credentials

Edit the `.env` file with your actual Snowflake credentials:

```bash
# Replace these with your actual values
SNOWFLAKE_ACCOUNT=your_account_here.us-east-1
SNOWFLAKE_USER=your_username_here
SNOWFLAKE_PASSWORD=your_password_here
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ANALYTICS
SNOWFLAKE_SCHEMA=APPS_FLYER
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

### 3. Test Connection

```bash
python db_connection.py
```

## 📊 Usage Options

### Option 1: Jupyter Notebook (Recommended for Cursor)

Open `database_queries.ipynb` in Cursor and run the cells interactively:

1. Click on the notebook file
2. Run cells one by one to explore your database
3. Modify queries as needed

### Option 2: Command Line Queries

```bash
# List all tables
python quick_query.py --list-tables

# Describe a table
python quick_query.py --describe your_table_name

# Get sample data
python quick_query.py --sample your_table_name --limit 5

# Run custom query
python quick_query.py "SELECT COUNT(*) FROM your_table_name"
```

### Option 3: Python Scripts

```python
from db_connection import SnowflakeConnection, quick_query

# Quick one-off query
result = quick_query("SELECT * FROM your_table LIMIT 5")
print(result)

# Or use the connection class for multiple queries
db = SnowflakeConnection()
if db.connect():
    tables = db.list_tables()
    data = db.query("SELECT * FROM your_table LIMIT 10")
    db.close()
```

## 🔧 Features

- **Secure**: Uses environment variables for credentials
- **Easy**: Simple interface for common operations
- **Flexible**: Supports both pandas DataFrames and raw results
- **Interactive**: Works great with Jupyter notebooks in Cursor

## 📁 Files

- `db_connection.py` - Main database connection module
- `database_queries.ipynb` - Interactive Jupyter notebook
- `quick_query.py` - Command-line query tool
- `requirements.txt` - Python dependencies
- `.env` - Database credentials (you need to fill this in)

## 🛠️ Troubleshooting

1. **Connection fails**: Check your `.env` file credentials
2. **Module not found**: Run `pip install -r requirements.txt`
3. **Permission denied**: Check your Snowflake role and permissions

## 💡 Tips for Cursor

1. Use the Jupyter notebook for interactive data exploration
2. Use Cursor's AI features to help write SQL queries
3. Save frequently used queries as separate `.sql` files
4. Use the command palette (Cmd+Shift+P) to run notebook cells

Happy querying! 🎉
