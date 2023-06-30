import requests
from bs4 import BeautifulSoup as bs
import json
import re
import os

from constants import DIR_URL, DEPARTMENT_PATTERN, DEPARTMENT_URL

def get_departments():
    # Check if file exists
    if os.path.isfile('json/departments.json'):
        print('JSON file already exists. Skipping request.')
        return 0
    
    # Scrape departments from page
    page = requests.get(DIR_URL)
    
    if page.status_code != 200:
        print('Error: Could not access website.')
        return 1
    
    soup = bs(page.text, 'html.parser')
    departments = soup.find_all('a',{'href': re.compile(DEPARTMENT_PATTERN)})
    
    # Extract department names from links
    codes = dict()
    
    for department in departments:
        
        # Get department title and code
        title = department.text.strip()
        code = department['href'].split('/')[-2]
        
        codes[code] = title
        
    with open('json/departments.json', 'w') as output_file:
        json_object = json.dumps(codes, indent = 4)
        output_file.write(json_object)
        output_file.write('\n')
    
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
