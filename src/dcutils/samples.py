


def postgres_utilities():

    commands = r"""

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ''' INSTALLATION
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    cd /path/to/dcutils
    python -m pip install -e .



    

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ''' COMMANDS
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    psql postgres
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'your_password';
    /opt/homebrew/opt/postgresql@16/bin/psql postgres

    MacOS
    -----
    "/opt/homebrew/opt/postgresql@16/bin/psql" -f "/Users/dichatzi/Root/Repos/optimus_dr_settlement/database/dr_settlement.sql" "postgres://postgres:PASSWORD@localhost:5432/dr_settlement"
    "/Library/PostgreSQL/16/bin/psql/

    Windows
    -------
    "C:\Program Files\PostgreSQL\16\bin\psql.exe" -f "C:\Root\Repos\Colaeus\Databases\colaeus.sql" "postgres://postgres:PASSWORD@localhost:5432/colaeus"

    Ubuntu
    ------
    "/usr/bin/psql" -f "/home/dchatzigiannis/Root/Demand_Response/Database/dr_settlement.sql" "postgres://postgres:PASSWORD@localhost:5433/dr_settlement"

    



    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ''' DATABASE
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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

    print(commands)