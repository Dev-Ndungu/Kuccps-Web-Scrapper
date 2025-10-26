#!/usr/bin/env python3
"""
Scrape KUCCPS courses using a browser instance.
This script launches a browser, waits for you to log in, then scrapes.
"""
import os
import json
import time
import pandas as pd
from playwright.sync_api import sync_playwright

OUT_JSON = "data/kuccps_courses.json"
OUT_CSV = "data/kuccps_courses.csv"

CLUSTER_SEARCH_URL = "https://students.kuccps.net/programmes/search/?group=cluster_{}"
CLUSTER_START = 1
CLUSTER_END = 20

DELAY_MIN = 0.5
DELAY_MAX = 1.2

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(OUT_JSON):
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

def append_json(obj):
    try:
        with open(OUT_JSON, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []
    
    data.append(obj)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
    """Extract table rows as dict from section containing header_text."""
    try:
        selector = f'h3:has-text("{header_text}"), h4:has-text("{header_text}")'
        page.wait_for_selector(selector, timeout=3000)
        table = page.query_selector(f'{selector} ~ table, {selector} + table')
        if not table:
            return []
        
        rows = table.query_selector_all('tbody tr')
        out = []
        for r in rows:
            cells = r.query_selector_all('th, td')
            if len(cells) >= 2:
                text = r.inner_text().strip()
                if 'NOTE:' in text or 'considered' in text:
                    continue
                    
                header = cells[0].inner_text().strip()
                value = cells[1].inner_text().strip()
                grade = cells[2].inner_text().strip() if len(cells) > 2 else ""
                
                out.append({
                    "requirement": header,
                    "value": value,
                    "grade": grade
                })
        return out
    except:
        return []

def extract_available_programmes(page):
    """Extract AVAILABLE PROGRAMMES table data."""
    try:
        selector = 'h4:has-text("Available Programmes") ~ div table tbody tr, h3:has-text("Available Programmes") ~ div table tbody tr'
        page.wait_for_selector(selector, timeout=3000)
        rows = page.query_selector_all(selector)
        out = []
        for r in rows:
            cols = r.query_selector_all('td, th')
            if len(cols) < 4:
                continue
                
            institution_cell = cols[0].inner_text().strip()
            lines = [line.strip() for line in institution_cell.split('\n') if line.strip()]
            institution = lines[0] if lines else ""
            county = lines[1] if len(lines) > 1 else ""
            
            inst_type = cols[1].inner_text().strip()
            prog_code = cols[2].inner_text().strip() if len(cols) > 2 else ""
            prog_name = cols[3].inner_text().strip() if len(cols) > 3 else ""
            kcse2025 = cols[4].inner_text().strip() if len(cols) > 4 else ""
            kcse2024 = cols[5].inner_text().strip() if len(cols) > 5 else ""
            kcse2023 = cols[6].inner_text().strip() if len(cols) > 6 else ""
            cluster_weight = cols[7].inner_text().strip() if len(cols) > 7 else ""
            
            out.append({
                "institution": institution,
                "county": county,
                "institution_type": inst_type,
                "programme_code": prog_code,
                "programme_name": prog_name,
                "kcse2025_cutoff": kcse2025,
                "kcse2024_cutoff": kcse2024,
                "kcse2023_cutoff": kcse2023,
                "cluster_weight": cluster_weight
            })
        return out
    except Exception as e:
        print(f"Error extracting programmes: {e}")
        return []

def main():
    """Connect to running Chrome via CDP and scrape."""
    print("Connecting to Chrome via CDP (Chrome DevTools Protocol)...")
    print("Make sure Chrome is running with: chrome.exe --remote-debugging-port=9222")
    print("And that you're logged in to students.kuccps.net")
    print()
    
    try:
        with sync_playwright() as p:
            # Connect to running Chrome instance
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the default context (your logged-in session)
            contexts = browser.contexts
            if not contexts:
                print("ERROR: No browser context found. Make sure Chrome is open with --remote-debugging-port=9222")
                return
            
            context = contexts[0]
            
            # Get existing pages or create new one
            pages = context.pages
            if pages:
                page = pages[0]
                print(f"Using existing page: {page.url}")
            else:
                page = context.new_page()
                print("Created new page")
            
            print("\n✓ Connected to Chrome!")
            print("✓ Make sure you're logged in to students.kuccps.net in this Chrome window")
            print("\nPress ENTER when ready to start scraping...")
            input()
            
            # Now scrape
            for cluster in range(CLUSTER_START, CLUSTER_END + 1):
                print(f"\n{'='*60}")
                print(f"CLUSTER {cluster}")
                print(f"{'='*60}\n")
                
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
                        
                        # Get course name
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
                            try:
                                page.goto(course_url, wait_until="domcontentloaded", timeout=10000)
                                time.sleep(2)
                            except Exception as nav_err:
                                print(f"Nav error, skipping ({nav_err})")
                                page.goto(cluster_url, wait_until="networkidle")
                                continue
                        
                        safe_sleep()
                        
                        # Get course title
                        try:
                            title_elem = page.query_selector('h4, h3, h2, .page-title, [class*="title"]')
                            course_title = title_elem.inner_text().strip() if title_elem else course_name
                        except:
                            course_title = course_name
                        
                        print(f"'{course_title[:40]}...' ", end="", flush=True)
                        
                        # Extract data
                        try:
                            entry_reqs = extract_table_section(page, "MINIMUM ENTRY REQUIREMENTS")
                            subject_reqs = extract_table_section(page, "MINIMUM SUBJECT REQUIREMENTS")
                            programmes = extract_available_programmes(page)
                        except Exception as e:
                            print(f"(extract error: {e})")
                            entry_reqs = []
                            subject_reqs = []
                            programmes = []
                        
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
                                    "entry_requirements": " | ".join([f"{r['requirement']}: {r['value']}" for r in entry_reqs]),
                                    "subject_requirements": " | ".join([f"{r['requirement']}: {r['value']} {r['grade']}" for r in subject_reqs]),
                                    "institution": p_row.get("institution", ""),
                                    "county": p_row.get("county", ""),
                                    "institution_type": p_row.get("institution_type", ""),
                                    "programme_code": p_row.get("programme_code", ""),
                                    "programme_name": p_row.get("programme_name", ""),
                                    "kcse2025_cutoff": p_row.get("kcse2025_cutoff", ""),
                                    "kcse2024_cutoff": p_row.get("kcse2024_cutoff", ""),
                                    "kcse2023_cutoff": p_row.get("kcse2023_cutoff", ""),
                                    "cluster_weight": p_row.get("cluster_weight", ""),
                                    "source_url": course_url
                                }
                                write_csv_row(csv_row)
                        else:
                            csv_row = {
                                "cluster": cluster,
                                "course_name": course_name,
                                "course_title": course_title,
                                "entry_requirements": " | ".join([f"{r['requirement']}: {r['value']}" for r in entry_reqs]),
                                "subject_requirements": " | ".join([f"{r['requirement']}: {r['value']} {r['grade']}" for r in subject_reqs]),
                                "institution": "",
                                "county": "",
                                "institution_type": "",
                                "programme_code": "",
                                "programme_name": "",
                                "kcse2025_cutoff": "",
                                "kcse2024_cutoff": "",
                                "kcse2023_cutoff": "",
                                "cluster_weight": "",
                                "source_url": course_url
                            }
                            write_csv_row(csv_row)
                        
                        print(f"    ✓ Saved")
                        
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
            
            # Don't close the browser - user might still be using it
            print(f"\n{'='*60}")
            print("✓ Scraping complete!")
            print(f"{'='*60}")
            print(f"\nResults saved to:")
            print(f"  • {OUT_JSON}")
            print(f"  • {OUT_CSV}")
            print(f"\nNote: Browser was NOT closed - you can continue using it")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
