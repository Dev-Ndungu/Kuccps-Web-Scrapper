#!/usr/bin/env python3
"""
Export cookies from your Chrome browser to auth.json for use with Playwright.
"""
import sqlite3
import json
import os
from pathlib import Path
import shutil

def get_chrome_cookies():
    """Extract cookies from Chrome's cookie database."""
    chrome_data_path = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
    cookies_db = chrome_data_path / "Cookies"
    cookies_copy = "cookies_temp.db"
    
    # Copy the database (Chrome locks it)
    shutil.copy(cookies_db, cookies_copy)
    
    cookies = {}
    try:
        conn = sqlite3.connect(cookies_copy)
        cursor = conn.cursor()
        cursor.execute("SELECT name, value, host_key, path FROM cookies WHERE host_key LIKE '%kuccps%'")
        
        for name, value, host_key, path in cursor.fetchall():
            cookies[name] = {
                "value": value,
                "domain": host_key.lstrip('.'),
                "path": path
            }
        
        conn.close()
    finally:
        # Clean up temp file
        if os.path.exists(cookies_copy):
            os.remove(cookies_copy)
    
    return cookies

def main():
    """Export cookies to auth.json."""
    print("Exporting cookies from Chrome...")
    
    try:
        cookies = get_chrome_cookies()
        
        if not cookies:
            print("No KUCCPS cookies found in Chrome.")
            print("\nPlease:")
            print("1. Make sure Chrome is running")
            print("2. Log in to students.kuccps.net")
            print("3. Try again")
            return
        
        # Create Playwright-compatible storage state format
        storage_state = {
            "cookies": [
                {
                    "name": name,
                    "value": data["value"],
                    "domain": data["domain"],
                    "path": data["path"],
                    "expires": -1,
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax"
                }
                for name, data in cookies.items()
            ],
            "origins": []
        }
        
        # Save to auth.json
        with open("auth.json", "w", encoding="utf-8") as f:
            json.dump(storage_state, f, indent=2)
        
        print(f"✓ Exported {len(cookies)} cookies to auth.json")
        print("\nNow you can run: python crawler.py")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nCouldn't export cookies. Make sure:")
        print("1. Chrome is running")
        print("2. You're logged into students.kuccps.net")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
