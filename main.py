from populate import populator
from decouple import config
import data
from rich.traceback import install


def configure_database():
    """
    Read database configuration from environment variables.
    """
    db_host = config("DB_HOST")
    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_database = config("DB_NAME")
    return db_host, db_user, db_password, db_database


def main():
    # Rich traceback for more visually appealing exception handling.
    install(max_frames=2)

    db_host, db_user, db_password, db_database = configure_database()

    populator(
        user=db_user,
        password=db_password,
        host=db_host,
        database=db_database,
        rows=data.number_of_fields,
        excluded_tables=data.excluded_tables,
        tables_to_fill=data.tables_to_fill,
        graph=data.graph,
        special_fields=data.fields,
    )


if __name__ == "__main__":
    main()
