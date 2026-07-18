import sqlite3
import pandas as pd
import sqlalchemy
import urllib
import math





class SqliteObject:

    def __init__(self, db_file:str=""):

        # Check if db_file is provided and create database and connection
        if db_file != "":
            self.db_file = db_file
            self.create_connection()

    def create_connection(self):

        self.connection = sqlite3.connect(self.db_file)     # Create connection

    def execute_query(self, query:str, commit:bool=False):

        # Create cursor
        cursor = self.connection.cursor()

        # Execute query
        cursor.execute(query)

        # Commit if required
        if commit:
            self.connection.commit()

    def upsert_data(self, data:pd.DataFrame, table_name:str, on_fields:list, clear_table:bool=False):

        # Clear table if flag is true
        if clear_table:
            self.execute_query(f"DELETE FROM {table_name}", commit=True)

        # Upload DataFrame to a temporary table
        data.to_sql('temp_table', self.connection, if_exists='replace', index=False)

        # Calculate update fields
        update_fields = [col for col in data.columns if col not in on_fields]

        # Calculate on fields string
        on_field = ', '.join(f'"{field}"' for field in on_fields)

        # Calculate update fields string
        update_field = ', '.join(f'"{field}" = EXCLUDED."{field}"' for field in update_fields)

        # Merge temporary table to main table
        update_query = f"""
                        INSERT INTO {table_name} ({', '.join('"' + str(col) + '"' for col in data.columns)})
                        SELECT * FROM temp_table WHERE true
                        ON CONFLICT ({on_field}) DO UPDATE SET {update_field}
                        """

        # Execute query
        self.execute_query(update_query, commit=True)

        # Optional: Drop the temporary table
        self.execute_query('DROP TABLE temp_table', commit=True)

    def commit(self):

        self.connection.commit()    # Enforce commit

    def close(self):
        self.connection.close()     # Close connection





