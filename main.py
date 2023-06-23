from populate import populator
from decouple import config
from faker import Faker


def main():
    
    faker = Faker()
    
    # TODO: Create a `.env` file, refer the `.env.sample` to complete it 
    db_host = config("DB_HOST")
    db_user = config("DB_USER")
    db_password = config("DB_PASSWORD")
    db_database = config("DB_NAME")

    # TODO: Modify the below values based on the requirements

    # * The `number_of_fields` variable determines the number of rows to insert
    # * The `excluded_tables` list should have the tables to not insert data into
    # * The `tables_to_fill` list should have the tables to insert data into
        # ? If empty, all tables in the database are filled
    # * Shows the database relation graph after the insertion
    # * Contains the fields that needs special values
        # ? Name of the field, it can be Null if it can be ignored
        # ? type of the field, it can be Null if it can be ignored
        # ? The Table in which the field is, can be Null to apply same to all Table
        # ? Choices of values, a value will be randomly chosen from this list
    
    # ! Note:
    # ! The `tables_to_fill` list is preferred over the `excluded_tables`
    # ! list hence, if both exists `excluded_tables` will be ignored
    
    number_of_fields = 50
    excluded_tables = ["user_settings"]
    tables_to_fill = ["user"]
    graph = True
    special_fields = [
        {
            "name": None, 
            "type": "tinyint", 
            "table": None, 
            "value": [0, 1], 
        },
        {
            "name": "karma",
            "type": None,
            "table": None,
            "value": list(range(9999999)),
        },
        {
            "name": "pi_id",
            "type": None,
            "table": None,
            "value": [f"{faker.name().replace(' ', '').lower()}@birm" for _ in range(1000)],
        },
    ]

    populator(
        user=db_user,  # * Database host name
        password=db_password,  # * Database username
        host=db_host,  # * Database password
        database=db_database,  # * Database name
        rows=number_of_fields,  # * Number of rows to insert
        excluded_tables=excluded_tables,  # * Tables to exclude from insertion must be a list
        tables_to_fill=tables_to_fill,  # * Tables to exclude from insertion must be a list
        graph=graph,  # * Whether to show table relation graph at the end must be a python bool
        special_fields=special_fields, # * If any special fields
    )


if __name__ == "__main__":
    main()
