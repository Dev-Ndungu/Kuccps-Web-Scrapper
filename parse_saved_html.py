"""
Parse saved HTML files from KUCCPS course pages
This script reads HTML files saved manually from the browser and extracts all course data
"""

import os
import json
import csv
from pathlib import Path
from bs4 import BeautifulSoup
import re

def extract_course_title(soup):
    """Extract course title from the page"""
    h3_tag = soup.find('h3')
    if h3_tag:
        return h3_tag.get_text(strip=True)
    return "Unknown Course"

def extract_table_section(soup, section_title):
    """Extract data from a table section (Entry Requirements or Subject Requirements)"""
    requirements = []
    
    # Find all h4 tags and look for the one matching our section
    for h4 in soup.find_all('h4'):
        if section_title.lower() in h4.get_text(strip=True).lower():
            # Find the next table after this h4
            table = h4.find_next('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        # Skip header rows
                        if any(header in cell_texts[0].lower() for header in ['cluster', 'subject', 'grade']):
                            continue
                        requirements.append(cell_texts)
            break
    
    return requirements

def extract_available_programmes(soup):
    """Extract available programmes table data"""
    programmes = []
    
    # Find the Available Programmes section
    for h4 in soup.find_all('h4'):
        if 'available programmes' in h4.get_text(strip=True).lower():
            # Find the next table
            table = h4.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 7:  # Ensure we have enough columns
                            # Extract institution and county
                            institution_cell = cells[0]
                            institution_text = institution_cell.get_text(strip=True)
                            
                            # Try to split institution and county
                            institution = institution_text
                            county = ""
                            
                            # Look for county in parentheses or after comma
                            county_match = re.search(r'\(([^)]+)\)$', institution_text)
                            if county_match:
                                county = county_match.group(1).strip()
                                institution = institution_text[:county_match.start()].strip()
                            elif ',' in institution_text:
                                parts = institution_text.rsplit(',', 1)
                                institution = parts[0].strip()
                                county = parts[1].strip()
                            
                            programme_data = {
                                'institution': institution,
                                'county': county,
                                'type': cells[1].get_text(strip=True),
                                'programme_code': cells[2].get_text(strip=True),
                                'programme_name': cells[3].get_text(strip=True),
                                'kcse_2025_cutoff': cells[4].get_text(strip=True),
                                'kcse_2024_cutoff': cells[5].get_text(strip=True),
                                'kcse_2023_cutoff': cells[6].get_text(strip=True),
                            }
                            
                            # Add cluster weight if it exists (8th column)
                            if len(cells) >= 8:
                                programme_data['cluster_weight'] = cells[7].get_text(strip=True)
                            else:
                                programme_data['cluster_weight'] = ''
                            
                            programmes.append(programme_data)
            break
    
    return programmes

def parse_html_file(file_path):
    """Parse a single HTML file and extract course data"""
    print(f"Parsing: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract course title
        course_title = extract_course_title(soup)
        print(f"  Course: {course_title}")
        
        # Extract entry requirements
        entry_requirements = extract_table_section(soup, "Entry Requirements")
        print(f"  Entry requirements: {len(entry_requirements)} items")
        
        # Extract subject requirements
        subject_requirements = extract_table_section(soup, "Subject Requirements")
        print(f"  Subject requirements: {len(subject_requirements)} items")
        
        # Extract available programmes
        programmes = extract_available_programmes(soup)
        print(f"  Available programmes: {len(programmes)} programmes")
        
        course_data = {
            'course_title': course_title,
            'entry_requirements': entry_requirements,
            'subject_requirements': subject_requirements,
            'available_programmes': programmes
        }
        
        return course_data
        
    except Exception as e:
        print(f"  ERROR parsing {file_path.name}: {e}")
        return None

def main():
    """Main function to parse all HTML files in the saved_pages directory"""
    
    # Create directories if they don't exist
    saved_pages_dir = Path('saved_pages')
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    if not saved_pages_dir.exists():
        print(f"Creating {saved_pages_dir} directory...")
        saved_pages_dir.mkdir(exist_ok=True)
        print(f"\nPlease save course pages as HTML files in the '{saved_pages_dir}' folder.")
        print("Instructions:")
        print("1. Open a course page in your browser")
        print("2. Right-click → 'Save As' → Save as 'Webpage, HTML Only'")
        print("3. Save to the 'saved_pages' folder with a descriptive name")
        print("4. Repeat for all courses you want to scrape")
        print("5. Run this script again\n")
        return
    
    # Find all HTML files
    html_files = list(saved_pages_dir.glob('*.html')) + list(saved_pages_dir.glob('*.htm'))
    
    if not html_files:
        print(f"No HTML files found in '{saved_pages_dir}' folder.")
        print("\nInstructions:")
        print("1. Open a course page in your browser")
        print("2. Right-click → 'Save As' → Save as 'Webpage, HTML Only'")
        print("3. Save to the 'saved_pages' folder")
        print("4. Run this script again\n")
        return
    
    print(f"Found {len(html_files)} HTML files to parse\n")
    
    # Parse all files
    all_courses = []
    for html_file in html_files:
        course_data = parse_html_file(html_file)
        if course_data:
            all_courses.append(course_data)
    
    if not all_courses:
        print("\nNo data extracted. Please check your HTML files.")
        return
    
    # Save to JSON
    json_file = data_dir / 'kuccps_courses.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(all_courses)} courses to {json_file}")
    
    # Save to CSV (flattened format)
    csv_file = data_dir / 'kuccps_courses.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Course Title',
            'Entry Requirements',
            'Subject Requirements',
            'Institution',
            'County',
            'Type',
            'Programme Code',
            'Programme Name',
            'KCSE 2025 Cutoff',
            'KCSE 2024 Cutoff',
            'KCSE 2023 Cutoff',
            'Cluster Weight'
        ])
        
        # Write data
        for course in all_courses:
            course_title = course['course_title']
            entry_req = '; '.join([' - '.join(req) for req in course['entry_requirements']])
            subject_req = '; '.join([' - '.join(req) for req in course['subject_requirements']])
            
            if course['available_programmes']:
                for prog in course['available_programmes']:
                    writer.writerow([
                        course_title,
                        entry_req,
                        subject_req,
                        prog['institution'],
                        prog['county'],
                        prog['type'],
                        prog['programme_code'],
                        prog['programme_name'],
                        prog['kcse_2025_cutoff'],
                        prog['kcse_2024_cutoff'],
                        prog['kcse_2023_cutoff'],
                        prog['cluster_weight']
                    ])
            else:
                # Write course without programmes
                writer.writerow([
                    course_title,
                    entry_req,
                    subject_req,
                    '', '', '', '', '', '', '', '', ''
                ])
    
    print(f"✓ Saved flattened data to {csv_file}")
    print(f"\n✓ Done! Processed {len(all_courses)} courses successfully.")

if __name__ == "__main__":
    main()
