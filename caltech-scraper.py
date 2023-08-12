import argparse
from connector import connect_database

def perform_actions(args):
    # Get connection to database, cursor
    database, cursor = connect_database()
    if database is None or cursor is None:
        return 1
    
    if (args.list):
        cursor.execute('SELECT abbr FROM departments')
        department_info = cursor.fetchall()
        print(department_info)
    
    if (args.department):
        cursor.execute('SELECT id FROM departments WHERE abbr = %s', (args.department,))
        department_id = cursor.fetchone()
        
        if department_id is None:
            print('Invalid department.')
            return 1
        
        cursor.execute('SELECT courses.label, courses.title FROM courses INNER JOIN course_department ON courses.id = course_department.course_id WHERE course_department.department_id = %s', (department_id[0],))
        courses = cursor.fetchall()
        
        if courses is None or len(courses) == 0:
            print('No courses found.')
            return 1
        
        for course in courses:
            print(f'{course[0]} -- {course[1]}')

    if (args.search):
        cursor.execute('SELECT label, title, course_desc FROM courses WHERE label LIKE %s', (f'%{args.search}%',))
        courses = cursor.fetchall()
        
        if courses is None or len(courses) == 0:
            print('No courses found.')
            return 1
        
        for course in courses:
            print(f'{course[0]} -- {course[1]}.\n{course[2]}')
    
    if (args.course):
        cursor.execute('SELECT * FROM courses WHERE label = %s', (args.course,))
        course = cursor.fetchone()
        
        if course is None:
            print('Invalid course.')
            return 1
        
        print(f'{course[0]} -- {course[1]}.\n{course[2]}\nPrerequisites: {course[3]}.')
        
        cursor.execute('SELECT label FROM courses WHERE id IN (SELECT prereq_id FROM course_prerequisites WHERE course_id = %s)', (course[4],))
        prerequisites = cursor.fetchall()
        
        if prerequisites is not None and len(prerequisites) != 0:
            print('Prerequisite Courses:')
            for prereq in prerequisites:
                print(f'- {prereq[0]}')
                
        if not args.needed:
            return 0
        
        cursor.execute('SELECT label FROM courses WHERE id IN (SELECT course_id FROM course_prerequisites WHERE prereq_id = %s)', (course[4],))
        successors = cursor.fetchall()
        
        if successors is not None and len(successors) != 0:
            print('Successor Courses:')
            for successor in successors:
                print(f'- {successor[0]}')
                
    # Close connections
    cursor.close()
    database.close()
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog='caltech-scraper.py',
        description='Caltech Course Catalogue',
        epilog=''
    )
    
    parser.add_argument('-l', '--list', action='store_true', help='Lists all departments.')
    parser.add_argument('-d', '--department', action='store', type=str, help='Displays all courses within the department.')
    parser.add_argument('-s', '--search', action='store', type=str, help='Searches for the keyword within course codes.')
    parser.add_argument('-c', '--course', action='store', type=str, help='Displays course information.')
    parser.add_argument('-n', '--needed', action='store_true', help='Displays all successor courses.')

    args = parser.parse_args()
    return perform_actions(args)


if __name__ == '__main__':
    main()
