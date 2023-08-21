# DataForge: Simplify Data Population in Your Database

![Data Forge Logo](https://github.com/MZaFaRM/DataForge/assets/98420006/d7ca0ca1-b958-4f78-82a2-f8b4ad3e4cf1)

DataForge is a Python tool designed to assist in generating and inserting realistic test data into your database. It aims to simplify tasks like detecting foreign key relations, with a focus on user-friendly design and efficiency. Whether you're a web developer, AI enthusiast, or tech enthusiast, you may find DataForge to be a useful addition to your toolkit.

## 🚀 Key Features

### Automated Data Generation
DataForge simplifies the data population process by automatically detecting foreign key relations and inserting data that respects these relations. No more manual data entry or complex scripting.

### Customizable Configuration
Tailor DataForge to meet your specific needs. Adjust the number of rows to insert, select tables to fill, and customize data generation instructions to match your database schema.

### Data Visualization
Gain insights into your data structure. DataForge provides a visualization of your database's foreign relations graph after data insertion, making it easier to understand your data model.

## 📖 How to Use

Getting started with DataForge is a breeze:

1. **Install Dependencies:** Begin by installing the required dependencies. Run the following command:
   
```
pip install -r requirements.txt
```


2. **Database Connection:** Set up your database connection details in the `.env` file following the example in `.env.sample`.

3. **Configuration:** Customize DataForge's behavior by configuring the `data.py` file. Here, you can specify the number of rows to insert, exclude tables from data insertion, and more.

4. **Run DataForge:** Execute `main.py` to start populating your database effortlessly.

## ⚙️ Configuration

![Code Snapshot](https://github.com/MZaFaRM/DataForge/assets/98420006/78a2f15d-2ad7-4f56-a39b-6abb3ff07db2)

DataForge's flexibility lies in its configuration options in `data.py`. You can fine-tune the tool to your precise requirements:

- `number_of_fields`: Specify the number of rows to insert into the database.
- `excluded_tables`: Define a list of tables to exclude from data insertion.
- `tables_to_fill`: Select specific tables for data insertion; leave it empty to fill all tables.
- `graph`: Opt to display the database's foreign relations graph after data insertion.
- `field`: Configure how columns are identified and filled with data.



  | Field       | Description                                         |
  |-------------|-----------------------------------------------------|
  | `name`      | The name of the field.                             |
  | `type`      | The type of the field.                             |
  | `table`     | The name of the table where the field is located. |
  | `generator` | Generator function to be used for data insertion.  |


Feel free to adjust these configurations to match your unique use case.

## 🛠️ Prerequisites

- Python `3.11.3`
- MySQL database server

## 📦 Dependencies

DataForge relies on several essential Python libraries:

- SQLAlchemy `2.0.20`
- mysql-connector-python `8.1.0`
- Faker `18.9.0`
- matplotlib `3.7.2`
- networkx `3.1`
- python-decouple `3.8`
- rich `13.5.2`
- SQLAlchemy-Utils `0.41.1`

## 📞 Support

If you have any questions or need assistance with using DataForge, don't hesitate to contact me at muhammedzafar.mm@gmail.com. Your feedback is invaluable as I continue to enhance this tool.

Thank you for choosing DataForge! I hope it simplifies your data population tasks and proves to be a valuable asset in your development journey.
