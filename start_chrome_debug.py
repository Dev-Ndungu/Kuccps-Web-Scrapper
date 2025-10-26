#!/usr/bin/env python3
"""
Launch Chrome with remote debugging enabled, then scrape KUCCPS courses.
"""
import subprocess
import time
import sys
import os

def launch_chrome_with_debugging():
    """Launch Chrome with remote debugging on port 9222."""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        print(f"ERROR: Chrome not found at {chrome_path}")
        sys.exit(1)
    
    print("Starting Chrome with remote debugging enabled...")
    print("(It should open at students.kuccps.net or your home page)")
    print()
    
    # Launch Chrome with remote debugging and disable sandbox for stability
    subprocess.Popen([
        chrome_path,
        "--remote-debugging-port=9222",
        "--disable-blink-features=AutomationControlled",
        "--disable-web-resources",
        "--no-first-run"
    ])
    
    print("Chrome is starting...")
    print("Waiting 5 seconds for Chrome to fully start...")
    time.sleep(5)
    
    print("\n✓ Chrome should now be running with remote debugging on port 9222")
    print("\nNext steps:")
    print("1. Log in at students.kuccps.net if not already logged in")
    print("2. Navigate to: https://students.kuccps.net/programmes/search/?group=cluster_1")
    print("3. Run: python scrape_with_browser.py")

if __name__ == "__main__":
    launch_chrome_with_debugging()
