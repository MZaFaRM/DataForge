# DataForge

<img width="926" alt="Data Forge home" src="https://github.com/MZaFaRM/DataForge/assets/98420006/d7ca0ca1-b958-4f78-82a2-f8b4ad3e4cf1">

DataForge is a Python tool that helps you populate databases with test data. It's designed to simplify the process of generating and inserting large volumes of realistic data into your database. It automatically detects foreign key relations and inserts data with respect to it.


## How to Use

1. Install the required dependencies by running the following command:

   ```
   pip install -r requirements.txt
   ```

2. Create and setup the `.env` file with the database connection details by referring to `.env.sample`.

3. [Configure `data.py`](#Configurations)

4. Run `main.py`.

## Configurations

![code-snapshot](https://github.com/MZaFaRM/DataForge/assets/98420006/78a2f15d-2ad7-4f56-a39b-6abb3ff07db2)

You can customize the behavior of this tool by modifying the following values from `data.py`:

- `number_of_fields`: the number of rows to insert into the database.
- `excluded_tables`: A list of tables to exclude from data insertion.
- `tables_to_fill`: A list of tables to insert data into. If empty, all tables in the database will be filled.
- `graph`: Displays the database foreign relations graph after data insertion.
- `field`: Contains instructions for identifying and filling columns.
  - `Field Name`: The name of the field.
  - `Field Type`: The type of the field.
  - `Table Name`: The name of the table where the field is located.
  - `Value Generation`: Instructions for generating values for the field.

Feel free to adjust these configurations based on your specific requirements.


## Support

For any questions or assistance with using DataForge, feel free to contact me at muhammedzafar.mm@gmail.com.
