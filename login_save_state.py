# login_save_state.py
import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()  # reads .env in current directory

KUCCPS_LOGIN = "https://students.kuccps.net/login/"

INDEX = os.getenv("KUCCPS_INDEX", "")
YEAR = os.getenv("KUCCPS_YEAR", "")
PASSWORD = os.getenv("KUCCPS_PASS", "")

if not INDEX or not YEAR or not PASSWORD:
    raise SystemExit("Please set KUCCPS_INDEX, KUCCPS_YEAR and KUCCPS_PASS in .env")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Changed to visible browser to act more like a normal user
        context = browser.new_context()
        page = context.new_page()

        print("Opening KUCCPS login page...")
        page.goto(KUCCPS_LOGIN, wait_until="networkidle", timeout=60000)
        page.screenshot(path="login_page_vpn.png")
        with open("login_page_vpn.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # Fill form - selector ids from HTML you pasted
        page.fill('#id_kcse_index_number', INDEX)
        page.fill('#id_kcse_year', YEAR)
        page.fill('#id_password', PASSWORD)

        # Submit
        page.click('button[type="submit"]')

        print("Submitted login form. Waiting for navigation / possible manual verification.")
        # Give up to 2 minutes for manual verification (captcha/2FA) if needed
        # You can increase this if your 2FA uses SMS and takes longer
        time.sleep(5)
        # Wait until not on /login or until 2 minutes elapsed
        max_wait = 120
        waited = 0
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            current = page.url
            # If redirected away from login page, assume auth succeeded
            if "/login" not in current and current != KUCCPS_LOGIN:
                print("Detected redirect away from login page:", current)
                break
            print(f"Still on login page... ({waited}s) - finish manual verification if needed")

        # Save storage state (cookies + localStorage) to file
        storage_path = "auth.json"
        context.storage_state(path=storage_path)
        print(f"Saved authenticated storage state to {storage_path}")

        browser.close()

if __name__ == "__main__":
    main()

