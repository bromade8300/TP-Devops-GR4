-- Create tables for the image detection application
USE image_detection;

CREATE TABLE IF NOT EXISTS detection_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    detections JSON NOT NULL,
    total_objects INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_filename (filename)
);
