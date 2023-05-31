from populate import populator
from decouple import config


def main():
    
    db_host = config("DB_HOST")
    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_database = config("DB_NAME")
    
    # TODO: Modify the below values based on the requirements
    number_of_fields = 1
    excluded_tables = ["system_setting"]
    graph = True

    populator(
        user=db_user, # * Database host name
        password=db_password, # * Database username
        host=db_host, # * Database password
        database=db_database, # * Database name
        rows=number_of_fields, # * Number of rows to insert
        excluded_tables=excluded_tables, # * Tables to exclude from insertion must be a list
        graph=graph, # * Whether to show table relation graph at the end must be a python bool
    )


if __name__ == "__main__":
    main()
