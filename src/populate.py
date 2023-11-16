import contextlib
import random
import re
from collections import OrderedDict
import time

import matplotlib.pyplot as plt
import networkx as nx
import sqlalchemy
from rich import print
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlalchemy import create_engine, inspect
from sqlalchemy_utils import has_unique_index
from rich import print
import keyboard


class DatabasePopulator:
    """
    The `DatabasePopulator` class is used to populate a database with random data. It uses the SQLAlchemy library to
    connect to a database and populate it with random data using `Faker`. It can be used to populate a database with random
    data for testing purposes or to populate a database with random data for a demo.

    Parameters:
        - `user` (str): The username of the database user.
        - `password` (str): The password of the database user.
        - `host` (str): The host name or IP address of the database server.
        - `database` (str): The name of the database to connect to.
        - `rows` (int): The number of rows to insert into each table.
        - `excluded_tables` (list): A list of table names to exclude from inheritance relations analysis.
        - `tables_to_fill` (list): A list of table names to fill with data. If empty, all tables in the database will be filled.
        - `graph` (bool): Determines whether to display the graph after data insertion.
        - `special_fields` (list of dict): Contains instructions for identifying and filling columns.
    """

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

        self.completed_tables_list = []
        self.special_fields = special_fields

        self.current_progress = 0

        self.engine = create_engine(db_url, echo=False)
        self.rows = rows
        inspector = inspect(self.engine)

        # If no tables are specified, fill all tables in the database
        # Otherwise, fill the specified tables
        tables_to_fill = tables_to_fill or inspector.get_table_names()
        tables_to_fill = set(tables_to_fill) - set(excluded_tables or [])
        total_len = len(tables_to_fill)
        if total_len == 0:
            raise ValueError(
                "I can't find any tables to fill. Check your "
                "`tables_to_fill` and `excluded_tables` "
                "parameters, maybe they need some tweaks?"
            )

        # Defines the layout of the CLI
        self.layout = self.get_layout(total_len)

        with Live(self.layout, refresh_per_second=10, screen=True):
            # Initializes the progress bar
            self.make_jobs(total_len)

            # Identifies inheritance relations between tables
            self.make_relations(
                inspector=inspector,
                tables_to_fill=tables_to_fill,
                excluded_tables=excluded_tables,
            )

            # Arranges inheritance relations in a directed graph
            self.arrange_graph()

            # Populates the database with random data
            self.fill_table(inspector=inspector)

            if graph:
                self.draw_graph()
            else:
                time.sleep(2)

        self.show_end_banner()

    def show_end_banner(self):
        with open("assets/banner.txt", encoding="utf-8") as f:
            banner = f.readlines()

        print()
        [
            print(
                Align(
                    bane.strip(),
                    align="center",
                )
            )
            for bane in banner
        ]

        success = random.choice(
            [
                "Voila!",
                "Wow!",
                "Ta-da!",
                "Yay!",
                "Oops!",
                "Woah!",
                "Cool!",
                "Bam!",
                "Eureka!",
                "Aha!",
                "Hooray!",
                "Oof!",
            ]
        )

        print(
            Align(
                f"[yellow]{success}[/] smoothly inserted {self.current_progress} rows.",
                align="center",
            )
        )
        print()

    def get_layout(self, tables_to_fill):
        """
        The function `get_layout` defines the layout of the CLI.
        """
        self.make_jobs(tables_to_fill)
        self.all_tables = tables_to_fill

        layout = self.make_layout()
        layout["header"].update(self.make_header())
        layout["body"].update(
            Panel(self.make_query_grid(), title="[green b]DATA ENTRY")
        )
        self.set_progress(layout)

        return layout

    def make_layout(self) -> Layout:
        """Define the layout."""
        layout = Layout(name="root")

        layout.split(
            Layout(name="header", size=10),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=7),
        )
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="body", ratio=2, minimum_size=60),
            Layout(name="right"),
        )

        return layout

    def make_jobs(self, tables_to_fill):
        """
        The function `make_jobs` initializes all the progress bars.

        """
        self.job_progress = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        self.identifying_relations = self.job_progress.add_task(
            "[green]Identifying relations", total=10
        )
        self.inserting_data = self.job_progress.add_task(
            "[magenta]Inserting data into tables",
            total=self.rows * tables_to_fill,
        )

    def set_progress(self, layout=None):
        """
        The function `set_progress` sets the progress bar in the footer of the CLI.
        """
        layout = layout or self.layout
        progress_table = Table.grid(expand=True)
        progress_table.add_row(
            Panel(
                Align.center(self.job_progress, vertical="middle"),
                title="[b]Progress",
                border_style="red",
                padding=(1, 2),
                subtitle="[yellow]Thanks for checking out my project! Do consider giving it a star on [link=https://github.com/MZaFaRM/DataForge/]GitHub[/link] and feel free to [link=https://www.linkedin.com/in/muhammed-zafar-mm/]reach out[/link] anytime.",
            ),
        )
        layout["footer"].update(progress_table)

    def handle_table_panel(self, left_tables) -> None:
        self.get_table_panel(left_tables, "left", "TABLES REMAINING")

        completed_tables_list = self.completed_tables_list.copy()
        completed_tables_list.reverse()

        self.get_table_panel(completed_tables_list, "right", "COMPLETED TABLES")

    def get_table_panel(self, table_name, side, title):
        tables_grid = Table.grid(padding=0)
        [tables_grid.add_row(f" {table_name}") for table_name in table_name]
        table_panel = Panel(Align.center(tables_grid), title=f"[green b]{title}")
        self.layout["main"][side].update(table_panel)

    def make_query_grid(self):
        self.query_grid = Table.grid(padding=1, expand=True)
        self.query_grid.add_column(ratio=1)
        self.query_grid.add_column(ratio=3)

        return self.query_grid

    def make_header(self) -> Panel:
        grid = self.get_banner("assets/banner.txt")
        grid.add_row(
            "From [b link=https://github.com/MZaFaRM/]Muhammed Zafar[/]",
        )
        return Panel(grid, style="purple on black")

    def get_banner(self, address):
        result = Table.grid(expand=True)
        result.add_column(justify="center")
        with open(address, encoding="utf-8") as banner:
            banner_lines = banner.readlines()
            [result.add_row(line.strip()) for line in banner_lines]
        return result

    def make_relations(
        self,
        inspector,
        excluded_tables: list = None,
        tables_to_fill: list = None,
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

        self.job_progress.advance(self.identifying_relations)
        self.handle_table_panel(tables_to_fill)

        self.job_progress.advance(self.identifying_relations)
        # The `self.inheritance_relations` is a list of tables arranged in a topological order
        # Respecting the inheritance relations between tables, It provides the order in which
        # the tables should be filled with data
        self.inheritance_relations = {}
        step = 8 / len(tables_to_fill)

        self.define_relations(inspector, tables_to_fill, step, excluded_tables)

    def define_relations(self, inspector, table_names, step, excluded_tables):
        for table_name in table_names:
            foreign_keys = inspector.get_foreign_keys(table_name)
            referred_tables = {
                foreign_key["referred_table"] for foreign_key in foreign_keys
            }
            self.inheritance_relations[table_name] = list(referred_tables)
            self.job_progress.advance(self.identifying_relations, advance=step)

            if excluded_tables:
                for table in excluded_tables:
                    with contextlib.suppress(KeyError):
                        self.inheritance_relations.pop(table)

            self.job_progress.advance(self.identifying_relations)

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
        topologically. It involves the user in resolving circular dependencies.
        """
        graph = nx.DiGraph()
        # Populate the graph
        for table, inherited_tables in self.inheritance_relations.items():
            if inherited_tables:
                for inherited_table in inherited_tables:
                    if table != inherited_table:  # Skip self-references
                        graph.add_edge(inherited_table, table)
            else:
                graph.add_node(table)

            self.job_progress.advance(self.identifying_relations)

        # Detect cycles
        try:
            ordered_tables = list(nx.topological_sort(graph))
        except nx.NetworkXUnfeasible as e:
            cycles = list(nx.simple_cycles(graph))
            ordered_cycles = self.resolve_cycles_with_user_input(cycles=cycles)

            graph = nx.DiGraph()

            # Populate the graph
            for table, inherited_tables in self.inheritance_relations.items():
                if inherited_tables:
                    for inherited_table in inherited_tables:
                        if table != inherited_table:  # Skip self-references
                            if (
                                table in ordered_cycles
                                and inherited_table in ordered_cycles
                                and ordered_cycles.index(table)
                                > ordered_cycles.index(inherited_table)
                            ):
                                continue
                            graph.add_edge(inherited_table, table)
                else:
                    graph.add_node(table)

                self.job_progress.advance(self.identifying_relations)
            ordered_tables = list(nx.topological_sort(graph))

        # Order the tables based on topological sort or user resolution
        ordered_inheritance_relations = OrderedDict()
        for table in ordered_tables:
            if table in self.inheritance_relations:
                ordered_inheritance_relations[table] = self.inheritance_relations[table]

            self.job_progress.advance(self.identifying_relations)

        self.inheritance_relations = ordered_inheritance_relations
        self.job_progress.advance(self.identifying_relations)

    def resolve_cycles_with_user_input(self, cycles):
        """
        Ask the user to resolve the detected cycles and return the adjusted order of tables.
        """
        current_index = 0
        cycles = list({item for cycle in cycles for item in cycle})

        self.generate_circular_dependency_list(cycles, current_index)
        while True:
            key = keyboard.read_event(suppress=False)
            if key.event_type == "down":
                key = key.name
                if key == "up":
                    if current_index > 0:
                        current_index -= 1
                        self.generate_circular_dependency_list(cycles, current_index)
                elif key == "down":
                    if current_index < len(cycles) - 1:
                        current_index += 1
                        self.generate_circular_dependency_list(cycles, current_index)
                elif key in ["+", "="]:
                    cycles, current_index = self.update_list_based_on_user_input(
                        cycles, 1, current_index
                    )
                elif key in ["-", "_"]:
                    cycles, current_index = self.update_list_based_on_user_input(
                        cycles, -1, current_index
                    )

                elif key == "enter":
                    # Handle 'Enter' key press (e.g., save the selected order)
                    return cycles
                elif key == "esc":
                    # Handle 'Esc' key press (e.g., exit or cancel)
                    break

    def display_list(self, indexed_list):
        self.layout["body"].update(
            Panel(
                Align.center("\n".join(indexed_list)),
                highlight=True,
                padding=1,
                expand=True,
                title="[yellow b]WARNING",
            )
        )

    def update_list_based_on_user_input(self, cycles, step, current_index):
        if step == -1:
            if (current_index + 1) < len(cycles):
                cycles[current_index], cycles[current_index + 1] = (
                    cycles[current_index + 1],
                    cycles[current_index],
                )
            current_index += 1
        elif step == 1:
            if current_index > 0:
                cycles[current_index], cycles[current_index - 1] = (
                    cycles[current_index - 1],
                    cycles[current_index],
                )
            current_index -= 1
        self.generate_circular_dependency_list(cycles, current_index)
        return cycles, current_index

    def generate_circular_dependency_list(self, cycles, current_index):
        """
        Generate a formatted list of circular dependencies for user interaction.

        Args:
            cycles (list): A list of lists, where each inner list represents a cycle of dependencies.
            and prints a formatted list with circular dependencies and instructions.

        Returns:
            None
        """
        cycles = cycles.copy()

        # Highlight the first table
        cycles[current_index] = f"[black on white]{cycles[current_index]}[/]"

        # Create the indexed list with proper formatting
        indexed_list = [
            f"{index}. {item}" for index, item in enumerate(cycles, start=1)
        ]

        # Insert headers and instructions
        indexed_list.insert(
            0, "[b red]Circular dependencies detected in the following tables,"
        )
        indexed_list.insert(1, "provide an order to fill:[/b red]\n")
        indexed_list.insert(
            2, "[i yellow]Use arrow keys to navigate, `+` to move an item up the list,"
        )
        indexed_list.insert(
            3, "`-` to move an item down the list, and `Enter` to save.[/i yellow]\n\n"
        )

        self.display_list(indexed_list)

    def populate_fields(self, column, table):
        """
        The function `populate_fields` populates a
        column with a value based on the column's name, type, and
        table name.
        """
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
                # If the generator is a function, call it and return the result
                value = (
                    field["generator"]()
                    if callable(field["generator"])
                    else field["generator"]
                )
                # If the value is a string, truncate it to the column's length
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
        """
        Compares a column with a given data using a specified type of comparison.
        it could be a regex or a string comparison.
        and the type could be the column's `name` or `type`.
        """
        if data:
            if self.is_valid_regex(data):
                return re.search(data, str(getattr(column, type)), re.IGNORECASE)
            return data in str(self.column[type]).lower()
        else:
            return False

    def handle_column_population(self, table, column):
        """
        This function handles the population of a column with a value.
        It first checks if the column is a foreign key, if it is, it
        returns a value from the related table. If it's not, it checks
        if the column is unique, if it is, it returns a unique value
        for the column. If it's not, it returns None.
        """
        tried_values = set()
        value = self.populate_fields(column, table)
        count = 30
        while value in self.existing_values or value in tried_values:
            tried_values.add(value)
            value = self.populate_fields(column, table)
            count -= 1
            if count <= 0:
                raise ValueError(
                    (
                        f"I can't find a unique value "
                        f"to insert into column '{column.name}' in "
                        f"table '{table.name}'"
                    )
                )

        return value

    def get_unique_column_values(self, column, unique_columns, table):
        """
        The function returns all values from a specified column in a table if the
        column is in a list of unique columns, otherwise it returns an empty list.
        """

        if column.name in unique_columns:
            # If the column's unique values have already been cached, return them
            if column in self.cached_unique_column_values:
                return self.cached_unique_column_values[column]

            conn = self.engine.connect()
            s = sqlalchemy.select(table.c[column.name])

            # Cache the column's unique values
            self.cached_unique_column_values[column] = {
                row[0] for row in conn.execute(s).fetchall()
            }
            conn.close()

            return self.cached_unique_column_values[column]
        return set()

    def get_value(self, column, foreign_columns, unique_columns, table):
        """
        The function `get_value` returns a value for a column in a table.
        """
        # It first checks if the column is unique, if it is, it fetches a
        # set of unique values to insert
        self.existing_values = self.get_unique_column_values(
            column=column, unique_columns=unique_columns, table=table
        )
        # it calls the `process_foreign`
        # function to check if the column is a foreign key
        # if it is, it returns a value from the related table
        if None is not (
            value := self.process_foreign(
                column=column,
                foreign_columns=foreign_columns,
                table=table,
            )
        ):
            return value
        # if the column is not a foreign key, it calls the `handle_column_population`
        # function to populate the column with a value based on the definition from
        # the `data.py` file
        elif None is not (
            value := self.handle_column_population(table=table, column=column)
        ):
            return value
        elif column.nullable:
            return None
        else:
            raise NotImplementedError(
                "I have no idea what value to assign "
                f"to the field '{column.name}' of type ",
                f"{column.type} in '{table}'. "
                "Maybe updating my `data.py` will help?"
            )

    def get_related_table_fields(self, column, foreign_columns):
        """
        The function `get_related_table_fields` returns a set of values from a related table
        """
        # desc is a tuple containing the
        # (name of the column, the name of the related table)
        desc = foreign_columns[column.name]
        # If the related table fields have already been cached, return them
        if desc in self.cached_related_table_fields:
            return self.cached_related_table_fields[desc]

        # Otherwise, query the database to get the related table fields
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=self.engine, only=[desc[1]])
        related_table = metadata.tables[desc[1]]
        conn = self.engine.connect()
        s = sqlalchemy.select(related_table.c[desc[0]])

        # and cache the related table fields
        self.cached_related_table_fields[desc] = {
            row[0] for row in conn.execute(s).fetchall()
        }

        conn.close()

        return self.cached_related_table_fields[desc]

    def process_foreign(self, foreign_columns, table, column):
        """
        The function `process_foreign` checks if a column is a foreign key, if it is,
        it returns a value from the related table.
        """
        if column.name not in foreign_columns:
            return None
        # Gets the related table fields from the `get_related_table_fields` function
        related_table_fields = self.get_related_table_fields(column, foreign_columns)

        # self.existing_values only gets populated if the column only accepts to unique values
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
        """
        The function `process_row_data` processes the data for a row in a table.
        """
        data = {}
        # query_grid is a table that displays the column name and the value
        # It's at the middle of the CLI and it gets updated every time a column
        # gets a value
        query_grid = self.make_query_grid()
        for column in table.columns:
            # The `get_value` function returns a value for a column
            data[column.name] = self.get_value(
                column=column,
                unique_columns=unique_columns,
                foreign_columns=foreign_columns,
                table=table,
            )
            # The `query_grid` gets updated with the column name and the value
            query_grid.add_row(f"[yellow]{column.name}", f"[green]{data[column.name]}")
            self.layout["body"].update(
                Panel(
                    Align.center(query_grid),
                    highlight=True,
                    padding=1,
                    expand=True,
                    title="[green b]DATA ENTRY",
                )
            )
        return data

    def fill_table(self, inspector):
        """
        The most important function in this class. It fills the tables with data.
        and it's called after the inheritance relations have been identified and
        arranged in a directed graph.
        """
        # The `self.inheritance_relations_list` is a list of tables arranged in a topological order
        # derived from the `self.inheritance_relations` OrderedDict variable defined in the
        # `arrange_graph` function
        self.inheritance_relations_list = list(self.inheritance_relations)

        # The `self.inheritance_relations` is a list of tables arranged in a topological order
        for table_name in self.inheritance_relations.copy():
            # Color the current table being filled's name in yellow
            table_name_index = self.inheritance_relations_list.index(table_name)
            self.inheritance_relations_list[table_name_index] = f"[yellow]{table_name}"

            # Update the table panel with the current table being filled's name
            self.handle_table_panel(self.inheritance_relations_list)

            # Call the `handle_database_insertion` function to fill the current table
            self.handle_database_insertion(table_name, inspector)

            # Logic for how to display the table after it has been filled
            self.inheritance_relations_list.remove(f"[yellow]{table_name}")
            self.completed_tables_list.append(f"[green]{table_name}")
            self.handle_table_panel(self.inheritance_relations_list)

    def handle_database_insertion(self, table_name, inspector):
        """
        The function `handle_database_insertion` fills a table with data.
        """
        self.metadata = sqlalchemy.MetaData()
        self.metadata.reflect(bind=self.engine, only=[table_name])
        table = self.metadata.tables[table_name]
        unique_columns = self.get_unique_columns(table=table)
        foreign_columns = self.get_foreign_columns(inspector=inspector, table=table)

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

            # The `row_data` variable contains the data for a row in a table
            row_data = self.process_row_data(
                table=table,
                unique_columns=unique_columns,
                foreign_columns=foreign_columns,
            )
            # The `database_insertion` function inserts the data into the database
            self.database_insertion(table=table, entries=row_data)

    def database_insertion(self, table, entries):
        # Simply inserts the data into the database
        with self.engine.begin() as connection:
            connection.execute(table.insert().values(**entries))
            # Advances the progress bar
            self.job_progress.advance(self.inserting_data)
            self.set_progress()
            # Updates the number of rows inserted
            self.current_progress += 1
