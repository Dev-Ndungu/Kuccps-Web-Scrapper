"""login_persistent.py

Launches a persistent Chrome context (interactive) using Playwright so you can
log in with your normal browser UI. After you log in, the script saves the
storage state (cookies + localStorage) to `auth.json` for use by `crawler.py`.

Usage:
  1. Close other Chrome windows if you plan to reuse the same profile directory.
  2. Run: python login_persistent.py
  3. A Chrome window will open. Complete the login manually if required.
  4. The script will detect when the browser navigates away from /login/ and
     then save `auth.json`.

Notes:
- By default the script uses a separate profile directory at
  `./chrome_profile_for_scraper` to avoid interfering with your main profile.
  If you want to use your real profile, set the environment variable
  CHROME_USER_DATA to your profile path (e.g., %LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default),
  but be cautious — sharing your profile with automation can be risky.
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

KUCCPS_LOGIN = "https://students.kuccps.net/login/"
OUT = "auth.json"

# Path to Chrome executable (update if installed elsewhere)
CHROME_PATH = os.environ.get("CHROME_PATH", r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
# Profile dir to use for this persistent session (safe default inside project)
PROFILE_DIR = os.environ.get("CHROME_USER_DATA", os.path.join(os.getcwd(), "chrome_profile_for_scraper"))

def main():
    print("Launching persistent Chrome. Profile directory:", PROFILE_DIR)
    print("If Chrome fails to start, check CHROME_PATH or set CHROME_USER_DATA env var.")
    with sync_playwright() as p:
        # Launch persistent context which behaves like a normal browser window
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            executable_path=CHROME_PATH,
            headless=False,
            args=["--start-maximized"]
        )

        page = browser.new_page()
        print("Opening KUCCPS login page...")
        page.goto(KUCCPS_LOGIN, wait_until="networkidle")

        # Give user time to interact — wait until URL changes away from /login
        max_wait = 300  # 5 minutes
        waited = 0
        print("Please log in using the opened browser window. Waiting for redirect...")
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            current = page.url
            if "/login" not in current and current != KUCCPS_LOGIN:
                print("Detected redirect away from login page:", current)
                break
            print(f"Still on login page... ({waited}s) - complete manual login if needed")

        # Save storage state
        try:
            browser.storage_state(path=OUT)
            print(f"Saved authenticated storage state to {OUT}")
        except Exception as e:
            print("Failed to save storage state:", e)

        print("You can now close the browser. Exiting script.")
        try:
            browser.close()
        except Exception:
            pass

if __name__ == '__main__':
    main()
