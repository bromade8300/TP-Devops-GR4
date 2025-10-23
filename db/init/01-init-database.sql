-- Initialize the image_detection database
CREATE DATABASE IF NOT EXISTS image_detection;
USE image_detection;

-- Create user for the application
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON image_detection.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
