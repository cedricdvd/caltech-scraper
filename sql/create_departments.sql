CREATE TABLE IF NOT EXISTS departments (
    abbr CHAR(3) NOT NULL,
    title VARCHAR(50) NOT NULL,
    course_count INT NOT NULL,
    course_prereq_count INT NOT NULL,
    id INT AUTO_INCREMENT PRIMARY KEY
);
