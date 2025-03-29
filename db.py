import sqlalchemy
from sqlalchemy import text
from sqlalchemy.engine.url import URL

# Hardcoded database credentials
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_tFUlfCsaCIcjgHeMb16"  # Hardcoded password
DB_HOST = "project-talha.f.aivencloud.com"
DB_PORT = 21991
DB_NAME = "defaultdb"


def create_engine():
    """
    Create and return a SQLAlchemy engine using SSL with hardcoded credentials.
    Returns:
        sqlalchemy.Engine: The SQLAlchemy engine for database interaction.
    """
    connection_url = URL.create(
        drivername='postgresql',
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
    engine = sqlalchemy.create_engine(connection_url)
    return engine


def main():
    engine = create_engine()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"Connected successfully! PostgreSQL version: {version}")


if __name__ == "__main__":
    main()
