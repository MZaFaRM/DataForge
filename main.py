from populate import populator
from decouple import config
from faker import Faker
import data

def main():
    
    db_host = config("DB_HOST")
    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_database = config("DB_NAME")
    
    populator(
        user=db_user,  # * Database host name
        password=db_password,  # * Database username
        host=db_host,  # * Database password
        database=db_database,  # * Database name
        rows=data.number_of_fields,  # * Number of rows to insert
        excluded_tables=data.excluded_tables,  # * Tables to exclude from insertion must be a list
        tables_to_fill=data.tables_to_fill,  # * Tables to exclude from insertion must be a list
        graph=data.graph,  # * Whether to show table relation graph at the end must be a python bool
        special_fields=data.special_fields, # * If any special fields
    )


if __name__ == "__main__":
    main()
