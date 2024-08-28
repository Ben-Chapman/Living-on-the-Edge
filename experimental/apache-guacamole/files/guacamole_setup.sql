-- Check if the database already exists
CREATE DATABASE IF NOT EXISTS guacamole_db;

-- Check if the user already exists
CREATE USER IF NOT EXISTS 'guacamole_user'@'%' IDENTIFIED BY 'guacamole';

-- Grant read and write access to the user on the database
GRANT SELECT, INSERT, UPDATE, DELETE ON guacamole_db.* TO 'guacamole_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
