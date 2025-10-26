#!/usr/bin/env python3
"""
SIMPLE MANUAL SCRAPER
You browse manually, this script saves the data automatically.

HOW IT WORKS:
1. You start Chrome with: chrome.exe --remote-debugging-port=9222
2. You manually browse to each course page
3. This script automatically detects the page and saves the data
4. You just click through the courses, script does the rest!
"""
import time
import json
import os
import pandas as pd
from playwright.sync_api import sync_playwright

OUT_JSON = "data/kuccps_courses.json"
OUT_CSV = "data/kuccps_courses.csv"

# Track what we've already scraped
scraped_urls = set()

if not os.path.exists("data"):
    os.makedirs("data")

if os.path.exists(OUT_JSON):
    try:
        with open(OUT_JSON, 'r', encoding='utf-8-sig') as f:
            content = f.read().strip()
            if content:
                existing = json.loads(content)
                scraped_urls = {item['source_url'] for item in existing if 'source_url' in item}
    except:
        # If file is corrupted, start fresh
        scraped_urls = set()

def append_json(obj):
    try:
        if os.path.exists(OUT_JSON):
            with open(OUT_JSON, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                data = json.loads(content) if content else []
        else:
            data = []
    except:
        data = []
    
    data.append(obj)
    
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def write_csv_row(row):
    df = pd.DataFrame([row])
    if not os.path.exists(OUT_CSV):
        df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    else:
        df.to_csv(OUT_CSV, mode='a', header=False, index=False, encoding="utf-8")

def extract_course_data(page):
    """Extract data from current course page."""
    try:
        # Get title
        title_elem = page.query_selector('h3.text-center, h4')
        title = title_elem.inner_text().strip() if title_elem else ""
        
        # Get cluster info
        cluster_btn = page.query_selector('.btn-danger')
        cluster_info = cluster_btn.inner_text().strip() if cluster_btn else ""
        
        # Extract cluster number
        cluster_num = 0
        if 'cluster' in cluster_info.lower():
            import re
            match = re.search(r'cluster\s*(\d+)', cluster_info, re.I)
            if match:
                cluster_num = int(match.group(1))
        
        # Entry requirements
        entry_reqs = []
        rows = page.query_selector_all('table tbody tr')
        for row in rows:
            cells = row.query_selector_all('th, td')
            if len(cells) >= 2:
                header = cells[0].inner_text().strip()
                if 'cluster subject' in header.lower():
                    entry_reqs.append({
                        "requirement": header,
                        "value": cells[1].inner_text().strip(),
                        "grade": ""
                    })
        
        # Subject requirements
        subject_reqs = []
        for row in rows:
            cells = row.query_selector_all('th, td')
            if len(cells) >= 2:
                header = cells[0].inner_text().strip()
                if 'subject' in header.lower() and 'cluster' not in header.lower() and 'NOTE' not in row.inner_text():
                    subject_reqs.append({
                        "requirement": header,
                        "value": cells[1].inner_text().strip(),
                        "grade": cells[2].inner_text().strip() if len(cells) > 2 else ""
                    })
        
        # Available programmes
        programmes = []
        prog_rows = page.query_selector_all('.table-responsive table tbody tr')
        for row in prog_rows:
            cols = row.query_selector_all('td, th')
            if len(cols) >= 8:
                inst_text = cols[0].inner_text().strip()
                lines = [l.strip() for l in inst_text.split('\n') if l.strip()]
                
                programmes.append({
                    "institution": lines[0] if lines else "",
                    "county": lines[1] if len(lines) > 1 else "",
                    "institution_type": cols[1].inner_text().strip(),
                    "programme_code": cols[2].inner_text().strip(),
                    "programme_name": cols[3].inner_text().strip(),
                    "kcse2025_cutoff": cols[4].inner_text().strip(),
                    "kcse2024_cutoff": cols[5].inner_text().strip(),
                    "kcse2023_cutoff": cols[6].inner_text().strip(),
                    "cluster_weight": cols[7].inner_text().strip()
                })
        
        return {
            "cluster": cluster_num,
            "course_title": title,
            "cluster_info": cluster_info,
            "entry_requirements": entry_reqs,
            "subject_requirements": subject_reqs,
            "available_programmes": programmes,
            "source_url": page.url
        }
    except Exception as e:
        print(f"Error extracting: {e}")
        return None

def main():
    print("="*60)
    print("KUCCPS MANUAL SCRAPER")
    print("="*60)
    print("\nConnecting to your Chrome browser...")
    print("Make sure Chrome is running with:")
    print("  chrome.exe --remote-debugging-port=9222\n")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            contexts = browser.contexts
            
            if not contexts:
                print("ERROR: No Chrome context found!")
                print("Please start Chrome with: chrome.exe --remote-debugging-port=9222")
                return
            
            context = contexts[0]
            pages = context.pages
            
            if not pages:
                print("ERROR: No pages found!")
                return
            
            page = pages[0]
            
            print("✓ Connected!")
            print(f"✓ Watching: {page.url}\n")
            print("="*60)
            print("HOW TO USE:")
            print("="*60)
            print("1. In your Chrome browser, navigate to any course page")
            print("2. This script will automatically detect and save the data")
            print("3. Click 'Back' and go to the next course")
            print("4. Repeat until you've gone through all courses")
            print("5. Press Ctrl+C when done\n")
            print(f"Already scraped: {len(scraped_urls)} courses")
            print("="*60)
            print("\nMonitoring... (Press Ctrl+C to stop)\n")
            
            last_url = ""
            
            while True:
                try:
                    current_url = page.url
                    
                    # Check if it's a course detail page we haven't scraped
                    if '/programmes/detail/' in current_url and current_url != last_url:
                        if current_url not in scraped_urls:
                            print(f"\n📄 New course detected!")
                            print(f"   URL: {current_url}")
                            
                            # Extract data
                            data = extract_course_data(page)
                            
                            if data and data.get('course_title'):
                                # Save to JSON
                                append_json(data)
                                scraped_urls.add(current_url)
                                
                                # Save to CSV
                                if data['available_programmes']:
                                    for prog in data['available_programmes']:
                                        csv_row = {
                                            "cluster": data['cluster'],
                                            "course_title": data['course_title'],
                                            "entry_requirements": " | ".join([f"{r['requirement']}: {r['value']}" for r in data['entry_requirements']]),
                                            "subject_requirements": " | ".join([f"{r['requirement']}: {r['value']} {r['grade']}" for r in data['subject_requirements']]),
                                            "institution": prog['institution'],
                                            "county": prog['county'],
                                            "institution_type": prog['institution_type'],
                                            "programme_code": prog['programme_code'],
                                            "programme_name": prog['programme_name'],
                                            "kcse2025_cutoff": prog['kcse2025_cutoff'],
                                            "kcse2024_cutoff": prog['kcse2024_cutoff'],
                                            "kcse2023_cutoff": prog['kcse2023_cutoff'],
                                            "cluster_weight": prog['cluster_weight'],
                                            "source_url": current_url
                                        }
                                        write_csv_row(csv_row)
                                
                                print(f"   ✓ Saved: {data['course_title']}")
                                print(f"   ✓ Programmes: {len(data['available_programmes'])}")
                                print(f"   Total scraped: {len(scraped_urls)}")
                            else:
                                print(f"   ⚠ Could not extract data from this page")
                        else:
                            print(f"\n⏭  Already scraped this course, skipping...")
                        
                        last_url = current_url
                    
                    time.sleep(0.5)  # Check every half second
                    
                except KeyboardInterrupt:
                    print("\n\n" + "="*60)
                    print("SCRAPING STOPPED")
                    print("="*60)
                    print(f"\nTotal courses scraped: {len(scraped_urls)}")
                    print(f"Data saved to:")
                    print(f"  • {OUT_JSON}")
                    print(f"  • {OUT_CSV}")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)
                    
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nMake sure:")
        print("1. Chrome is running")
        print("2. Started with: chrome.exe --remote-debugging-port=9222")
        print("3. You're logged into students.kuccps.net")

if __name__ == "__main__":
    main()
