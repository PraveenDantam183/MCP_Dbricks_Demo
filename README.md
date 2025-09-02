# Databricks MCP Demo

Integrate the **Model Context Protocol (MCP)** with **Databricks SQL Warehouse** and **Unity Catalog** so an AI agent (e.g., Claude Desktop) can list tables, run read-only queries, and perform simple inserts/updates/deletes via natural-language tools.

---

## Features

- **list_tables** — list tables in a catalog/schema  
- **sql_query** — run read-only SQL (`SELECT / SHOW / DESCRIBE`)  
- **insert_row** — insert one row into a table  
- **update_rows** — update rows with a `WHERE` clause  
- **delete_rows** — delete rows with a `WHERE` clause

---

## 📂 Project Structure

```
mcp-databricks/
├─ server.py            # MCP server with tools (list, query, insert, update, delete)
├─ requirements.txt     # Python dependencies
├─ .env                 # Example environment variables (copy to .env and fill)
├─ README.md            # This document
└─ sql/
   └─ setup.sql         # Example SQL script to create sample tables & data
```

---


---

## Prerequisites

- Python **3.10+**
- Databricks **SQL Warehouse** (ODBC/JDBC endpoint)
- Databricks **Personal Access Token**
- (Optional) Databricks CLI to run `sql/setup.sql`

---

## Quick Start

### 1) Clone & enter the project
```bash
git clone <your-fork-or-repo-url>.git
cd MCP_Dbricks_Demo

```

2) **Create virtual environment**
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

3) **Install dependencies**
```bash
pip install -r requirements.txt
```

4) **Configure environment**
Copy `.env.example` → `.env` and fill in your Databricks details:
```ini
DATABRICKS_HOST=adb-xxxxxxxx.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxxxxxxxxxxxxx
DATABRICKS_TOKEN=YOUR_PERSONAL_ACCESS_TOKEN
DB_DEFAULT_CATALOG=mcp_dbricks_demo
DB_DEFAULT_SCHEMA=core
```

5) **(Optional) Create demo tables**
```bash
databricks sql -f sql/setup.sql
```

---
6) **Run the MCP server (for manual testing)**
```bash
python server.py
```
---
**Using with Claude Desktop (MCP Client)**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "C:\\\\path\\\\to\\\\mcp_databricks_demo\\\\.venv\\\\Scripts\\\\python.exe",
      "args": ["C:\\\\path\\\\to\\\\mcp_databricks_demo\\\\server.py"],
      "workingDirectory": "C:\\\\path\\\\to\\\\mcp_databricks_demo"
    }
  }
}



```
Restart Claude Desktop → Settings → Developer should show the databricks MCP server as running.

## Example Prompts (in Claude)

- List all tables in the mcp_dbricks_demo.core schema.

- Run: SELECT * FROM mcp_dbricks_demo.core.products LIMIT 5.

- Insert a row into mcp_dbricks_demo.core.customers with customer_id='C-006', name='Alice', email='alice@example.com', country='US'.

- Update products set price = 1000 where name = 'Wireless Mouse'.

- Delete from shipments where status = 'pending'.

---
## What the Tools Do

- list_tables(catalog?, schema?): 
Uses SHOW TABLES IN <catalog>.<schema> and returns normalized JSON (database, table, isTemporary).

- sql_query(query): 
Runs read-only queries. If it’s a SELECT without LIMIT, appends LIMIT 25.

- insert_row(table, data, catalog?, schema?): 
Builds INSERT INTO <fqtn> (cols) VALUES (vals) from a dict.

- update_rows(table, set_data, where_sql, catalog?, schema?): 
Builds UPDATE <fqtn> SET col=val,... WHERE <where_sql> (WHERE required).

- delete_rows(table, where_sql, catalog?, schema?): 
Builds DELETE FROM <fqtn> WHERE <where_sql> (WHERE required).

Safety: This is a demo. Add validation, role-based controls, audit logging, and schema enforcement for production.
---

## Troubleshooting

- MCP server shows “Server disconnected” in Claude:
Ensure your .env values are correct and the SQL Warehouse is running.

- Activate.ps1 not recognized on Windows:
  ```bash
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
    ```
  Then re-activate:
    ```bash
  .\.venv\Scripts\Activate.ps1
    ```
- Git push errors (src refspec main/master does not match any):
Ensure you’ve committed to the branch you’re pushing:
    ```bash
    git status
    git add .
    git commit -m "init"
    git branch -M main
    git push -u origin main
    ```
---
## 👨‍💻 Authors

Demo prepared by **Praveen** and team for Ignite Talks 🚀

