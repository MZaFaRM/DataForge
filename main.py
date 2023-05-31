from populate import populator
import os


def main():

    db_host = None # Insert the database host
    db_user = None # Insert the database username
    db_password = None # Insert the database password
    db_database = None # Insert the database name
    number_of_rows = None # Insert the number of rows

    populator(db_host, db_user, db_password, db_database, number_of_rows)


if __name__ == "__main__":
    main()
