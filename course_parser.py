from bs4 import BeautifulSoup as bs
import re

from connector import connect_database
from constants import PREREQ_PATTERN

# Example Course:
# <div class="course-description2 " id={course_id}>
#   <div class="course-description2__label">
#     {course_description}
#   </div>
#   <h3 class="course-description2__title">
#     {course_title}
#   </h3>
#   <div class="course-description2__units-and-terms">
#     <span class="course-description2__units-and-terms__item">9 units (3-0-6)</span>
#       &nbsp; |&nbsp;
#     <span class="course-description2__units-and-terms__item">first, second, third terms</span>
#   </div>
#   <div class="course-description2__prerequisites">
#     Prerequisites: {course_prerequisites}.
#   </div>
#   <div class="course-description2__description course-description2__general-text">
#     <p>
#       {course_description}.
#     </p>
#   </div>
#
#     <div class="course-description2__instructors course-description2__general-text">
#       <span class="course-description2__instructors__label font-weight-bold">
#         Instructors:
#       </span>
#       {course_instructors}.
#     </div>
# </div>

def parse_courses(department):
    # Connect to database
    database, cursor = connect_database()
    if database is None or cursor is None:
        return 1
    
    # Check if courses already processed
    cursor.execute('SELECT course_count FROM departments WHERE abbr = %s', (department,))
    course_count = cursor.fetchone()
    if course_count is not None and course_count[0] > 0:
        print('Courses already exist. Skipping request.')
        return 0
    
    # Get department id
    cursor.execute('SELECT id FROM departments WHERE abbr = %s', (department,))
    department_id = cursor.fetchone()
    
    if department_id is None:
        return 1
    
    department_id = department_id[0]
    
    # Prepare html
    with open(f'html/{department}.html') as file:
        courses = bs(file.read(), 'html.parser')
    
    # Parse courses
    for course in courses.find_all('div', {'class':'course-description2'}):
        # Increment counter
        cursor.execute('UPDATE departments SET course_count = course_count + 1 WHERE abbr = %s', (department,))
        data = bs(str(course), 'html.parser')
        
        # Extract course label and title
        label = data.find('div',{'class':'course-description2__label'})
        title = data.find('h3', {'class':'course-description2__title'})
        
        if label is None or title is None:
            continue
        
        label = label.text.strip()
        title = title.text.strip()
        
        # Skip if course already processed
        cursor.execute('SELECT id FROM courses WHERE label = %s', (label,))
        course_id = cursor.fetchone()
        if course_id is not None:
            cursor.execute('INSERT course_department (department_id, course_id) VALUES (%s, %s)', (department_id, course_id[0]))
            continue
        
        # Insert course to database
        cursor.execute('INSERT INTO courses (label, title) VALUES (%s, %s)', (label, title))
        
        # Extract course prerequisites
        prerequisites = data.find('div',{'class':'course-description2__prerequisites'})
        if prerequisites is not None:
            prereq_text = prerequisites.text.strip()
            prereq_text = re.sub(r'Prerequisites?: ', '', prereq_text).removesuffix('.')
            cursor.execute('UPDATE courses SET prereqs = %s WHERE label = %s', (prereq_text, label))
        
        # Extract course description
        description = data.find('div',{'class':'course-description2__description'})
        if description is not None:
            desc_text = description.text.strip()
            prereq_text = re.search(r'Prerequisites?: (.*\.)', desc_text)
            
            # Handle case where prerequisite is in the description (ch-80)
            if prereq_text is not None and prerequisites is None:
                prereq_text = prereq_text.group()
                desc_text = re.sub(prereq_text,'', desc_text)
                prereq_text = re.sub(r'Prerequisites?: ', '', prereq_text).removesuffix('.')
                cursor.execute('UPDATE courses SET prereqs = %s WHERE label = %s', (prereq_text, label))
            
            cursor.execute('UPDATE courses SET course_desc = %s WHERE label = %s', (desc_text, label))
        
        # Connect course with department
        cursor.execute('INSERT course_department (department_id, course_id) VALUES (%s, LAST_INSERT_ID())', (department_id,))
    
    database.commit()
    cursor.close()
    database.close()
    return 0

def parse_prerequisites(current_department, departments):
    # Connect to database
    database, cursor = connect_database()
    if database is None or cursor is None:
        return 1
    
    cursor.execute('SELECT id, course_prereq_count FROM departments WHERE abbr = %s', (current_department,))
    department_id, course_prereq_count = cursor.fetchone()
    
    if department_id is None or course_prereq_count is None:
        return 1
    
    if course_prereq_count > 0:
        print('Prerequisites already inserted. Skipping request.')
        return 0
    
    # Get department's courses
    cursor.execute('SELECT id, label, prereqs FROM courses JOIN course_department ON courses.id = course_department.course_id WHERE course_department.department_id = %s', (department_id,))
    courses = cursor.fetchall()
    
    # Parse course prerequisites
    for course_data in courses:
        cursor.execute('UPDATE departments SET course_prereq_count = course_prereq_count + 1 WHERE abbr = %s', (current_department,))
        
        # Separate data
        course_id = course_data[0]
        course_label = course_data[1]
        prereq_text = course_data[2]
        
        # Check if course already processed
        cursor.execute('SELECT course_id FROM course_prerequisites WHERE course_id = %s', (course_id,))
        if cursor.fetchone() is not None:
            continue
        
        # Check if prerequisites exist
        if prereq_text is None:
            continue
        
        # Clean up math prereqs
        prereq_text = re.sub(r'Math', 'Ma', prereq_text)
        
        # Extract prerequisite classes
        prereqs = re.findall(PREREQ_PATTERN, prereq_text)
        
        # Clean up prerequisites
        for index, group in enumerate(prereqs):
            if group[0] not in departments:
                group = list(group)
                group[0] = prereqs[index - 1][0]
                group = tuple(group)
                
            # Combine if multiple departments
            prereq_departments = [dep for dep in group[0:4] if dep != '']
            entry = '/'.join(prereq_departments) + ''.join(group[4:])
            
            # Get prerequisite course id
            cursor.execute('SELECT id FROM courses WHERE label = %s', (entry,))
            prereq_id = cursor.fetchone()
            
            if prereq_id is None:
                continue
            
            # Insert prerequisite
            cursor.execute('INSERT INTO course_prerequisites (course_id, prereq_id) VALUES (%s, %s)', (course_id, prereq_id[0]))
    
    database.commit()
    cursor.close()
    database.close()
    
    return 0
