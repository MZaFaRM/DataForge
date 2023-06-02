from populate import populator
from decouple import config


def main():
    db_host = config("DB_HOST")
    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_database = config("DB_NAME")

    # TODO: Modify the below values based on the requirements
    number_of_fields = 50
    excluded_tables = ["system_setting"]
    graph = True
    special_fields = [
        {
            "name": None, # * Name of the field, can be Null if it can be ignored
            "type": "tinyint", # * type of the field, can be Null if it can be ignored
            "table": None, # * The Table in which the field is, can be Null to apply same to all Table
            "value": [0, 1], # * Choices of values, a value will be randomly chosen from this list
        },
        {
            "name": "karma",
            "type": None,
            "table": None,
            "value": list(range(9999999)),
        },
        {
            "name": "org_type",
            "type": None,
            "table": "organization",
            "value": ["College", "Company", "Community"],
        },
    ]

    populator(
        user=db_user,  # * Database host name
        password=db_password,  # * Database username
        host=db_host,  # * Database password
        database=db_database,  # * Database name
        rows=number_of_fields,  # * Number of rows to insert
        excluded_tables=excluded_tables,  # * Tables to exclude from insertion must be a list
        graph=graph,  # * Whether to show table relation graph at the end must be a python bool
        special_fields=special_fields, # * If any special fields
    )


if __name__ == "__main__":
    main()
