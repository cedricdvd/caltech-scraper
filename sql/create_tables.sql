CREATE TABLE IF NOT EXISTS departments (
    abbr CHAR(3) NOT NULL,
    title VARCHAR(50) NOT NULL,
    course_count INT NOT NULL,
    course_prereq_count INT NOT NULL,
    id INT AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS courses (
    -- abbr VARCHAR(20), (not needed)
    course_code VARCHAR(30) NOT NULL,
    title VARCHAR(120) NOT NULL,
    course_desc VARCHAR(1500),
    prereq VARCHAR(190),
    id INT AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS course_prereqs (
    course_id INT NOT NULL,
    prereq_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (prereq_id) REFERENCES courses(id)
);
