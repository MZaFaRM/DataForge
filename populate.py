import contextlib
import random
import time
from faker import Faker
import re
from pyparsing import col
import sqlalchemy
from sqlalchemy import create_engine, inspect
import networkx as nx
import matplotlib.pyplot as plt
from collections import OrderedDict
from sqlalchemy.exc import IntegrityError
from rich.progress import Progress
from rich import print
from sqlalchemy_utils import has_unique_index
from sqlalchemy import text


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
        db_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        self.rows = rows
        self.special_fields = special_fields

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

    def populate_fields(self, column, table):
        for field in self.special_fields:
            if (
                self.compare_column_with(column, field["name"], "name")
                or self.compare_column_with(column, field["type"], "type")
                and (
                    True
                    if (field.get("table") and field["table"] == table.name)
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
                        return str(value)[: column.type.length]
                    except AttributeError:
                        return value

        return None

    def is_valid_regex(self, pattern):
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    def compare_column_with(self, column, data, type):
        if data:
            if self.is_valid_regex(data):
                return re.search(data, str(getattr(column, type)), re.IGNORECASE)
            return data in str(self.column[type]).lower()
        else:
            return False

    def handle_column_population(self, table, column):
        tried_values = set()
        value = self.populate_fields(column, table)
        count = 30
        while value in self.existing_values or value in tried_values:
            tried_values.add(value)
            value = self.populate_fields(column, table)
            print(f"Trying {value}, attempt number {count}")
            count -= 1
            if count <= 0:
                raise ValueError(
                    f"Can't find a unique value to insert into column '{column.name}' in table '{table.name}'"
                )

        return value

    def get_unique_column_values(self, column, unique_columns, table):
        """
        The function `get_unique_column_values` returns all values from a specified column in a table if the
        column is in a list of unique columns, otherwise it returns an empty list.

        :param column: The "column" parameter is an object representing a column in a database table. It
        has properties such as "name" to get the name of the column
        :param unique_columns: A list of column names that are considered unique in the table
        :param table: The `table` parameter is a SQLAlchemy table object. It represents a database table and
        is used to perform database operations such as selecting, inserting, updating, and deleting data
        :return: a list of unique values from the specified column in the given table.
        """

        if column.name in unique_columns:
            if column in self.cached_unique_column_values:
                return self.cached_unique_column_values[column]

            conn = self.engine.connect()
            s = sqlalchemy.select(table.c[column.name])

            self.cached_unique_column_values[column] = {
                row[0] for row in conn.execute(s).fetchall()
            }
            conn.close()
            
            return self.cached_unique_column_values[column]
        return set()

    def get_value(self, column, foreign_columns, unique_columns, table):
        self.existing_values = self.get_unique_column_values(
            column=column, unique_columns=unique_columns, table=table
        )

        value = self.process_foreign(
            column=column,
            foreign_columns=foreign_columns,
            table=table,
        )
        if value is not None:
            return value

        value = self.handle_column_population(table=table, column=column)
        if value is not None:
            return value

        else:
            raise NotImplementedError("Can you please raise an issue on github?")

    def get_related_table_fields(self, column, foreign_columns):
        desc = foreign_columns[column.name]
        if desc in self.cached_related_table_fields:
            return self.cached_related_table_fields[desc]

        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine, only=[desc[1]])
        related_table = metadata.tables[desc[1]]
        conn = self.engine.connect()
        s = sqlalchemy.select(related_table.c[desc[0]])

        self.cached_related_table_fields[desc] = {
            row[0] for row in conn.execute(s).fetchall()
        }
        
        conn.close()

        return self.cached_related_table_fields[desc]

    def process_foreign(self, foreign_columns, table, column):
        if column.name not in foreign_columns:
            return None

        related_table_fields = self.get_related_table_fields(column, foreign_columns)
        if selectable_fields := related_table_fields - self.existing_values:
            return random.choice(list(selectable_fields))
        else:
            raise ValueError(
                f"Can't find a unique value to insert into column '{column.name}' in table '{table.name}'"
            )

    def get_unique_columns(self, table):
        return [column.name for column in table.columns if has_unique_index(column)]

    def get_foreign_columns(self, inspector, table):
        return {
            foreign_key["constrained_columns"][0]: (
                foreign_key["referred_columns"][0],
                foreign_key["referred_table"],
            )
            for foreign_key in inspector.get_foreign_keys(table.name)
        }

    def process_row_data(self, table, unique_columns, foreign_columns):
        return {
            column.name: self.get_value(
                column=column,
                unique_columns=unique_columns,
                foreign_columns=foreign_columns,
                table=table,
            )
            for column in table.columns
        }

    def fill_table(self, inspector):
        for table_name in self.inheritance_relations:
            self.handle_database_insertion(table_name, inspector)

    def handle_database_insertion(self, table_name, inspector):
        self.metadata = sqlalchemy.MetaData()
        self.metadata.reflect(bind=self.engine, only=[table_name])
        table = self.metadata.tables[table_name]
        unique_columns = self.get_unique_columns(table=table)
        foreign_columns = self.get_foreign_columns(inspector=inspector, table=table)

        with Progress() as progress:
            color = self.rnd_color()
            task = progress.add_task(
                f"[{color}] Inserting rows into {table_name}...",
                total=100,
                pulse=True,
            )

            for _ in range(self.rows):
                # This variable is used to cache the related table fields
                # so that we don't have to query the database every time
                # we need to get the related table fields
                # Its usage can be found in the `get_related_table_fields` function
                self.cached_related_table_fields = {}

                # Similarly to the `cached_related_table_fields` variable
                # This variable is used to cache the unique column values
                # so that we don't have to query the database every time
                # we need to get the unique column values
                # Its usage can be found in the `get_unique_column_values` function
                self.cached_unique_column_values = {}

                row_data = self.process_row_data(
                    table=table,
                    unique_columns=unique_columns,
                    foreign_columns=foreign_columns,
                )

                self.database_insertion(table=table, entries=row_data)

                progress.update(
                    task,
                    description=f"[{color}] Inserting rows into {table_name}...",
                    advance=100 / self.rows,
                )

    def database_insertion(self, table, entries):
        with self.engine.begin() as connection:
            connection.execute(table.insert().values(**entries))

    def rnd_color(self):
        # rgb = [random.randint(100, 255) for _ in range(3)]
        # return '#{:02x}{:02x}{:02x}'.format(*rgb)
        return random.choice(["#00ff00", "#91C788"])
