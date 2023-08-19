import contextlib
import random
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
                self.make_relations(
                    inspector=inspector, excluded_tables=excluded_tables
                )

            self.arrange_graph()
            self.fill_table(inspector=inspector)
            print("[#00FF00] Operation successful!")
            if graph:
                self.draw_graph()
        except Exception as e:
            print("[#ff0000]Oops, something went wrong!")
            raise e

    def make_relations(
        self, inspector, excluded_tables: list = None, tables_to_fill: list = None
    ):
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
                    ordered_inheritance_relations[table] = self.inheritance_relations[
                        table
                    ]
                progress.update(
                    task, description=f"[{color}] Saving relations...", advance=step
                )

            self.inheritance_relations = ordered_inheritance_relations
            progress.update(
                task, description="[#00FF00] Ordered identified relations..."
            )

    def populate_fields(self, table_name):
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
                value = (
                    field["generator"]()
                    if callable(field["generator"])
                    else field["generator"]
                )

                if value is not None:
                    try:
                        return value[: self.column["type"].length]
                    except AttributeError:
                        return value

        return None

    def is_valid_regex(self, pattern):
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    def compare_column_with(self, data, type):
        if data:
            if self.is_valid_regex(data):
                return re.search(data, str(self.column[type]), re.IGNORECASE)
            return data in str(self.column[type]).lower()
        else:
            return False

    def get_value(self, column, foreign_keys, table_name):
        self.column = column

        value = self.populate_fields(table_name)
        if value is not None:
            return value
        value = self.process_foreign(foreign_keys, table_name)
        if value is not None:
            return value
        else:
            raise NotImplementedError("Can you please raise an issue on github?")

    def process_foreign(self, foreign_keys, table_name):
        if self.column["name"] not in foreign_keys:
            return None

        desc = foreign_keys[self.column["name"]]
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine, only=[desc[1]])
        related_table = metadata.tables[desc[1]]
        conn = self.engine.connect()

        s = sqlalchemy.select(related_table.c[desc[0]])
        result = conn.execute(s).fetchall()

        items = [row[0] for row in result]

        column_metadata = related_table.c[desc[0]]
        unique_constraint = column_metadata.unique

        unique_rows = []

        if unique_constraint:
            s = sqlalchemy.select(table_name.c[self.column["name"]])
            result = conn.execute(s).fetchall()
            unique_rows = [row[0] for row in result]

            if len(unique_rows) == len(items):
                raise ValueError("Exhausted Choices")

        conn.close()
        random_element = self.fake.random_element(elements=items)

        while random_element in unique_rows:
            random_element = self.fake.random_element(element=items)
        return random_element

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
        row_data

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
