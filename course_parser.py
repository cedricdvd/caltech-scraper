from bs4 import BeautifulSoup as bs
import json
import re
import os

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
    if os.path.isfile(f'json/courses/{department}.json'):
        print('JSON file already exists. Skipping request.')
        return 0
    
    with open(f'html/{department}.html') as file:
        courses = bs(file.read(), 'html.parser')
        
    courses_dict = dict()
    
    for course in courses.find_all('div', {'class':'course-description2'}):
        data = bs(str(course), 'html.parser')
        course_info = dict()
        
        # Extract course label
        label = data.find('div',{'class':'course-description2__label'})
        if label is not None:
            course_info['label'] = label.text.strip()
        
        # Extract course title
        title = data.find('h3', {'class':'course-description2__title'})
        if title is not None:
            course_info['title'] = title.text.strip()
        
        # Extract course prerequisites
        prerequisites = data.find('div',{'class':'course-description2__prerequisites'})
        if prerequisites is not None:
            prereq_text = prerequisites.text.strip()
            course_info['prerequisites'] = re.sub(r'Prerequisites?', '', prereq_text).removesuffix('.')
        
        # Extract course description
        description = data.find('div',{'class':'course-description2__description'})
        if description is not None:
            desc_text = description.text.strip()
            prereq_text = re.search(r'Prerequisites?: (.*\.)', desc_text)
            
            # Handle case where prerequisite is in the description (ch-80)
            if prereq_text is not None and prerequisites is None:
                prereq_text = prereq_text.group()
                desc_text = re.sub(prereq_text,'', desc_text)
                course_info['prerequisites'] = re.sub(r'Prerequisites?: ', '', prereq_text).removesuffix('.')
            
            course_info['description'] = desc_text
        
        # Extract course id and store in dictionary
        id = data.find('div')['id'] # type: ignore
        courses_dict[id] = course_info
        
    with open(f'json/courses/{department}.json', 'w') as output_file:
        json_object = json.dumps(courses_dict, indent=4)
        output_file.write(json_object + '\n')
        
    return 0

def parse_prerequisites(current_department, departments):
    if os.path.isfile(f'json/prerequisites/{current_department}.json'):
        print('JSON file already exists. Skipping request.')
        return 0
    
    # Load course information
    with open(f'json/courses/{current_department}.json', 'r') as file:
        courses = json.load(file)
    
    prereqs_dict = dict()
    
    # Parse course prerequisites
    for course in courses:
        prereq_text = courses[course].get('prerequisites')
        
        # Check if prerequisites exist
        if prereq_text is None:
            continue
        
        course_prereqs = []
        prereq_text = re.sub(r'Math', 'Ma', prereq_text)
        prereqs = re.findall(PREREQ_PATTERN, prereq_text)
        
        for index, group in enumerate(prereqs):
            if group[0] not in departments:
                group = list(group)
                group[0] = prereqs[index - 1][0]
                group = tuple(group)
                
            prereq_departments = [dep for dep in group[0:4] if dep != '']
            entry = '/'.join(prereq_departments) + ''.join(group[4:])
            course_prereqs.append(entry)
            
            if len(course_prereqs) != 0:
                prereqs_dict[course] = course_prereqs
                
    with open(f'json/prerequisites/{current_department}.json', 'w') as output_file:
        json_object = json.dumps(prereqs_dict, indent=4)
        output_file.write(json_object + '\n')
    
    return
