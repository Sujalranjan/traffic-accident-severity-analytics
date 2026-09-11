from pathlib import Path

from connection import get_connection


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

SQL_ROOT = PROJECT_ROOT / "sql"


def execute_sql_file(cursor, file_path):
    """
    Read and execute a SQL file.
    """
    print(f"Executing: {file_path.relative_to(PROJECT_ROOT)}")

    sql = file_path.read_text(encoding="utf-8")

    if sql.strip():
        cursor.execute(sql)


def initialize_database():
    """
    Create the PostgreSQL database schemas and tables
    using the project's SQL files.
    """

    connection = None

    try:
        connection = get_connection()

        # Create a cursor
        cursor = connection.cursor()

        print("Connected to PostgreSQL.")
        print()

        # --------------------------------------------------
        # 1. Create schemas
        # --------------------------------------------------

        schema_file = SQL_ROOT / "schemas" / "01_create_schemas.sql"

        execute_sql_file(cursor, schema_file)

        # --------------------------------------------------
        # 2. Create relational tables
        # --------------------------------------------------

        table_files = [
            SQL_ROOT / "tables" / "01_create_collisions.sql",
            SQL_ROOT / "tables" / "02_create_vehicles.sql",
            SQL_ROOT / "tables" / "03_create_casualties.sql",
            SQL_ROOT / "tables" / "04_create_indexes.sql",
        ]

        for table_file in table_files:
            execute_sql_file(cursor, table_file)

        # Commit all database changes
        connection.commit()

        print()
        print("Database initialization completed successfully.")

        cursor.close()
        connection.close()

    except Exception as error:

        if connection:
            connection.rollback()
            connection.close()

        print()
        print("Database initialization failed.")
        print(f"Error: {error}")

        raise


if __name__ == "__main__":
    initialize_database()