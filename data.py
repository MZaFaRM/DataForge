import faker
import uuid

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
    
fake = faker.Faker()

number_of_fields = 10
excluded_tables = ["system_setting"]
tables_to_fill = []
graph = True
    
special_fields = [

    {
        "name": r"(\bid)|(_id)|(id_)", 
        "type": None, 
        "table": None, 
        "generator": lambda: str(uuid.uuid4()), 
    },
    {
        "name": "first_name",
        "type": None,
        "table": None,
        "generator": lambda: fake.first_name()
    },
    {
        "name": "last_name",
        "type": None,
        "table": None,
        "generator": lambda: fake.last_name()
    },
    {
        "name": "description",
        "type": None,
        "table": None,
        "generator": lambda: fake.sentence()
    },
    {
        "name": "email",
        "type": None,
        "table": None,
        "generator": lambda: fake.email()
    },
    {
        "name": "password",
        "type": None,
        "table": None,
        "generator": lambda: fake.password()
    },
    {
        "name": "mobile",
        "type": None,
        "table": None,
        "generator": lambda: fake.phone_number()
    },
    {
        "name": "gender",
        "type": None,
        "table": None,
        "generator": lambda: fake.random_element(elements=["Male", "Female"])
    },
    {
        "name": None,
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.word().capitalize()
    },
    {
        "name": None,
        "type": "date",
        "table": None,
        "generator": lambda: fake.date()
    },
    {
        "name": None,
        "type": "datetime",
        "table": None,
        "generator": lambda: fake.date_time()
    },
    {
        "name": None,
        "type": "boolean",
        "table": None,
        "generator": lambda: fake.boolean()
    },
    {
        "name": None,
        "type": "tinyint",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=1)
    },
    {
        "name": None,
        "type": "bigint",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=9223372036854775807)
    },
    {
        "name": None,
        "type": "integer",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=100)
    },
]