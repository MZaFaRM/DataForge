import contextlib
from decimal import DivisionByZero
from inspect import Parameter
import random
from types import NoneType
from faker import Faker
import re
import sqlalchemy
from sqlalchemy import create_engine, inspect
import networkx as nx
import matplotlib.pyplot as plt
from collections import OrderedDict
from sqlalchemy.exc import IntegrityError
from rich.progress import Progress
from rich import print


class populator:
    # The populator class is a Python class that populates a MySQL database with fake data based on the
    # table relations and column data types.
    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        database: str,
        rows: int,
        excluded_tables: list = None,
        tables_to_fill: list = None,
        graph: bool = True,
        special_fields: list[dict] = None,
    ) -> None:
        try:
            db_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
            self.rows = rows
            self.special_fields = special_fields
            self.fake = Faker("en_IN")

            self.engine = create_engine(db_url, echo=False)

            inspector = inspect(self.engine)
            
            if tables_to_fill:
                self.make_relations(inspector=inspector, tables_to_fill=tables_to_fill)
            else: 
                self.make_relations(inspector=inspector, excluded_tables=excluded_tables)

            self.arrange_graph()
            self.fill_table(inspector=inspector)
            print("[#00FF00] Operation successful!")
            if graph:
                self.draw_graph()
        except Exception as e:
            raise(e)
            print(f"[#ff0000]Oops, something went wrong!: {e}")

    def make_relations(self, inspector, excluded_tables :list = None, tables_to_fill :list = None):
        """
        The function identifies table relations and tracks foreign key relations while excluding specified
        tables.

        :param inspector: an object that can inspect a database schema and retrieve information about its
        tables and relationships
        :param excluded_tables: A list of table names that should be excluded from the inheritance relations
        analysis
        :return: the dictionary of inheritance relations between tables, with excluded tables removed.
        """
        with Progress() as progress:
            color = self.rnd_color()
            task = progress.add_task(
                f"[{color}] Identifying table relations...", total=100, pulse=True
            )

            table_names = tables_to_fill or inspector.get_table_names()
            
            progress.update(
                task, description=f"[{color}] Getting table names", advance=10
            )

            self.inheritance_relations = {}

            step = 80 / len(table_names)

            for table_name in table_names:
                foreign_keys = inspector.get_foreign_keys(table_name)

                referred_tables = {
                    foreign_key["referred_table"] for foreign_key in foreign_keys
                }

                self.inheritance_relations[table_name] = list(referred_tables)

                progress.update(
                    task,
                    description=f"[{color}] Tracking foreign relations...",
                    advance=step,
                )

            progress.update(
                task, description=f"[{color}] Removing excluded tables...", advance=10
            )
            
            if excluded_tables:
                for table in excluded_tables:
                    with contextlib.suppress(ValueError):
                        self.inheritance_relations.pop(table)

            progress.update(
                task, description="[#00FF00] Foreign key relations identified..."
            )
            return self.inheritance_relations

    def draw_graph(self):
        """
        This function draws a graph to visualize the inheritance relationships between tables in a database.
        """
        graph = nx.DiGraph()

        for table, inherited_tables in self.inheritance_relations.items():
            if inherited_tables:
                for inherited_table in inherited_tables:
                    graph.add_edge(inherited_table, table)
            else:
                graph.add_node(table)

        plt.figure(figsize=(12, 8))
        pos = nx.shell_layout(graph)
        nx.draw_networkx(
            graph, pos, with_labels=True, edge_color="gray", node_size=0, font_size=10
        )

        plt.title("Database Inheritance Relationships")
        plt.axis("off")
        plt.show()

    def arrange_graph(self):
        """
        The function arranges identified inheritance relations in a directed graph and orders them
        topologically.
        """
        with Progress() as progress:
            color = self.rnd_color()
            task = progress.add_task(
                f"[{color}] Ordering identified relations...", total=100, pulse=True
            )
            graph = nx.DiGraph()

            step = 60 / len(self.inheritance_relations)
            for table, inherited_tables in self.inheritance_relations.items():
                if inherited_tables:
                    for inherited_table in inherited_tables:
                        graph.add_edge(inherited_table, table)
                else:
                    graph.add_node(table)
                progress.update(
                    task,
                    description=f"[{color}] Establishing connections...",
                    advance=step,
                )

            ordered_tables = list(nx.topological_sort(graph))

            ordered_inheritance_relations = OrderedDict()

            for table in ordered_tables:
                if table in self.inheritance_relations:
                    ordered_inheritance_relations[table] = self.inheritance_relations[table]
                progress.update(
                    task, description=f"[{color}] Saving relations...", advance=step
                )

            self.inheritance_relations = ordered_inheritance_relations
            progress.update(
                task, description="[#00FF00] Ordered identified relations..."
            )
    
    def populate_special_fields(self, table_name):
        for field in self.special_fields:
            if (
                self.compare_column_with(field["name"], "name")
                or self.compare_column_with(field["type"], "type")
                and (
                    True
                    if (field.get("table") and field["table"] == table_name)
                    else not field.get("table")
                )
            ):
                value = self.fake.random_element(elements=field["value"])
                if value is not None:
                    return value

        return None


    def get_value_from_column_name(self):
        """
        This function returns fake data based on the column name.
        :return: either a generated fake data value based on the column name or False if none of the
        conditions are met.
        """

        if re.search(
            re.compile(r"(\bid)|(_id)|(id_)", re.IGNORECASE), self.column["name"]
        ):
            return self.fake.uuid4()
        elif self.compare_column_with("first_name", "name"):
            return self.generate_fake_data("first_name()")
        elif self.compare_column_with("last_name", "name"):
            return self.generate_fake_data("last_name()")
        elif self.compare_column_with("description", "name"):
            return self.generate_fake_data("sentence()")
        elif self.compare_column_with("email", "name"):
            return self.generate_fake_data("email()")
        elif self.compare_column_with("password", "name"):
            return self.generate_fake_data("password()")
        elif self.compare_column_with("mobile", "name"):
            return self.generate_fake_data("phone_number()")
        elif self.compare_column_with("gender", "name"):
            return self.fake.random_element(elements=["Male", "Female"])

        return None

    def generate_fake_data(self, type):
        """
        This function generates fake data based on the specified type using the Python Faker library.

        :param type: The "type" parameter is a string that specifies the type of fake data to be generated.
        It is used to dynamically call a method from the "fake" object (which is an instance of the Faker
        library) to generate the desired type of fake data. The method is called using the "eval
        :return: The function `generate_fake_data` returns either a subset of fake data of the specified
        type (if the length of the subset is less than or equal to the length of the column of that type),
        or all the fake data of the specified type (if the length of the subset is greater than the length
        of the column of that type). The fake data is generated using the `fake` attribute of self
        """
        try:
            return eval(f"self.fake.{type}")[: self.column["type"].length]
        except AttributeError:
            return eval(f"self.fake.{type}")

    def compare_column_with(self, data, type):
        try:
            return data in str(self.column[type]).lower()
        except TypeError:
            return False

    def get_value_from_data_type(self):
        if self.compare_column_with("varchar", "type"):
            return self.generate_fake_data("word()").capitalize()

        elif self.compare_column_with("date", "type"):
            return self.generate_fake_data("date()")
        elif self.compare_column_with("datetime", "type"):
            return self.generate_fake_data("date_time()")

        elif self.compare_column_with("boolean", "type"):
            return self.fake.boolean()
        elif self.compare_column_with("tinyint", "type"):
            return self.fake.random_int(min=-128, max=127)
        elif self.compare_column_with("bigint", "type"):
            return self.fake.random_int(
                min=-9223372036854775808, max=9223372036854775807
            )

        elif self.compare_column_with("integer", "type"):
            return self.fake.random_int(min=0, max=100)

        return None

    def get_value(self, column, foreign_keys, table_name):
        self.column = column

        methods = [
            (self.populate_special_fields, (table_name,)),
            (self.process_foreign, (foreign_keys,)),
            (self.get_value_from_column_name, ()),
            (self.get_value_from_data_type, ())
        ]

        value = None
        for method, args in methods:
            value = method(*args)
            if value is not None:
                break

        return value

    def process_foreign(self, foreign_keys):
        if self.column["name"] in foreign_keys:
            desc = foreign_keys[self.column["name"]]
            metadata = sqlalchemy.MetaData()
            metadata.reflect(bind=self.engine, only=[desc[1]])
            related_table = metadata.tables[desc[1]]

            s = sqlalchemy.select(related_table.c[desc[0]])
            conn = self.engine.connect()
            result = conn.execute(s).fetchall()
            conn.close()

            items = [row[0] for row in result]
            referred_items = result
            items = [item[0] for item in referred_items]

            return self.fake.random_element(elements=items)

        return None

    def process_row_data(self, inspector, table_name):
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)

        foreign_keys = {
            foreign_key["constrained_columns"][0]: (
                foreign_key["referred_columns"][0],
                foreign_key["referred_table"],
            )
            for foreign_key in foreign_keys
        }

        return {
            column["name"]: self.get_value(column, foreign_keys, table_name)
            for column in columns
        }

    def fill_table(self, inspector):
        for table_name in self.inheritance_relations:
            color = self.rnd_color()
            with Progress() as progress:
                task = progress.add_task(
                    f"[{color}] Inserting rows into {table_name}...",
                    total=100,
                    pulse=True,
                )
                for _ in range(self.rows):
                    status = self.database_insertion(table_name, inspector)
                    while not status:
                        progress.update(
                            task,
                            description="[#FF0000] An Integrity Error occurred trying again...",
                        )
                        status = self.database_insertion(table_name, inspector)

                    progress.update(
                        task,
                        description=f"[{color}] Inserting rows into {table_name}...",
                        advance=100 / self.rows,
                    )

    def database_insertion(self, table_name, inspector):
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine, only=[table_name])
        table = metadata.tables[table_name]
        row_data = self.process_row_data(inspector, table_name)

        with self.engine.begin() as connection:
            try:
                connection.execute(table.insert().values(**row_data))
                return True
            except IntegrityError as e:
                return False
            except Exception as e:
                raise

    def rnd_color(self):
        # rgb = [random.randint(100, 255) for _ in range(3)]
        # return '#{:02x}{:02x}{:02x}'.format(*rgb)
        return random.choice(["#00ff00", "#91C788"])



    # def make_relations(self, inspector, excluded_tables):
    #     """
    #     The function identifies table relations and tracks foreign key relations while excluding specified
    #     tables.

    #     :param inspector: an object that can inspect a database schema and retrieve information about its
    #     tables and relationships
    #     :param excluded_tables: A list of table names that should be excluded from the inheritance relations
    #     analysis
    #     :return: the dictionary of inheritance relations between tables, with excluded tables removed.
    #     """
    #     with Progress() as progress:
    #         color = self.rnd_color()
    #         task = progress.add_task(
    #             f"[{color}] Identifying table relations...", total=100, pulse=True
    #         )


    #         table_names = inspector.get_table_names()

    #         progress.update(
    #             task, description=f"[{color}] Removing excluded tables...", advance=10
    #         )

    #         for table in excluded_tables:
    #             table_names.remove(table)


    #         self.inheritance_relations = {}

    #         progress.update(
    #             task, description=f"[{color}] Removing related tables", advance=10
    #         )

    #         print(table_names)
            
    #         excluded_tables = self.filter_tables(table_names, excluded_tables, inspector)
    #         for table in excluded_tables:
    #             with contextlib.suppress(ValueError):
    #                 table_names.remove(table)
                    
    #         print(table_names)

    #         step = 80 / len(table_names)

    #         for table_name in table_names:
    #             foreign_keys = inspector.get_foreign_keys(table_name)

    #             referred_tables = {
    #                 foreign_key["referred_table"] for foreign_key in foreign_keys
    #             }

    #             self.inheritance_relations[table_name] = list(referred_tables)

    #             progress.update(
    #                 task,
    #                 description=f"[{color}] Tracking foreign relations...",
    #                 advance=step,
    #             )

    #         progress.update(
    #             task, description="[#00FF00] Foreign key relations identified..."
    #         )
    #         return self.inheritance_relations
        
    # def filter_tables(self, table_names, excluded_tables, inspector):
    #     for table_name in table_names:
    #         foreign_keys = inspector.get_foreign_keys(table_name)
    #         referred_tables = [foreign_key["referred_table"] for foreign_key in foreign_keys]
                    
    #         for r_table in referred_tables:
    #             if r_table in excluded_tables and table_name not in excluded_tables:
    #                 excluded_tables.append(table_name)  
    #                 return self.filter_tables(table_names, excluded_tables, inspector)
                
    #     return excluded_tables
