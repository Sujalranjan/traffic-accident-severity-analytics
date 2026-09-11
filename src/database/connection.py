import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Database configuration is loaded from environment variables:
        POSTGRES_HOST
        POSTGRES_PORT
        POSTGRES_DB
        POSTGRES_USER
        POSTGRES_PASSWORD
    """

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "traffic_analytics")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")

    connection = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password
    )

    return connection


if __name__ == "__main__":
    try:
        connection = get_connection()

        print("PostgreSQL connection successful!")

        connection.close()

    except Exception as error:
        print("PostgreSQL connection failed.")
        print(f"Error: {error}")