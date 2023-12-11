import datetime
from decimal import Decimal
import json
import os
import faker
import uuid

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃ Customize Tool Behavior
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ➤ `number_of_fields`: Determines the number of rows to insert.

# ➤ `excluded_tables`: A list of tables to exclude from data insertion.

# ➤ `tables_to_fill`: A list of tables to insert data into. If empty, all tables in the database will be filled.

# ➤ `graph`: Displays the graph after data insertion.

# ➤ `special_foreign_fields`: Contains instructions for identifying and filling foreign referencing columns.
#     ➜ `Field Name`: The name of the field.
#     ➜ `Field Type`: The type of the field.
#     ➜ `Table Name`: The name of the table where the field is located.
#     ➜ `Value Generation`: Instructions for generating values for the field.

# ➤ `field`: Contains instructions for identifying and filling columns.
#     ** Keys are similar to `special_foreign_fields` **


# Feel free to adjust these configurations based on your specific requirements.


fake = faker.Faker()
number_of_fields = 40
excluded_tables = []
tables_to_fill = []
graph = False

special_foreign_fields = [
    {
        "name": "role_id",
        "type": "varchar",
        "table": None,
        "generator": lambda: "023d36f7-209c-4976-b328-767364758560",
    }
]

fields = [
    {
        "name": r"(\bid)|(_id)|(id_)",
        "type": "varchar",
        "table": None,
        "generator": lambda: str(uuid.uuid4()),
    },
    {
        "name": "first_name",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.first_name(),
    },
    {
        "name": "last_name",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.last_name(),
    },
    {
        "name": "name",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.name(),
    },
    {
        "name": "description",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.sentence(),
    },
    {
        "name": "email",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.email(),
    },
    {
        "name": "password",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.password(),
    },
    {
        "name": "mobile",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.phone_number(),
    },
    {
        "name": "gender",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.random_element(elements=["Male", "Female"]),
    },
    {
        "name": "address",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.address(),
    },
    {
        "name": "city",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.city(),
    },
    {
        "name": "state",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.state(),
    },
    {
        "name": "country",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.country(),
    },
    {
        "name": "zipcode",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.zipcode(),
    },
    {
        "name": "company",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.company(),
    },
    {
        "name": "job_title",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.job(),
    },
    {
        "name": "website",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.url(),
    },
    {
        "name": "ipv4",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.ipv4(),
    },
    {
        "name": "ipv6",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.ipv6(),
    },
    {
        "name": "user_agent",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.user_agent(),
    },
    {
        "name": "credit_card_number",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.credit_card_number(),
    },
    {
        "name": "credit_card_expire",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.credit_card_expire(),
    },
    {
        "name": "credit_card_security_code",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.credit_card_security_code(),
    },
    {
        "name": "iban",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.iban(),
    },
    {
        "name": "bic",
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.bic(),
    },
    {
        "name": None,
        "type": "varchar",
        "table": None,
        "generator": lambda: fake.word().capitalize(),
    },
    {
        "name": None,
        "type": "float",
        "table": None,
        "generator": lambda: fake.random_element(elements=(1.0, 10.0)),
    },
    {
        "name": None,
        "type": "date",
        "table": None,
        "generator": lambda: fake.date(),
    },
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
    {
        "name": None,
        "type": "smallint",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=32767),
    },
    {
        "name": None,
        "type": "text",
        "table": None,
        "generator": lambda: fake.text(),
    },
    {
        "name": None,
        "type": "uuid",
        "table": None,
        "generator": lambda: str(uuid.uuid4()),
    },
    {
        "name": None,
        "type": "json",
        "table": None,
        "generator": lambda: json.dumps(fake.profile()),
    },
    {
        "name": None,
        "type": "decimal",
        "table": None,
        "generator": lambda: Decimal(fake.random_number(digits=5)) / 100,
    },
    {
        "name": None,
        "type": "numeric",
        "table": None,
        "generator": lambda: fake.random_number(digits=5),
    },
    {
        "name": None,
        "type": "timestamp",
        "table": None,
        "generator": lambda: fake.unix_time(),
    },
    {
        "name": None,
        "type": "time",
        "table": None,
        "generator": lambda: fake.time(),
    },
    {
        "name": None,
        "type": "year",
        "table": None,
        "generator": lambda: fake.year(),
    },
    {
        "name": None,
        "type": "binary",
        "table": None,
        "generator": lambda: os.urandom(10),
    },
    {
        "name": None,
        "type": "enum",
        "table": None,
        "generator": lambda: fake.random_element(
            elements=("option1", "option2", "option3")
        ),
    },
    {
        "name": None,
        "type": "set",
        "table": None,
        "generator": lambda: {fake.word(), fake.word(), fake.word()},
    },
    {
        "name": None,
        "type": "blob",
        "table": None,
        "generator": lambda: bytes(fake.sentence(), "utf-8"),
    },
    {
        "name": None,
        "type": "geometry",
        "table": None,
        "generator": lambda: f"POINT({fake.longitude()} {fake.latitude()})",
    },
    {
        "name": None,
        "type": "point",
        "table": None,
        "generator": lambda: (fake.longitude(), fake.latitude()),
    },
    {
        "name": None,
        "type": "varbinary",
        "table": None,
        "generator": lambda: os.urandom(20),
    },
    {
        "name": None,
        "type": "mediumint",
        "table": None,
        "generator": lambda: fake.random_int(min=0, max=16777215),
    },
    {
        "name": None,
        "type": "longblob",
        "table": None,
        "generator": lambda: bytes(fake.text(), "utf-8"),
    },
    {
        "name": None,
        "type": "longtext",
        "table": None,
        "generator": lambda: fake.text(max_nb_chars=10000),
    },
    {
        "name": None,
        "type": "mediumblob",
        "table": None,
        "generator": lambda: bytes(fake.text(), "utf-8"),
    },
    {
        "name": None,
        "type": "mediumtext",
        "table": None,
        "generator": lambda: fake.text(max_nb_chars=5000),
    },
    {
        "name": None,
        "type": "tinyblob",
        "table": None,
        "generator": lambda: bytes(fake.text(max_nb_chars=255), "utf-8"),
    },
    {
        "name": None,
        "type": "tinytext",
        "table": None,
        "generator": lambda: fake.text(max_nb_chars=255),
    },
]
