import os
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.engine.url import URL
# Removed streamlit and dotenv imports since we're not using them

# Database connection parameters
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_tFUlfCsaCIcjgHeMb16"  # Hardcoded password
DB_HOST = "project-talha.f.aivencloud.com"
DB_PORT = 21991
DB_NAME = "defaultdb"

# Create connection URL with SSL mode
connection_url = URL.create(
    drivername='postgresql',
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={'sslmode': 'require'}
)

# Create SQLAlchemy engine
engine = sqlalchemy.create_engine(connection_url)

def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"Connected successfully! PostgreSQL version: {version[0]}")
            return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
