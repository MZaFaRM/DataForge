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
        graph: bool = True,
    ) -> None:

        db_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        self.rows = rows

        self.engine = create_engine(db_url, echo=False)

        inspector = inspect(self.engine)
        self.make_relations(inspector=inspector, excluded_tables=excluded_tables)

        self.arrange_graph()
        self.fill_table(inspector=inspector)
        print("[Green]Operation successful!")
        if graph:
            self.draw_graph()

    def make_relations(self, inspector, excluded_tables):
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Identifying table relations...", total=100, pulse=True
            )

            table_names = inspector.get_table_names()
            progress.update(task, description="[cyan]Getting table names", advance=10)

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
                    description="[cyan]Tracking foreign relations...",
                    advance=step,
                )

            progress.update(
                task, description="[cyan]Removing excluded tables...", advance=10
            )
            self.inheritance_relations.pop(*excluded_tables)
            progress.update(
                task, description="[cyan]Foreign key relations identified..."
            )
            return self.inheritance_relations

    def draw_graph(self):
        graph = nx.DiGraph()

        for table, inherited_tables in self.inheritance_relations.items():
            for inherited_table in inherited_tables:
                graph.add_edge(inherited_table, table)

        plt.figure(figsize=(12, 8))
        pos = nx.shell_layout(graph)
        nx.draw_networkx(
            graph, pos, with_labels=True, edge_color="gray", node_size=0, font_size=10
        )

        plt.title("Database Inheritance Relationships")
        plt.axis("off")
        plt.show()

    def arrange_graph(self):
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Ordering identified relations...", total=100, pulse=True
            )
            graph = nx.DiGraph()

            step = 60 / len(self.inheritance_relations)
            for table, inherited_tables in self.inheritance_relations.items():
                for inherited_table in inherited_tables:
                    graph.add_edge(inherited_table, table)
                progress.update(
                    task, description="[cyan]Establishing connections...", advance=step
                )

            ordered_tables = list(nx.topological_sort(graph))

            ordered_inheritance_relations = OrderedDict()

            step = 40 / len(ordered_tables)
            for table in ordered_tables:
                ordered_inheritance_relations[table] = self.inheritance_relations[table]
                progress.update(
                    task, description="[cyan]Saving relations...", advance=step
                )

            self.inheritance_relations = ordered_inheritance_relations
            progress.update(task, description="[cyan]Ordered identified relations...")

    def get_value(self, column, foreign_keys):
        fake = Faker("en_IN")
        column_name = column["name"]
        data_type = column["type"]

        pattern = re.compile(r"(\bid)|(_id)|(id_)", re.IGNORECASE)

        if column_name in foreign_keys:
            value = self.process_foreign(foreign_keys, column_name, fake)
        elif re.search(pattern, column_name):
            value = fake.uuid4()
        elif "first_name" in column_name:
            value = fake.first_name()[: data_type.length]
        elif "last_name" in column_name:
            value = fake.last_name()[: data_type.length]
        elif "description" in column_name:
            value = fake.sentence()[: data_type.length]
        elif "email" in column_name:
            value = fake.email()[: data_type.length]
        elif "password" in column_name:
            value = fake.password()[: data_type.length]
        elif "mobile" in column_name:
            value = fake.phone_number()[: data_type.length]
        elif "gender" in column_name:
            value = fake.random_element(elements=["Male", "Female"])
        elif "varchar" in str(data_type).lower():
            value = fake.name()[: data_type.length]
        elif "integer" in str(data_type).lower():
            value = fake.random_int(min=0, max=100)
        elif "date" in str(data_type).lower():
            value = fake.date()
        elif "datetime" in str(data_type).lower():
            value = fake.date_time()
        elif "tinyint" in str(data_type).lower():
            value = fake.random_element(elements=[0, 1])
        elif "bigint" in str(data_type).lower():
            value = fake.random_int(min=0, max=1000)

        return value

    def process_foreign(self, foreign_keys, column_name, fake):
        desc = foreign_keys[column_name]
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

        return fake.random_element(elements=items)

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
            column["name"]: self.get_value(column, foreign_keys) for column in columns
        }

    def fill_table(self, inspector):
        for table_name in self.inheritance_relations:
            with Progress() as progress:
                task = progress.add_task(
                    f"[cyan]Inserting rows into {table_name}...", total=100, pulse=True
                )
                for _ in range(self.rows):
                    status = self.database_insertion(table_name, inspector)
                    while not status:
                        progress.update(
                            task,
                            description="[red]An Integrity Error occurred trying again...",
                        )
                        status = self.database_insertion(table_name, inspector)

                    progress.update(
                        task,
                        description=f"[cyan]Inserting rows into {table_name}...",
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
