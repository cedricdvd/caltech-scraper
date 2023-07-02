import os

from scraper import get_courses, get_departments
from course_parser import parse_courses, parse_prerequisites
from connector import connect_database

def main():
    # Store departments into database
    get_departments()
    
    # Create html if does not exist
    if os.path.isdir('html'):
        print('HTML directory already exists. Skipping creation.')
    else:
        os.mkdir('html')
        print('HTML directory created.')
    
    # Get connection to database, cursor
    database, cursor = connect_database()
    if database is None or cursor is None:
        return 1
    
    # Get departments
    cursor.execute('SELECT abbr FROM departments')
    departments = [department[0] for department in cursor.fetchall()]
    
    # Create course tables
    with open('sql/create_courses.sql', 'r') as file:
        create_courses_sql = file.read()
        cursor.execute(create_courses_sql)
        
    with open('sql/create_course_department.sql', 'r') as file:
        create_course_department_sql = file.read()
        cursor.execute(create_course_department_sql)
    
    # Scrape and process course pages
    for department in departments:
        print(f'Parsing {department}\'s courses...')
        get_courses(department)
        parse_courses(department)
    
    # Process course prerequisites
    with open('sql/create_prerequisites.sql', 'r') as file:
        create_prerequisites_sql = file.read()
        cursor.execute(create_prerequisites_sql)
        
    for department in departments:
        print(f'Parsing {department}\'s prerequisites...')
        parse_prerequisites(department, departments)
    
    # Clear screen and prompt user
    os.system('clear')
    user_input = input('Enter a course or \'exit\': ')
    while user_input != 'exit':
        # Extract course
        cursor.execute('SELECT * FROM courses WHERE label = %s', (user_input,))
        course_info = cursor.fetchone()
        
        if course_info is None:
            user_input = input('Invalid Course.\n\nCourse or \'exit\': ')
            continue
        
        label = course_info[0]
        title = course_info[1]
        description = course_info[2]
        prerequisites_text = course_info[3]
        id = course_info[4]
        
        print(f'{label} -- {title}.\n{description}\nPrerequisites: {prerequisites_text}.')
        
        # Extract course prerequisites
        cursor.execute('SELECT prereq_id FROM course_prerequisites WHERE course_id = %s', (id,))
        prerequisites = cursor.fetchall()
        
        if prerequisites is None or len(prerequisites) == 0:
            user_input = input('\nCourse or \'exit\': ')
        
        print('\nPrerequisite Courses:')
        for prereq in prerequisites:
            cursor.execute('SELECT label FROM courses WHERE id = %s', (prereq[0],))
            prereq_course = cursor.fetchone()
            
            if prereq_course is not None:
                print(f'- {prereq_course[0]}')
        
        # Prompt user
        user_input = input('\nCourse or \'exit\': ')
    
    # Close connections
    cursor.close()
    database.close()

if __name__ == '__main__':
    main()
