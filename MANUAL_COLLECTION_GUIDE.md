# Manual Data Collection Guide

Since automated scraping is blocked by your network firewall, here are **2 working methods** to collect the data:

---

## ✅ METHOD 1: Save HTML Files (RECOMMENDED - Fastest & Most Accurate)

### Steps:

1. **Open your browser** and navigate to KUCCPS course pages:
   - Start at: https://students.kuccps.net/programmes/search/?group=cluster_1
   - Click on any course to view details

2. **Save each course page as HTML:**
   - Right-click anywhere on the page
   - Select **"Save As"** or **"Save Page As"**
   - Choose **"Webpage, HTML Only"** (NOT "Complete")
   - Navigate to: `C:\Users\kelvinnj\Desktop\kuccps-scraper\saved_pages\`
   - Name it something descriptive like: `cluster1_engineering.html`
   - Click **Save**

3. **Repeat for all courses** you want to scrape (all 20 clusters)

4. **Run the parser script:**
   ```powershell
   python parse_saved_html.py
   ```

5. **Done!** Your data will be in:
   - `data/kuccps_courses.json` (detailed JSON format)
   - `data/kuccps_courses.csv` (flattened spreadsheet format)

### Tips:
- Save files with descriptive names: `cluster1_course1.html`, `cluster2_course5.html`, etc.
- You can save multiple pages at once (open tabs, save each)
- The script automatically extracts ALL data from the HTML files
- No manual typing needed!

---

## 🎯 METHOD 2: Screenshot + OCR (If HTML doesn't work)

If the saved HTML files don't contain the data (due to JavaScript rendering), we can use screenshot + OCR:

### Steps:

1. **Take screenshots of course pages:**
   - Open a course page
   - Press `Win + Shift + S` to take a screenshot
   - Save screenshots to: `saved_pages/screenshots/`

2. **Run OCR extraction script:**
   ```powershell
   python extract_from_screenshots.py
   ```

(I can create this script if METHOD 1 doesn't work for you)

---

## 📊 What Data Gets Extracted

From each course page, the script extracts:

### ✓ Course Information:
- Course Title

### ✓ Entry Requirements:
- Cluster subjects
- Minimum grades required

### ✓ Subject Requirements:
- Required subjects
- Minimum grades per subject

### ✓ Available Programmes:
- Institution name
- County
- Programme type
- Programme code
- Programme name
- KCSE 2025 cutoff points
- KCSE 2024 cutoff points
- KCSE 2023 cutoff points
- Cluster weight

---

## 🔧 Troubleshooting

### "No HTML files found"
- Make sure you saved files to the `saved_pages` folder
- Check the file extension is `.html` or `.htm`

### "No data extracted"
- Open one of your saved HTML files in Notepad
- Check if it contains the actual course data (not just "Page Blocked")
- If it's empty/blocked, try saving while logged in to KUCCPS

### "Parse error"
- Some HTML files might have different formatting
- Run the script anyway - it will skip problematic files
- Send me the error message and I can fix the parser

---

## 📂 File Organization

```
kuccps-scraper/
├── saved_pages/              ← Save your HTML files here
│   ├── cluster1_course1.html
│   ├── cluster1_course2.html
│   ├── cluster2_course1.html
│   └── ...
├── data/
│   ├── kuccps_courses.json   ← Output (detailed)
│   └── kuccps_courses.csv    ← Output (spreadsheet)
└── parse_saved_html.py       ← Parser script
```

---

## ⚡ Quick Start

1. Open browser, go to KUCCPS
2. Right-click page → Save As → HTML Only → Save to `saved_pages/`
3. Repeat for all courses
4. Run: `python parse_saved_html.py`
5. Check `data/` folder for results!

---

## 📞 Need Help?

If METHOD 1 doesn't work:
1. Save one HTML file and check if it contains data (open in Notepad)
2. If empty, the page might be JavaScript-rendered - let me know
3. I can create METHOD 2 (screenshot OCR) or other alternatives

The key is: **Your browser can access the data, so we work with what your browser gives us!**
