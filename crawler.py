# crawler.py
import os
import json
import time
import math
from dotenv import load_dotenv
from tqdm import tqdm
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

load_dotenv()

# Config
STORAGE = "auth.json"
OUT_JSON = "data/kuccps_courses.json"
OUT_CSV = "data/kuccps_courses.csv"

# Base cluster search URL; we'll substitute cluster number 1..20
CLUSTER_SEARCH_URL = "https://students.kuccps.net/programmes/search/?group=cluster_{}"

# Clusters to iterate (1..20)
CLUSTER_START = 1
CLUSTER_END = 20

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5

# polite delays
DELAY_MIN = 0.8
DELAY_MAX = 1.6

# create outputs if missing
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists(OUT_JSON):
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

# helper to append JSON
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
    """
    Extract table rows as dict from section containing header_text.
    Returns list of dicts with row headers and values.
    """
    try:
        selector = f'h3:has-text("{header_text}"), h4:has-text("{header_text}")'
        page.wait_for_selector(selector, timeout=3000)
        # Find the table after this header
        table = page.query_selector(f'{selector} ~ table, {selector} + table')
        if not table:
            return []
        
        rows = table.query_selector_all('tbody tr')
        out = []
        for r in rows:
            cells = r.query_selector_all('th, td')
            if len(cells) >= 2:
                # Skip footer/note rows
                text = r.inner_text().strip()
                if 'NOTE:' in text or 'considered' in text:
                    continue
                    
                header = cells[0].inner_text().strip()
                value = cells[1].inner_text().strip()
                # For subject requirements, also capture grade if present
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
    """
    Extracts rows from the AVAILABLE PROGRAMMES table into list of dicts.
    Extracts: Institution, County, Institution Type, Programme Code, Programme Name, 
    KCSE cutoffs (2025, 2024, 2023), Cluster Weights
    """
    try:
        selector = 'h4:has-text("Available Programmes") ~ div table tbody tr, h3:has-text("Available Programmes") ~ div table tbody tr'
        page.wait_for_selector(selector, timeout=3000)
        rows = page.query_selector_all(selector)
        out = []
        for r in rows:
            cols = r.query_selector_all('td, th')
            if len(cols) < 4:  # Skip header or incomplete rows
                continue
                
            # Extract institution name and county from first column
            institution_cell = cols[0].inner_text().strip()
            lines = [line.strip() for line in institution_cell.split('\n') if line.strip()]
            institution = lines[0] if lines else ""
            county = lines[1] if len(lines) > 1 else ""
            
            # Institution type from second column
            inst_type_cell = cols[1]
            inst_type = inst_type_cell.inner_text().strip()
            
            # Programme code
            prog_code = cols[2].inner_text().strip() if len(cols) > 2 else ""
            
            # Programme name
            prog_name = cols[3].inner_text().strip() if len(cols) > 3 else ""
            
            # Cutoffs (may be "-" if not available)
            kcse2025 = cols[4].inner_text().strip() if len(cols) > 4 else ""
            kcse2024 = cols[5].inner_text().strip() if len(cols) > 5 else ""
            kcse2023 = cols[6].inner_text().strip() if len(cols) > 6 else ""
            
            # Cluster weight
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
        print(f"    Error extracting programmes: {e}")
        return []