class PostgresDatabase:
    """Manage a Postgres connection, run queries, and upsert dataframes.

    Combines the former DatabaseObject, PostgresSimpleData and PostgresData
    classes. Per-call data (dataframe, table, on_fields) is passed as method
    arguments instead of living in a separate object's constructor.
    """

    SUPPORTED_TYPES = {"postgres"}

    def __init__(self, database, username, password, servername, port, database_type="postgres"):
        if database_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported database_type: {database_type!r}")

        self.database = database
        self.username = username
        self.password = urllib.parse.quote_plus(password)
        self.servername = servername
        self.port = port

        self.engine = sqlalchemy.create_engine(
            f"postgresql://{self.username}:{self.password}"
            f"@{self.servername}:{self.port}/{self.database}"
        )
        self.connection = self.engine.connect()

    # ------------------------------------------------------------------ #
    # Lifecycle / context manager
    # ------------------------------------------------------------------ #
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the connection and dispose of the engine."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()

    # ------------------------------------------------------------------ #
    # Querying
    # ------------------------------------------------------------------ #
    def send_query(self, query: str) -> pd.DataFrame:
        result = self.connection.execute(sqlalchemy.text(query))
        self.connection.commit()
        return pd.DataFrame(result.fetchall(), columns=result.keys())

    # ------------------------------------------------------------------ #
    # Helpers: build a dataframe from dicts
    # ------------------------------------------------------------------ #
    @staticmethod
    def _check_array(value):
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, (list, tuple, set)):
            return list(value)
        return [value]

    def _merge_dicts(self, dict_a, dict_b):
        return {
            **{k: self._check_array(v) for k, v in dict_a.items()},
            **{k: self._check_array(v) for k, v in dict_b.items()},
        }

    def pass_data(self, schema, table, on_fields, upd_fields, slice_length=10000):

        """Convenience wrapper: build a dataframe from dicts and upsert it."""
        data = self._merge_dicts(on_fields, upd_fields)
        df = pd.DataFrame(data=data)
        return self.upsert_table(
            dataframe=df,
            schema=schema,
            table=table,
            on_fields=list(on_fields.keys()),
            slice_length=slice_length,
        )

    # ------------------------------------------------------------------ #
    # Upsert
    # ------------------------------------------------------------------ #
    def upsert_table(self, dataframe, schema, table, on_fields, truncate_table: bool = False, slice_length: int = 0, sql_query: str = ""):

        upd_fields = [c for c in dataframe.columns if c not in on_fields]
        target = f"{self.database}.{schema}.{table}"

        # Optional pre-steps
        if truncate_table:
            self.connection.execute(sqlalchemy.text(f"TRUNCATE TABLE {target}"))
            self.connection.commit()

        if sql_query:
            self.connection.execute(sqlalchemy.text(sql_query))
            self.connection.commit()

        # Build column / conflict / update clauses
        on_field = ", ".join(f'"{f}"' for f in on_fields)
        fields = ", ".join(f'"{f}"' for f in [*on_fields, *upd_fields])
        updates = ", ".join(f'"{f}" = EXCLUDED."{f}"' for f in upd_fields)

        # Slice the dataframe and upsert in chunks
        slice_size = dataframe.shape[0] if slice_length == 0 else slice_length
        no_iterations = math.ceil(dataframe.shape[0] / slice_size) if slice_size else 0

        for i in range(no_iterations):
            start_row = i * slice_size
            last_row = min(start_row + slice_size, len(dataframe))
            table_data = dataframe[start_row:last_row]

            if slice_length > 0:
                print(f"Slice {i + 1}: updating data")

            # Stage chunk in a temp table, then upsert from it
            table_data.to_sql("temp_table", self.engine, index=False,
                              if_exists="replace")

            self.connection.execute(sqlalchemy.text(
                f"INSERT INTO {target} ({fields}) "
                f"SELECT {fields} FROM temp_table WHERE true "
                f"ON CONFLICT ({on_field}) DO UPDATE SET {updates}"
            ))
            self.connection.execute(
                sqlalchemy.text("DROP TABLE IF EXISTS public.temp_table")
            )
            self.connection.commit()

        return dataframe



def postgres_commands():
    
    commands = r"""
    psql postgres
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'your_password';
    /opt/homebrew/opt/postgresql@16/bin/psql postgres

    MacOS
    -----
    "/opt/homebrew/opt/postgresql@16/bin/psql" -f "/Users/dichatzi/Root/Repos/optimus_dr_settlement/database/dr_settlement.sql" "postgres://postgres:Dipbsia_01@localhost:5432/dr_settlement"
    "/Library/PostgreSQL/16/bin/psql/

    Windows
    -------
    "C:\Program Files\PostgreSQL\16\bin\psql.exe" -f "C:\Root\Repos\Colaeus\Databases\colaeus.sql" "postgres://postgres:Dipbsia_01@localhost:5432/colaeus"

    Ubuntu
    ------
    "/usr/bin/psql" -f "/home/dchatzigiannis/Root/Demand_Response/Database/dr_settlement.sql" "postgres://postgres:Dipbsia_01@localhost:5433/dr_settlement"
    """

    print(commands)


