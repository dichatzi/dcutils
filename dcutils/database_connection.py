import pandas as pd
import warnings
warnings.simplefilter("ignore")
import urllib
import sqlalchemy
import math
import pymongo


class DatabaseObject:
    def __init__(self, database, username, password, servername, port, database_type="postgres"):
    
        # Database data
        self.database = database
        self.username = username
        self.password = urllib.parse.quote_plus(password)
        self.servername = servername
        self.port = port

        # Create engine
        match database_type:
            case "postgres":
                self.engine = sqlalchemy.create_engine(f'postgresql://{self.username}:{self.password}@{self.servername}:{self.port}/{self.database}')
            case _:
                print("You have not selected a correct database type!")
        
        # Connect to engine
        self.connection = self.engine.connect()


class PgDatabaseData:
    def __init__(self, database_object, dataframe, database_name, schema_name, table_name, on_fields, upd_fields):
        self.database_object = database_object
        self.dataframe = dataframe
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_name = table_name
        self.on_fields = on_fields
        self.upd_fields = upd_fields

        # # Check if dataframe containts duplicate values
        # check_duplicates = dataframe[dataframe.duplicated(subset=on_fields, keep=False)]
        # if len(check_duplicates) > 0:
        #     self.contains_duplicates = True
        # else:
        #     self.contains_duplicates = False

    def upsert_table(self, truncate_table:bool=False, slice_length:int=0, sql_query:str=""):

        """
        INITIALIZE DATA
        """
        # Truncate table if flag is activated
        if truncate_table:
            # Create truncate table query
            truncate_table_query = sqlalchemy.text(f"TRUNCATE TABLE {self.database_name}.{self.schema_name}.{self.table_name}")
            self.database_object.connection.execute(truncate_table_query)

            # Commit changes
            self.database_object.connection.commit()

        # Execute custom sql query
        if len(sql_query) > 0:
            # Create custom sql query
            custom_sql_query = sqlalchemy.text(sql_query)
            self.database_object.connection.execute(custom_sql_query)

            # Commit changes
            self.database_object.connection.commit()


        # Calculate on fields string
        on_field = ""
        for on_id, field in enumerate(self.on_fields):
            prefix = ", " if on_id > 0 else ""
            on_field = f'{on_field}{prefix}"{field}"'

        # Calculate update fields string
        upd_field = ""
        for upd_id, field in enumerate(self.upd_fields):
            prefix = ", " if upd_id > 0 else ""
            upd_field = f'{upd_field}{prefix}"{field}"'

        # Calculate fields string
        fields = f"{on_field}, {upd_field}"

        # Calculate updates string
        updates = ""
        for id, field in enumerate(self.upd_fields):
            prefix = ", " if id > 0 else ""
            updates = f'{updates}{prefix}"{field}" = EXCLUDED."{field}"'


        """
        PERFORM UPSERT OPERATIONS
        """
        # Calculate the length of the examined slice
        slice = self.dataframe.shape[0] if slice_length==0 else slice_length

        # Find the number of iterations
        no_iterations = math.ceil(self.dataframe.shape[0] / slice)

        # Update table data for each iteration
        for i in range(no_iterations):
            # Calculate start and end rows
            start_row = i * slice
            last_row = min(start_row + slice, len(self.dataframe))

            # Create sub dataframe
            table_data = self.dataframe[start_row:last_row]

            # Uploading data
            if slice_length > 0:
                print(f"Slice {i + 1}: updating data")



            # > After that it was working before --------------------------
            # Insert dataframe data to temporary table
            table_data.to_sql("temp_table", self.database_object.engine, index=False, if_exists='replace')

            # Upsert data from temporary table to database
            upsert_table_query = sqlalchemy.text(f"INSERT INTO {self.database_name}.{self.schema_name}.{self.table_name} ({fields}) SELECT {fields} FROM temp_table WHERE true ON CONFLICT ({on_field}) DO UPDATE SET {updates}")
            self.database_object.connection.execute(upsert_table_query)
            
            # Drop temporary table
            drop_temporary_table_query = sqlalchemy.text("DROP TABLE IF EXISTS public.temp_table")
            self.database_object.connection.execute(drop_temporary_table_query)

            # Commit changes
            self.database_object.connection.commit()


def connect_to_mongo():

    # Create Mongo Connection 
    MONGO_CONNECTION_STRING = "mongodb://localhost:27017"
    
    # Connect to client
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    
    # Connect to database
    energy_management = client["energy_management"]
    
    # Connect to collection
    volue_forecasts = energy_management["volue_forecasts"]
    
    # Upsert data to database
    result = upsert_mongo(forecast_data, ["trading_date", "update_date", "bidding_area"], volue_forecasts)


def upsert_mongo(items, filters, collection):

    # Check if filter fields input is a list
    if not isinstance(filters, list):
        filters = [filters]
        
    # Create operations array
    operations = [
        pymongo.UpdateOne(
            {filter: item[filter] for filter in filters},
            {"$set": item},
            upsert=True
        )
        for item in items
    ]
    # Perform the bulk_write operation
    result = collection.bulk_write(operations)
    
    # Return result
    return result