def main():
    if not os.path.exists(STORAGE):
        raise SystemExit(f"Storage file {STORAGE} not found. Run login_save_state.py first and authenticate.")

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(
            headless=False,
            slow_mo=100,  # Slow down actions to appear more human
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        context = browser.new_context(
            storage_state=STORAGE,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = context.new_page()
        
        # Set extra HTTP headers to appear more like a real browser
        page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        # For each cluster
        for cluster in range(CLUSTER_START, CLUSTER_END + 1):
            print(f"\n{'='*70}")
            print(f"CLUSTER {cluster}")
            print(f"{'='*70}")
            cluster_url = CLUSTER_SEARCH_URL.format(cluster)
            
            # Retry navigation if it fails
            for attempt in range(MAX_RETRIES):
                try:
                    print(f"Loading cluster {cluster} page...")
                    page.goto(cluster_url, wait_until="domcontentloaded", timeout=60000)
                    safe_sleep()
                    break
                except Exception as e:
                    print(f"  Attempt {attempt+1} failed: {e}")
                    if attempt < MAX_RETRIES - 1:
                        print(f"  Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        print(f"  Skipping cluster {cluster} after {MAX_RETRIES} attempts")
                        continue

            # Increase items per page if there's a length select (attempt to set to 100)
            try:
                page.wait_for_selector('select', timeout=5000)
                page.select_option('select', '100')
                print("  Set to show 100 entries per page")
                time.sleep(2)
            except Exception:
                print("  Using default page size")
                pass

            # Collect course link anchors visible on the page
            # The course link anchor is probably inside the first column or second; adjust if needed
            # We'll find all anchors in table body rows and operate on them by index
            # To avoid stale handles after navigation, we will re-query anchors each loop by index
            # First, count rows
            try:
                page.wait_for_selector('table tbody tr', timeout=5000)
                total_rows = len(page.query_selector_all('table tbody tr'))
            except PWTimeoutError:
                total_rows = 0
            print(f"Found {total_rows} rows in cluster {cluster}")

            # Loop row indices
            for idx in range(total_rows):
                print(f"\n[{idx+1}/{total_rows}] ", end='', flush=True)
                try:
                    # Re-query the anchor in this row
                    # Select: table tbody tr:nth-child(N) td a  (choose the anchor in the row)
                    row_selector = f"table tbody tr:nth-child({idx+1})"
                    row = page.query_selector(row_selector)
                    if not row:
                        print("Row not found, skipping.")
                        continue
                    
                    row_anchor_selector = f"table tbody tr:nth-child({idx+1}) td a"
                    a = page.query_selector(row_anchor_selector)

                    href = None
                    name = None

                    if a:
                        href = a.get_attribute("href")
                        name = a.inner_text().strip()
                        if href and href.startswith("/"):
                            href = "https://students.kuccps.net" + href
                        print(f"{name[:40]}...", end=' ', flush=True)
                        # Navigate directly
                        page.goto(href, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(1)
                    else:
                        # No anchor — try clicking the row or the second cell which on
                        # this site behaves like a link in the UI.
                        try:
                            second_td = row.query_selector('td:nth-child(2)')
                            name = second_td.inner_text().strip() if second_td else row.inner_text().strip()
                            print("Attempting to click row/cell for:", name)
                            clicked = False
                            try:
                                # Try clicking the second cell
                                if second_td:
                                    second_td.click()
                                    page.wait_for_load_state('networkidle', timeout=5000)
                                    clicked = True
                                else:
                                    row.click()
                                    page.wait_for_load_state('networkidle', timeout=5000)
                                    clicked = True
                            except Exception:
                                # fallback: try clicking the row
                                try:
                                    row.click()
                                    page.wait_for_load_state('networkidle', timeout=5000)
                                    clicked = True
                                except Exception:
                                    clicked = False

                            if clicked:
                                href = page.url
                                print("Navigated by click to:", href)
                                safe_sleep()
                            else:
                                # Attempt to parse onclick attribute for a URL
                                onclick = None
                                try:
                                    onclick = second_td.get_attribute('onclick') if second_td else row.get_attribute('onclick')
                                except Exception:
                                    onclick = None
                                if onclick and 'location' in onclick:
                                    import re
                                    m = re.search(r"['\"](\/[^'\"]+)['\"]", onclick)
                                    if m:
                                        href = 'https://students.kuccps.net' + m.group(1)
                                        print("Found URL in onclick:", href)
                                        page.goto(href, wait_until='networkidle')
                                        safe_sleep()
                                else:
                                    print("No clickable anchor or onclick URL found; skipping row.")
                                    # go to next row
                                    page.goto(cluster_url, wait_until="networkidle")
                                    continue
                        except Exception as e:
                            print("Error attempting to click row:", e)
                            page.goto(cluster_url, wait_until="networkidle")
                            continue

                    # Get page title (sensible fallback to given name)
                    try:
                        title = page.query_selector('h3.text-center, h4, h3')
                        course_title = title.inner_text().strip() if title else name
                    except Exception:
                        course_title = name
                    
                    print(f"-> {len(extract_available_programmes(page))} programmes", end=' ', flush=True)

                    # Extract sections
                    entry_reqs = extract_table_section(page, "MINIMUM ENTRY REQUIREMENTS")
                    subject_reqs = extract_table_section(page, "MINIMUM SUBJECT REQUIREMENTS")
                    programmes = extract_available_programmes(page)

                    # Build result object
                    result = {
                        "cluster": cluster,
                        "course_index_in_cluster": idx + 1,
                        "course_name_list_page": name,
                        "course_title": course_title,
                        "entry_requirements": entry_reqs,
                        "subject_requirements": subject_reqs,
                        "available_programmes": programmes,
                        "source_url": href
                    }

                    # Persist incrementally
                    append_json(result)

                    # Write flattened rows to CSV for each available programme (or one empty row if none)
                    if programmes:
                        for p_row in programmes:
                            csv_row = {
                                "cluster": cluster,
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
                                "source_url": href
                            }
                            write_csv_row(csv_row)
                    else:
                        csv_row = {
                            "cluster": cluster,
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
                            "source_url": href
                        }
                        write_csv_row(csv_row)

                    print("✓")

                    # Go back to cluster list
                    page.goto(cluster_url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(1)

                except Exception as e:
                    print("Error scraping row idx", idx, ":", str(e))
                    try:
                        # attempt to go back to cluster page to continue safely
                        page.goto(cluster_url, wait_until="networkidle")
                        time.sleep(1)
                    except Exception:
                        pass
                    continue

        browser.close()
        
        print("\n" + "="*70)
        print("SCRAPING COMPLETE!")
        print("="*70)
        
        # Count total entries
        try:
            with open(OUT_JSON, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                total_courses = len(data)
                total_programmes = sum(len(course.get('available_programmes', [])) for course in data)
            
            print(f"\n✓ Total courses scraped: {total_courses}")
            print(f"✓ Total programmes found: {total_programmes}")
        except:
            pass
        
        print(f"\n📁 Data saved to:")
        print(f"   • {OUT_JSON}")
        print(f"   • {OUT_CSV}")
        print("\n" + "="*70)

if __name__ == "__main__":
    main()
