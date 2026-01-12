-- Initialize the frog_identifier database
-- This script runs automatically when the MySQL container starts

-- Ensure we're using the right database
USE frog_identifier;

-- Grant all privileges to our user
GRANT ALL PRIVILEGES ON frog_identifier.* TO 'frog_user'@'%';
FLUSH PRIVILEGES;
