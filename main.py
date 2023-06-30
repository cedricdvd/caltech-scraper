import os
import json

from scraper import get_courses, get_departments

def main():
    # Create json directory
    if os.path.isdir('json'):
        print('JSON directory already exists. Skipping creation.')
    else:
        os.mkdir('json')
        print('JSON directory created.')
    
    # Store departments in JSON file
    get_departments()
    
    # Extract data from JSON file
    with open('json/departments.json', 'r') as file:
        json_data = json.load(file)
    
    # Create html directory
    if os.path.isdir('html'):
        print('HTML directory already exists. Skipping creation.')
    else:
        os.mkdir('html')
        print('HTML directory created.')
    
    # Store courses in HTML files
    for department in json_data:
        get_courses(department)
        
        

if __name__ == '__main__':
    main()