import os
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv  # loads credentials from a local .env.
from fastmcp import FastMCP   # tiny framework that turns Python functions into MCP tools.
from databricks import sql as dbsql

# Load .env from this file's folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

APP = FastMCP("databricks-mcp")

# --- Env ---
HOST = os.environ["DATABRICKS_HOST"]
HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"] # SQL Warehouse > Connection details
TOKEN = os.environ["DATABRICKS_TOKEN"]

DEF_CAT = os.getenv("DB_DEFAULT_CATALOG")      # e.g. mcp_dbricks_demo
DEF_SCHEMA = os.getenv("DB_DEFAULT_SCHEMA", "core")

# --- DB helpers ---

def get_conn():
    return dbsql.connect(
        server_hostname=HOST,
        http_path=HTTP_PATH,
        access_token=TOKEN,
    )

def qualify(table: str, catalog: Optional[str], schema: Optional[str]) -> str:
    """
    Returns a fully-qualified table name: <catalog>.<schema>.<table>
    If the input already has dots, leave it as-is.
    """
    if "." in table:
        return table
    cat = catalog or DEF_CAT
    sch = schema or DEF_SCHEMA
    if not cat:
        raise ValueError("Catalog is required (set DB_DEFAULT_CATALOG or pass catalog).")
    return f"{cat}.{sch}.{table}"

def _escape(v: Any) -> str:
    """Very small utility to render SQL literals safely for demo purposes."""
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    return str(v)

def _execute(query: str, commit: bool = False) -> Dict[str, Any]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        if commit:
            conn.commit()
        # Rowcount can be -1 for some drivers; include anyway.
        return {"columns": cols, "rows": [list(r) for r in rows], "rowcount": getattr(cur, "rowcount", None)}

# --- Tools ---

@APP.tool()
def list_tables(
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List tables in a given catalog.schema (falls back to DB_DEFAULT_*).
    """
    cat = catalog or DEF_CAT
    sch = schema or DEF_SCHEMA
    if not cat:
        raise ValueError("Catalog is required (set DB_DEFAULT_CATALOG or pass catalog).")

    q = f"SHOW TABLES IN {cat}.{sch}"
    out = _execute(q)
    # Normalize the SHOW TABLES output
    result = []
    for r in out["rows"]:
        # Databricks returns columns like: database, tableName, isTemporary
        # Pull by position for robustness.
        result.append({"database": r[0], "table": r[1], "isTemporary": r[2]})
    return {"result": result}

@APP.tool()
def sql_query(query: str) -> Dict[str, Any]:
    """
    Run a *read-only* query (SELECT/SHOW/DESCRIBE). If no LIMIT is present for SELECT,
    a LIMIT 25 is appended for safety.
    """
    if not query or not query.strip():
        raise ValueError("Provide a SQL query.")
    q = query.strip().rstrip(";")
    ql = q.lower()

    if not (ql.startswith("select") or ql.startswith("show") or ql.startswith("describe")):
        raise ValueError("Only SELECT / SHOW / DESCRIBE are allowed in sql_query.")

    if ql.startswith("select") and " limit " not in f" {ql} ":
        q += " LIMIT 25"

    return _execute(q)

@APP.tool()
def insert_row(
    table: str,
    data: Dict[str, Any],
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a single row. `data` is a dict of column: value.
    """
    if not table:
        raise ValueError("Provide a table name.")
    if not data:
        raise ValueError("Provide data as a non-empty dict.")

    fqtn = qualify(table, catalog, schema)
    cols = ", ".join(data.keys())
    vals = ", ".join(_escape(v) for v in data.values())
    q = f"INSERT INTO {fqtn} ({cols}) VALUES ({vals})"
    out = _execute(q, commit=True)
    return {"success": True, "affected_rows": out["rowcount"]}

@APP.tool()
def update_rows(
    table: str,
    set_data: Dict[str, Any],
    where_sql: str,
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update rows. Example:
      table="products",
      set_data={"price": 1000},
      where_sql="lower(name) = 'apple'"
    """
    if not table:
        raise ValueError("Provide a table name.")
    if not set_data:
        raise ValueError("Provide set_data as a non-empty dict.")
    if not where_sql:
        raise ValueError("Provide a WHERE clause to avoid updating all rows.")

    fqtn = qualify(table, catalog, schema)
    sets = ", ".join(f"{k} = {_escape(v)}" for k, v in set_data.items())
    q = f"UPDATE {fqtn} SET {sets} WHERE {where_sql}"
    out = _execute(q, commit=True)
    return {"success": True, "affected_rows": out["rowcount"]}

@APP.tool()
def delete_rows(
    table: str,
    where_sql: str,
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Delete rows. Example:
      table="shipments",
      where_sql="status = 'pending'"
    """
    if not table:
        raise ValueError("Provide a table name.")
    if not where_sql:
        raise ValueError("Provide a WHERE clause to avoid deleting all rows.")

    fqtn = qualify(table, catalog, schema)
    q = f"DELETE FROM {fqtn} WHERE {where_sql}"
    out = _execute(q, commit=True)
    return {"success": True, "affected_rows": out["rowcount"]}

if __name__ == "__main__":
    # STDIO transport (Claude Desktop / MCP Inspector)
    APP.run()
