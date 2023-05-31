from populate import populator

host = "localhost"
user = "root"
password = "!W?+<KGy=3GJ"
database = "populator"
number_of_rows = 10

def main():
    populator(user, password, host, database, 10)

if __name__ == "__main__":
    main()