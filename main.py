from src.populate import DatabasePopulator
from decouple import config
from rich.traceback import install
import data


def configure_database():
    """
    Read database configuration from environment variables.

    Reads the following environment variables:
    - DB_HOST:     Database host name or IP address.
    - DB_USER:     Database username.
    - DB_PASSWORD: Database password.
    - DB_NAME:     Database name.

    Returns:
    Tuple (str, str, str, str): A tuple containing (host, user, password, database).
    """
    # Read database configuration
    db_host = config("DB_HOST")
    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_database = config("DB_NAME")

    return db_host, db_user, db_password, db_database


def main():
    install(max_frames=100)

    db_host, db_user, db_password, db_database = configure_database()

    DatabasePopulator(
        user=db_user,
        password=db_password,
        host=db_host,
        database=db_database,
        rows=data.number_of_fields,  # Number of rows to insert
        excluded_tables=data.excluded_tables,  # List of tables to exclude from insertion
        tables_to_fill=data.tables_to_fill,  # List of tables to insert data into
        graph=data.graph,  # Show table relation graph (True/False)
        special_fields=data.fields,  # Instructions for identifying and filling columns
    )


if __name__ == "__main__":
    main()
