from bs4 import BeautifulSoup as bs
import requests
import re
import os

from connector import connect_database
from constants import DIR_URL, DEPARTMENT_PATTERN, DEPARTMENT_URL

def get_departments():
    # Get database and cursor connection
    database, cursor = connect_database()
    if database is None or cursor is None:
        print('Connection failed.')
        return 1
    
    # Check if table exists
    cursor.execute('SHOW TABLES')
    if ('departments',) in cursor.fetchall():
        cursor.execute('SELECT COUNT(*) FROM departments')
        row_count = cursor.fetchone()
        if row_count is not None and row_count[0] == 46:
            print('Table already exists. Skipping request.')
            return 0
    
    # Create table if not exists
    with open('sql/create_departments.sql', 'r') as file:
        create_department_sql = file.read()
    cursor.execute(create_department_sql)
    
    # Prepare html page
    page = requests.get(DIR_URL)
    
    if page.status_code != 200:
        print('Error: Could not access website.')
        return 1
    
    soup = bs(page.text, 'html.parser')
    departments = soup.find_all('a',{'href': re.compile(DEPARTMENT_PATTERN)})
    
    # Store departments into database
    for department in departments:
        title = department.text.strip()
        code = department['href'].split('/')[-2]
        cursor.execute('INSERT INTO departments (abbr, title, course_count, course_prereq_count) VALUES (%s, %s, 0, 0)', (code, title))
    
    # Commit changes and close connections
    database.commit()
    cursor.close()
    database.close()
    
    return 0


def get_courses(department):
    
    # Check if file exists
    if os.path.isfile(f'html/{department}.html'):
        print('HTML file already exists. Skipping request.')
        return 1
    
    # Check if website accessible
    page = requests.get(f'{DEPARTMENT_URL}{department}/')
    if page.status_code != 200:
        print('Error: Could not access website.')
        return 1
    
    # Store website to html file
    source = bs(page.text, 'html.parser')
    classes = source.find_all('div', {'class': 'course-description2'})
    with open(f'html/{department}.html', 'w') as f:
        for c in classes:
            f.write(str(c))
        f.write('\n')
    return 0
