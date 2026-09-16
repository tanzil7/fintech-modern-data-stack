/*
    Fintech Modern Data Stack Platform
    Initial Snowflake infrastructure setup
*/

USE ROLE ACCOUNTADMIN;

-- Create a dedicated project role
CREATE ROLE IF NOT EXISTS FINTECH_TRANSFORM_ROLE
    COMMENT = 'Owns and transforms objects for the fintech analytics platform';

-- Grant the role to the current user
SET project_user = CURRENT_USER();

GRANT ROLE FINTECH_TRANSFORM_ROLE
    TO USER IDENTIFIER($project_user);

-- Place the project role beneath SYSADMIN in the role hierarchy
GRANT ROLE FINTECH_TRANSFORM_ROLE
    TO ROLE SYSADMIN;

-- Create a cost-controlled virtual warehouse
CREATE WAREHOUSE IF NOT EXISTS FINTECH_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Compute warehouse for the fintech analytics platform';

-- Create the project database
CREATE DATABASE IF NOT EXISTS FINTECH_DB
    COMMENT = 'Database for the fintech modern data stack portfolio project';

-- Transfer project object ownership away from ACCOUNTADMIN
GRANT OWNERSHIP ON WAREHOUSE FINTECH_WH
    TO ROLE FINTECH_TRANSFORM_ROLE
    COPY CURRENT GRANTS;

GRANT OWNERSHIP ON DATABASE FINTECH_DB
    TO ROLE FINTECH_TRANSFORM_ROLE
    COPY CURRENT GRANTS;

-- Use the project role for normal development
USE ROLE FINTECH_TRANSFORM_ROLE;
USE WAREHOUSE FINTECH_WH;
USE DATABASE FINTECH_DB;

-- Create the platform layers
CREATE SCHEMA IF NOT EXISTS RAW
    COMMENT = 'Unmodified data loaded from source systems';

CREATE SCHEMA IF NOT EXISTS STAGING
    COMMENT = 'Cleaned and standardized source data';

CREATE SCHEMA IF NOT EXISTS INTERMEDIATE
    COMMENT = 'Reusable transformations and business logic';

CREATE SCHEMA IF NOT EXISTS MARTS
    COMMENT = 'Analytics-ready facts, dimensions, and business marts';

CREATE SCHEMA IF NOT EXISTS MONITORING
    COMMENT = 'Pipeline audit records and data quality results';

-- Confirm the active development context
SELECT
    CURRENT_ROLE() AS active_role,
    CURRENT_WAREHOUSE() AS active_warehouse,
    CURRENT_DATABASE() AS active_database;

SHOW SCHEMAS IN DATABASE FINTECH_DB;