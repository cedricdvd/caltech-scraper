CREATE TABLE IF NOT EXISTS course_department (
    department_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
