import pyodbc
from typing import Dict, Any
from app.core.config import settings
from app.monitoring.logging import get_logger

logger = get_logger(__name__)


class AzureSQLClient:
    def __init__(self):
        self.server = settings.AZURE_DB_HOST
        self.database = settings.AZURE_DATABASE
        self.username = settings.AZURE_DB_USER
        self.password = settings.AZURE_DB_PASSWORD
        self.connection_string = None
        self._setup_connection_string()

    def _setup_connection_string(self):
        """Setup connection string for Azure SQL with SQL authentication"""
        self.connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )

    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        conn = None
        try:
            # Remove comments and validate
            lines = query.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('--')]
            query_clean = '\n'.join(clean_lines).strip()

            if not query_clean:
                logger.warning(f"Invalid query (comment or empty): {query}")
                return {
                    "success": False,
                    "error": "No valid SQL query generated. Please provide a specific business question.",
                    "data": []
                }

            logger.info(f"Executing query: {query_clean}")

            # Split by semicolon for multiple statements
            statements = [s.strip() for s in query_clean.split(';') if s.strip()]

            all_results = []
            all_columns = []

            # Execute each statement separately with its own connection to avoid memory corruption
            for stmt in statements:
                conn = pyodbc.connect(self.connection_string, autocommit=True)
                cursor = conn.cursor()

                cursor.execute(stmt)

                # Get column names
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    if not all_columns:
                        all_columns = columns

                    # Fetch rows and convert to dicts
                    rows = cursor.fetchall()
                    for row in rows:
                        all_results.append(dict(zip(columns, row)))

                cursor.close()
                conn.close()
                conn = None

            return {
                "success": True,
                "data": all_results,
                "row_count": len(all_results),
                "columns": all_columns,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Query execution failed: {error_msg}")
            return {"success": False, "error": error_msg, "data": []}
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def execute_query_safe(self, query: str, max_rows: int = 1000) -> Dict[str, Any]:
        """Execute query with safety limits"""
        try:
            # Add LIMIT if not present and query is a SELECT
            if (
                query.strip().upper().startswith("SELECT")
                and "LIMIT" not in query.upper()
            ):
                if "TOP" not in query.upper():
                    # Add TOP clause for SQL Server
                    query = query.replace("SELECT", f"SELECT TOP {max_rows}", 1)

            return self.execute_query(query)

        except Exception as e:
            logger.error(f"Safe query execution failed: {str(e)}")
            return {"success": False, "error": str(e), "data": []}
