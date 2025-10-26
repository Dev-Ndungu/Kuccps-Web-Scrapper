#!/usr/bin/env python3
"""
Scrape KUCCPS by launching Playwright with your Chrome user data directory.
This reuses your existing cookies/session without needing separate auth.
"""
import os
import json
import time
import sys
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright

# Config
OUT_JSON = "data/kuccps_courses.json"
OUT_CSV = "data/kuccps_courses.csv"

CLUSTER_SEARCH_URL = "https://students.kuccps.net/programmes/search/?group=cluster_{}"
CLUSTER_START = 1
CLUSTER_END = 1

DELAY_MIN = 0.5
DELAY_MAX = 1.2

# Create output dir
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(OUT_JSON):
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

def append_json(obj):
    with open(OUT_JSON, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(obj)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

def write_csv_row(row):
    df = pd.DataFrame([row])
    if not os.path.exists(OUT_CSV):
        df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    else:
        df.to_csv(OUT_CSV, mode='a', header=False, index=False, encoding="utf-8")

def safe_sleep():
    t = DELAY_MIN + (DELAY_MAX - DELAY_MIN) * 0.5
    time.sleep(t)

def extract_table_section(page, header_text):
    """Extract table rows from section containing header_text."""
    try:
        selector = f"section:has-text(\"{header_text}\") table tbody tr"
        page.wait_for_selector(selector, timeout=2000)
        rows = page.query_selector_all(selector)
        out = []
        for r in rows:
            out.append(r.inner_text().strip())
        return out
    except:
        return []

def extract_available_programmes(page):
    """Extract AVAILABLE PROGRAMMES table data."""
    try:
        selector = 'section:has-text("AVAILABLE PROGRAMMES") table tbody tr'
        page.wait_for_selector(selector, timeout=2000)
        rows = page.query_selector_all(selector)
        out = []
        for r in rows:
            cols = r.query_selector_all('td')
            texts = [c.inner_text().strip() for c in cols]
            # Pad to 8 columns
            while len(texts) < 8:
                texts.append('')
            out.append({
                "institution": texts[0],
                "institution_type": texts[1],
                "programme_code": texts[2],
                "programme_name": texts[3],
                "kcse2025": texts[4],
                "kcse2024": texts[5],
                "kcse2023": texts[6],
                "cluster_weight": texts[7]
            })
        return out
    except:
        return []

def main():
    """Launch browser with your Chrome profile and scrape."""
    # Path to your Chrome user data directory
    chrome_user_data = str(Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data")
    
    if not os.path.exists(chrome_user_data):
        print(f"ERROR: Chrome user data not found at {chrome_user_data}")
        sys.exit(1)
    
    print(f"Using Chrome profile from: {chrome_user_data}")
    print("Launching browser...\n")
    
    try:
        with sync_playwright() as p:
            # Launch Chromium using Chrome's user data directory (reuses your session)
            browser = p.chromium.launch_persistent_context(
                user_data_dir=chrome_user_data,
                headless=False,  # Show the browser so you can see what's happening
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                ]
            )
            
            page = browser.new_page()
            print("Browser launched. Navigating to KUCCPS...\n")
            
            # Scrape clusters
            for cluster in range(CLUSTER_START, CLUSTER_END + 1):
                print(f"\n{'='*60}")
                print(f"CLUSTER {cluster}")
                print(f"{'='*60}")
                
                cluster_url = CLUSTER_SEARCH_URL.format(cluster)
                page.goto(cluster_url, wait_until="networkidle")
                safe_sleep()
                
                # Try to show 100 entries per page
                try:
                    page.select_option('select', '100')
                    time.sleep(1)
                except:
                    pass
                
                # Get rows
                try:
                    page.wait_for_selector('table tbody tr', timeout=5000)
                except:
                    print("ERROR: Could not find course table. Are you logged in?")
                    browser.close()
                    return
                
                rows = page.query_selector_all('table tbody tr')
                total_rows = len(rows)
                print(f"Found {total_rows} courses\n")
                
                # Loop through rows
                for idx in range(total_rows):
                    try:
                        print(f"[{idx+1}/{total_rows}] ", end="", flush=True)
                        
                        # Reload rows to avoid stale references
                        rows = page.query_selector_all('table tbody tr')
                        if idx >= len(rows):
                            print("Row no longer available, skipping.")
                            continue
                        
                        row = rows[idx]
                        cells = row.query_selector_all('td')
                        
                        # Get course name (usually first or second cell)
                        course_name = None
                        course_url = None
                        
                        # Look for link
                        a_tag = row.query_selector('a')
                        if a_tag:
                            course_name = a_tag.inner_text().strip()
                            href = a_tag.get_attribute('href')
                            if href:
                                course_url = 'https://students.kuccps.net' + href if href.startswith('/') else href
                        
                        # If no link found, try to click row
                        if not course_url:
                            if len(cells) > 1:
                                course_name = cells[1].inner_text().strip()
                            
                            try:
                                # Click second cell (which acts like a link on this site)
                                if len(cells) > 1:
                                    cells[1].click()
                                else:
                                    row.click()
                                page.wait_for_load_state('networkidle', timeout=5000)
                                course_url = page.url
                            except:
                                print("Could not navigate, skipping.")
                                page.goto(cluster_url, wait_until="networkidle")
                                continue
                        
                        if not course_url:
                            print("No URL found, skipping.")
                            page.goto(cluster_url, wait_until="networkidle")
                            continue
                        
                        # Navigate if we found a link
                        if a_tag and course_url:
                            page.goto(course_url, wait_until="networkidle")
                        
                        safe_sleep()
                        
                        # Get course title
                        try:
                            title_elem = page.query_selector('h4, h3, h2')
                            course_title = title_elem.inner_text().strip() if title_elem else course_name
                        except:
                            course_title = course_name
                        
                        print(f"'{course_title[:50]}...' ", end="", flush=True)
                        
                        # Extract data
                        entry_reqs = extract_table_section(page, "MINIMUM ENTRY REQUIREMENTS")
                        subject_reqs = extract_table_section(page, "MINIMUM SUBJECT REQUIREMENTS")
                        programmes = extract_available_programmes(page)
                        
                        print(f"({len(programmes)} programmes)")
                        
                        # Save JSON
                        result = {
                            "cluster": cluster,
                            "course_index": idx + 1,
                            "course_name": course_name,
                            "course_title": course_title,
                            "entry_requirements": entry_reqs,
                            "subject_requirements": subject_reqs,
                            "available_programmes": programmes,
                            "source_url": course_url
                        }
                        append_json(result)
                        
                        # Save CSV rows
                        if programmes:
                            for p_row in programmes:
                                csv_row = {
                                    "cluster": cluster,
                                    "course_name": course_name,
                                    "course_title": course_title,
                                    "entry_requirements": " | ".join(entry_reqs),
                                    "subject_requirements": " | ".join(subject_reqs),
                                    "institution": p_row.get("institution", ""),
                                    "institution_type": p_row.get("institution_type", ""),
                                    "programme_code": p_row.get("programme_code", ""),
                                    "programme_name": p_row.get("programme_name", ""),
                                    "kcse2025": p_row.get("kcse2025", ""),
                                    "kcse2024": p_row.get("kcse2024", ""),
                                    "kcse2023": p_row.get("kcse2023", ""),
                                    "cluster_weight": p_row.get("cluster_weight", ""),
                                    "source_url": course_url
                                }
                                write_csv_row(csv_row)
                        else:
                            csv_row = {
                                "cluster": cluster,
                                "course_name": course_name,
                                "course_title": course_title,
                                "entry_requirements": " | ".join(entry_reqs),
                                "subject_requirements": " | ".join(subject_reqs),
                                "institution": "",
                                "institution_type": "",
                                "programme_code": "",
                                "programme_name": "",
                                "kcse2025": "",
                                "kcse2024": "",
                                "kcse2023": "",
                                "cluster_weight": "",
                                "source_url": course_url
                            }
                            write_csv_row(csv_row)
                        
                        # Go back to cluster page
                        page.goto(cluster_url, wait_until="networkidle")
                        safe_sleep()
                        
                    except Exception as e:
                        print(f"ERROR: {e}")
                        try:
                            page.goto(cluster_url, wait_until="networkidle")
                        except:
                            pass
                        continue
            
            browser.close()
            print(f"\n{'='*60}")
            print("✓ Scraping complete!")
            print(f"{'='*60}")
            print(f"Results saved to:")
            print(f"  • {OUT_JSON}")
            print(f"  • {OUT_CSV}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
