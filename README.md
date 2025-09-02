# Databricks MCP Demo

This project demonstrates how to integrate **Model Context Protocol (MCP)** with **Databricks SQL Warehouse** and **Unity Catalog**.  
It lets AI agents (e.g., Claude Desktop) list tables, run queries, and perform simple inserts/updates/deletes via natural-language tools.

---

## 🚀 Features

- **List Tables** — Show all tables in a catalog/schema  
- **Run Queries** — Read-only `SELECT`, `SHOW`, `DESCRIBE`  
- **Insert Rows** — Add new records into a table  
- **Update Rows** — Update records with conditions  
- **Delete Rows** — Delete records with conditions

---

## 📂 Project Structure

```
mcp-databricks/
├─ server.py            # MCP server with tools (list, query, insert, update, delete)
├─ requirements.txt     # Python dependencies
├─ .env.example         # Example environment variables (copy to .env and fill)
├─ README.md            # This document
└─ sql/
   └─ setup.sql         # Example SQL script to create sample tables & data
```

---

## ✅ Prerequisites

- Python **3.10+**
- A Databricks **SQL Warehouse** and **Personal Access Token**
- (Optional) Databricks CLI for running `sql/setup.sql`

---

## ⚙️ Setup Instructions

1) **Clone the repo**
```bash
git clone https://github.com/ignitedata-ai/IgniteTalks-repo.git
cd IgniteTalks-repo/mcp_databricks_Aug_21_2025
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
DATABRICKS_HOST=adb-xxxx.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxx
DATABRICKS_TOKEN=YOUR_PERSONAL_ACCESS_TOKEN
DB_DEFAULT_CATALOG=mcp_dbricks_demo
DB_DEFAULT_SCHEMA=core
```

5) **Run the MCP server**
```bash
python server.py
```

---

## 🗄️ Initialize Demo Tables (optional)

Use the provided SQL to create sample tables and rows.

**Option A: Databricks CLI**
```bash
# Requires CLI configured and a default target set for the SQL Warehouse
databricks sql -f sql/setup.sql
```

**Option B: Databricks SQL UI**
- Open **SQL Editor** → select your **Warehouse**  
- Paste the contents of `sql/setup.sql` → **Run**

This creates:
- `customers`
- `products`
- `shipments`
- `orders`

---

## 💬 Example Prompts (Claude Desktop)

- “List all tables in the `mcp_dbricks_demo.core` schema.”  
- “Show the first 5 rows from `products`.”  
- “Update the price to 1000 where name = 'Wireless Mouse'.”  
- “Delete rows from `shipments` where status = 'pending'.”  

---

## 🔒 Notes

- Do **not** commit `.env` (already ignored).  
- This is a **POC**—add validation, audit, and access controls for production.

---

## 👨‍💻 Authors

Demo prepared by **Praveen** for Ignite Talks 🚀
