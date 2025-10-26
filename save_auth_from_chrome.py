"""save_auth_from_chrome.py

Tries to connect to a running Chrome (your normal browser) via the DevTools
protocol and export the storage state (cookies + localStorage) for reuse by
Playwright. This lets the scraper run using your real logged-in session and
should avoid blocks that target automated headless browsers.

Usage:
1. If you already started Chrome with remote debugging enabled (port 9222), just
   run this script:
       python save_auth_from_chrome.py

2. If not, close Chrome and start it with remote debugging using PowerShell
   (replace the path if your Chrome is installed elsewhere):

   # Example PowerShell command (copy-paste):
   & "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222

   Then run this script.

Notes:
- If you prefer to use a different port, set the environment variable
  PLAYWRIGHT_CDP_URL (for example "http://127.0.0.1:9223") before running.
- This script will attempt to use the first available browser context from
  the connected Chrome. If that succeeds it will save `auth.json` in the
  current directory.
"""

import os
import time
import sys
from playwright.sync_api import sync_playwright

CDP_DEFAULT = os.environ.get("PLAYWRIGHT_CDP_URL", "http://127.0.0.1:9222")
OUT = "auth.json"

def main():
    print(f"Attempting to connect to Chrome CDP at {CDP_DEFAULT} ...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_DEFAULT)
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                print("Found existing browser context – using it to export storage state.")
            else:
                print("No existing contexts found on the connected browser. Creating a new context (may be empty).")
                context = browser.new_context()

            # Try to open the KUCCPS login page to ensure cookies/localStorage are loaded
            page = None
            try:
                page = context.new_page()
                print("Opening KUCCPS login page to load relevant storage...")
                page.goto("https://students.kuccps.net/login/", wait_until="networkidle", timeout=30000)
                time.sleep(1)
            except Exception as e:
                print("Warning: opening page failed (this may be okay if the browser already has storage).", str(e))

            # Save storage state
            try:
                context.storage_state(path=OUT)
                print(f"Saved storage state to {OUT}. You can now run crawler.py.")
            except Exception as e:
                print("Failed to save storage state:", e)
                sys.exit(1)

            # cleanup
            try:
                if page:
                    page.close()
            except Exception:
                pass

    except Exception as exc:
        print("Could not connect to Chrome DevTools endpoint.")
        print("Make sure Chrome is running with remote debugging enabled on port 9222.")
        print("Close all Chrome windows and start Chrome from PowerShell with:")
        print()
        print('  & "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        print()
        print("Then re-run this script. If Chrome is installed in a different path, update the command accordingly.")
        sys.exit(1)

if __name__ == '__main__':
    main()
