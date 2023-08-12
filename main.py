import os
from connector import connect_database

def main():
    # Get connection to database, cursor
    database, cursor = connect_database()
    if database is None or cursor is None:
        return 1
    
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
