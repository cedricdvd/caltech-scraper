CREATE TABLE IF NOT EXISTS course_prerequisites (
    course_id INT NOT NULL,
    prereq_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (prereq_id) REFERENCES courses(id)
);
