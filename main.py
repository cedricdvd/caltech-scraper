import os

from scraper import get_courses, get_departments
from course_parser import parse_courses, parse_prerequisites
from connector import connect_database

def main():
    get_departments()
    
    if os.path.isdir('html'):
        print('HTML directory already exists. Skipping creation.')
    else:
        os.mkdir('html')
        print('HTML directory created.')
        
    database, cursor = connect_database()
    if database is None or cursor is None:
        return 1
    
    cursor.execute('SELECT abbr FROM departments')
    departments = [department[0] for department in cursor.fetchall()]
    
    with open('sql/create_courses.sql', 'r') as file:
        create_courses_sql = file.read()
        cursor.execute(create_courses_sql)
        
    with open('sql/create_course_department.sql', 'r') as file:
        create_course_department_sql = file.read()
        cursor.execute(create_course_department_sql)
        
    for department in departments:
        print(f'Parsing {department}\'s courses...')
        get_courses(department)
        parse_courses(department)
    
    with open('sql/create_prerequisites.sql', 'r') as file:
        create_prerequisites_sql = file.read()
        cursor.execute(create_prerequisites_sql)
        
    for department in departments:
        print(f'Parsing {department}\'s prerequisites...')
        parse_prerequisites(department, departments)
    

if __name__ == '__main__':
    main()