def postgres_database_sample():

    sample = r"""
    -- Create extension if not already installed
    -- CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

    -- [entsoe_data] schema
    CREATE SCHEMA IF NOT EXISTS settlement_data AUTHORIZATION postgres;
    CREATE SCHEMA IF NOT EXISTS settlement_results AUTHORIZATION postgres;


    -- [settlement_data] schema =============================================================================================================================
    -- [berbe_w1] table
    CREATE TABLE IF NOT EXISTS settlement_data.berbe
    (
        stl_uid BIGINT,
        stl_bsp TEXT,
        stl_ro TEXT,
        stl_entity_type TEXT,
        stl_dir TEXT,
        stl_rescom TEXT,
        stl_step INTEGER,
        stl_config TEXT,
        stl_resolution TEXT,
        stl_start_time TIMESTAMPTZ,
        stl_end_time TIMESTAMPTZ,
        stl_determinant_name TEXT,
        stl_determinant_value NUMERIC,
        stl_version INTEGER,
        stl_week TEXT,
        PRIMARY KEY (stl_uid, stl_bsp, stl_ro, stl_entity_type, stl_dir, stl_rescom, stl_step, stl_config, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_version, stl_week),
        UNIQUE (stl_uid, stl_bsp, stl_ro, stl_entity_type, stl_dir, stl_rescom, stl_step, stl_config, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_version, stl_week)	
    );
    ALTER TABLE IF EXISTS settlement_data.berbe OWNER to postgres;

    -- [imbal_w1] table
    CREATE TABLE IF NOT EXISTS settlement_data.imbal
    (
        stl_uid BIGINT,
        stl_brp TEXT,
        stl_cs TEXT,
        stl_ro TEXT,
        stl_bidding_zone TEXT,
        stl_et TEXT,
        stl_resolution TEXT,
        stl_start_time TIMESTAMPTZ,
        stl_end_time TIMESTAMPTZ,
        stl_determinant_name TEXT,
        stl_determinant_value NUMERIC,
        stl_version INTEGER,
        stl_week TEXT, 
        PRIMARY KEY (stl_uid, stl_brp, stl_cs, stl_ro, stl_bidding_zone, stl_et, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_version, stl_week),
        UNIQUE (stl_uid, stl_brp, stl_cs, stl_ro, stl_bidding_zone, stl_et, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_version, stl_week)	
    );
    ALTER TABLE IF EXISTS settlement_data.imbal OWNER to postgres;

    -- [bcrbc_w1] table
    CREATE TABLE IF NOT EXISTS settlement_data.bcrbc
    (
        stl_uid BIGINT,
        stl_bsp TEXT,
        stl_ro TEXT,
        stl_config TEXT,
        stl_step INTEGER,
        stl_resolution TEXT,
        stl_start_time TIMESTAMPTZ,
        stl_end_time TIMESTAMPTZ,
        stl_determinant_name TEXT,
        stl_determinant_value NUMERIC,
        stl_version INTEGER,
        stl_week TEXT,
        PRIMARY KEY (stl_uid, stl_bsp, stl_ro, stl_config, stl_step, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_version, stl_week),
        UNIQUE (stl_uid, stl_bsp, stl_ro, stl_config, stl_step, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_version, stl_week)	
    );
    ALTER TABLE IF EXISTS settlement_data.bcrbc OWNER to postgres;
    -- Create a unique index on ts_id and ts_version
    -- CREATE UNIQUE INDEX IF NOT EXISTS settlement_data_bcrbc_idx ON settlement_data.bcrbc (stl_uid, stl_bsp, stl_ro, stl_config, stl_step, stl_start_time, stl_end_time, stl_determinant_name);
    -- Create BRIN indexes
    -- CREATE INDEX IF NOT EXISTS settlement_data_bcrbc_brin_indexes ON settlement_data.bcrbc USING BRIN (stl_uid, stl_bsp, stl_ro, stl_config, stl_step, stl_start_time, stl_end_time, stl_determinant_name);
    -- Convert the table to a hypertable
    -- SELECT create_hypertable('settlement_data.bcrbc', 'stl_start_time');






    -- [logs] table
    CREATE TABLE IF NOT EXISTS settlement_data.logs
    (
        stl_category TEXT,
        stl_period TEXT,
        stl_date DATE,
        stl_file TEXT,
        stl_update_date TIMESTAMPTZ,
        PRIMARY KEY (stl_category, stl_period, stl_date),
        UNIQUE (stl_category, stl_period, stl_date)	
    );
    ALTER TABLE IF EXISTS settlement_data.logs OWNER to postgres;



    -- [portfolio_data] table
    CREATE TABLE IF NOT EXISTS settlement_data.portfolio_data
    (
        stl_portfolio TEXT, 
        stl_identifier TEXT, 
        stl_start_date DATE, 
        stl_end_date DATE, 
        stl_available_net_power NUMERIC,
        stl_indicative_share NUMERIC,
        PRIMARY KEY (stl_portfolio, stl_start_date, stl_end_date),
        UNIQUE (stl_portfolio, stl_start_date, stl_end_date)	
    );
    ALTER TABLE IF EXISTS settlement_data.portfolio_data OWNER to postgres;


    -- [settlement_parameters] table
    CREATE TABLE IF NOT EXISTS settlement_data.settlement_parameters
    (
        stl_portfolio TEXT, 
        stl_identifier TEXT, 
        stl_start_date DATE, 
        stl_end_date DATE, 
        stl_available_net_power NUMERIC,
        stl_indicative_share NUMERIC,
        PRIMARY KEY (stl_portfolio, stl_start_date, stl_end_date),
        UNIQUE (stl_portfolio, stl_start_date, stl_end_date)	
    );
    ALTER TABLE IF EXISTS settlement_data.portfolio_data OWNER to postgres;


    -- [portfolio_data] table
    CREATE TABLE IF NOT EXISTS settlement_data.settlement_files
    (
        stl_file_code TEXT,
        stl_message_identification TEXT,
        stl_message_version INTEGER,
        stl_status TEXT,
        stl_application_time_interval_start TIMESTAMPTZ,
        stl_application_time_interval_end TIMESTAMPTZ,
        stl_server_timestamp TIMESTAMPTZ,
        stl_type TEXT,
        stl_owner TEXT,
        stl_week TEXT,
        stl_processed_time TIMESTAMPTZ,
        PRIMARY KEY (stl_file_code, stl_message_identification, stl_message_version, stl_status, stl_application_time_interval_start, stl_application_time_interval_end, stl_server_timestamp, stl_type, stl_owner, stl_week),
        UNIQUE (stl_file_code, stl_message_identification, stl_message_version, stl_status, stl_application_time_interval_start, stl_application_time_interval_end, stl_server_timestamp, stl_type, stl_owner, stl_week)	
    );
    ALTER TABLE IF EXISTS settlement_data.settlement_files OWNER to postgres;



    -- [settlement_results] schema ==========================================================================================================================
    -- [berbe_w1] table
    CREATE TABLE IF NOT EXISTS settlement_results.energy_clearing
    (
        stl_uid BIGINT,
        stl_bsp TEXT,
        stl_ro TEXT,
        stl_entity_type TEXT,
        stl_dir TEXT,
        stl_rescom TEXT,
        stl_step INTEGER,
        stl_config TEXT,
        stl_resolution TEXT,
        stl_start_time TIMESTAMPTZ,
        stl_end_time TIMESTAMPTZ,
        stl_determinant_name TEXT,
        stl_determinant_value NUMERIC,
        stl_week TEXT,
        PRIMARY KEY (stl_uid, stl_bsp, stl_ro, stl_entity_type, stl_dir, stl_rescom, stl_step, stl_config, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_week),
        UNIQUE (stl_uid, stl_bsp, stl_ro, stl_entity_type, stl_dir, stl_rescom, stl_step, stl_config, stl_resolution, stl_start_time, stl_end_time, stl_determinant_name, stl_week)	
    );
    ALTER TABLE IF EXISTS settlement_data.berbe OWNER to postgres;



    -- stl_settlement_period, stl_mfrr_be_up_price_z, stl_mfrr_be_dn_price_z, stl_mq_all_cbse, stl_bl_cbse, stl_mfrr_abe_up_rtbm_cbse, stl_mfrr_abe_dn_rtbm_cbse, stl_imb_price, 
    -- stl_date, stl_year, stl_month, stl_balancing_energy_up_revenue, stl_balancing_energy_dn_revenue, stl_balancing_energy_revenue

    """

    print(sample)