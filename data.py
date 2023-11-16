import datetime
import faker
import uuid

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃ Customize Tool Behavior
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ➤ `number_of_fields`: Determines the number of rows to insert.

# ➤ `excluded_tables`: A list of tables to exclude from data insertion.

# ➤ `tables_to_fill`: A list of tables to insert data into. If empty, all tables in the database will be filled.

# ➤ `graph`: Displays the graph after data insertion.

# ➤ `field`: Contains instructions for identifying and filling columns.
#     ➜ `Field Name`: The name of the field.
#     ➜ `Field Type`: The type of the field.
#     ➜ `Table Name`: The name of the table where the field is located.
#     ➜ `Identification Method`: Instructions for identifying the field.
#     ➜ `Value Generation`: Instructions for generating values for the field.

# Feel free to adjust these configurations based on your specific requirements.


fake = faker.Faker()
number_of_fields = 1
excluded_tables = ["system_setting"]
tables_to_fill = []
graph = True

fields = [
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
        "generator": lambda: fake.first_name(),
    },
    {
        "name": "last_name",
        "type": None,
        "table": None,
        "generator": lambda: fake.last_name(),
    },
    {"name": "name", "type": None, "table": None, "generator": lambda: fake.name()},
    {
        "name": "description",
        "type": None,
        "table": None,
        "generator": lambda: fake.sentence(),
    },
    {"name": "email", "type": None, "table": None, "generator": lambda: fake.email()},
    {
        "name": "password",
        "type": None,
        "table": None,
        "generator": lambda: fake.password(),
    },
    {
        "name": "mobile",
        "type": None,
        "table": None,
        "generator": lambda: fake.phone_number(),
    },
    {
        "name": "gender",
        "type": None,
        "table": None,
        "generator": lambda: fake.random_element(elements=["Male", "Female"]),
    },
    {
        "name": None,
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.word().capitalize(),
    },
    {"name": None, "type": "date", "table": None, "generator": lambda: fake.date()},
    {
        "name": None,
        "type": "datetime",
        "table": None,
        "generator": lambda: fake.date_time(),
    },
    {
        "name": None,
        "type": "boolean",
        "table": None,
        "generator": lambda: fake.boolean(),
    },
    {
        "name": None,
        "type": "tinyint",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=1),
    },
    {
        "name": None,
        "type": "bigint",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=9223372036854775807),
    },
    {
        "name": None,
        "type": "integer",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=100),
    },
]
