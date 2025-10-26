# 🎯 KUCCPS Data Collection - All Methods

Your network firewall blocks automated scraping, so here are **3 working alternatives** that use your browser directly (which can access the data):

---

## 🏆 METHOD 1: One-Click Bookmarklet (FASTEST & EASIEST!)

**⏱️ Time: ~30 seconds per page (just one click!)**

### Quick Summary:
1. Create a bookmark with special code (1-minute setup)
2. Click the bookmark on each course page
3. Download all data as JSON on the last page

### Files:
- `BOOKMARKLET_METHOD.txt` - Complete instructions
- `create_bookmarklet.py` - Script that created the instructions

### Pros:
✅ Fastest method (1 click per page)
✅ No typing or copy/pasting
✅ Instant feedback popup
✅ Auto-downloads JSON file
✅ Works in any browser

### Cons:
❌ Need to visit each page manually
❌ One-time bookmark setup

**👉 RECOMMENDED IF: You want the quickest method**

---

## 📋 METHOD 2: Browser Console Script

**⏱️ Time: ~1 minute per page (copy/paste once)**

### Quick Summary:
1. Open browser Developer Console (F12)
2. Copy/paste the extraction script
3. Visit course pages (data auto-saves)
4. Run export command to download JSON

### Files:
- `BROWSER_CONSOLE_METHOD.txt` - Complete instructions
- `create_console_script.py` - Script that created the instructions

### Pros:
✅ More control over the process
✅ Can see exactly what's being extracted
✅ Data persists in browser storage
✅ Good for debugging

### Cons:
❌ Need to paste script (or run on each page)
❌ Requires some tech comfort with DevTools

**👉 RECOMMENDED IF: You're comfortable with browser DevTools**

---

## 💾 METHOD 3: Save HTML Files

**⏱️ Time: ~1-2 minutes per page (Right-click → Save As)**

### Quick Summary:
1. Right-click on course page → "Save As"
2. Save as "HTML Only" to `saved_pages/` folder
3. Repeat for all courses
4. Run `python parse_saved_html.py`
5. Get JSON + CSV output

### Files:
- `MANUAL_COLLECTION_GUIDE.md` - Complete instructions
- `parse_saved_html.py` - HTML parser script
- `saved_pages/` - Folder where you save HTML files

### Pros:
✅ Offline processing (save now, parse later)
✅ Can verify HTML files contain data
✅ Creates both JSON and CSV outputs
✅ Most reliable if JavaScript is an issue

### Cons:
❌ Slowest method (manual saving)
❌ Need to run parser script after
❌ More steps involved

**👉 RECOMMENDED IF: You prefer having offline backups of the pages**

---

## 📊 Comparison Table

| Method | Speed | Tech Level | Setup Time | Pros |
|--------|-------|------------|------------|------|
| **Bookmarklet** | ⭐⭐⭐⭐⭐ | Easy | 1 min | Fastest! One click per page |
| **Console** | ⭐⭐⭐⭐ | Medium | 2 min | More control, debugging |
| **Save HTML** | ⭐⭐ | Easy | 0 min | Offline, creates CSV too |

---

## 🎯 My Recommendation

**Start with METHOD 1 (Bookmarklet)** - It's the fastest and easiest:

1. Open `BOOKMARKLET_METHOD.txt`
2. Follow the setup instructions (1 minute)
3. Start clicking through course pages
4. Download your JSON file when done

**If bookmarklet doesn't work**, try METHOD 2 (Console Script):
1. Open `BROWSER_CONSOLE_METHOD.txt`
2. Copy/paste the script in Console
3. Visit pages, then export

**If you want CSV format too**, use METHOD 3 (Save HTML):
1. Open `MANUAL_COLLECTION_GUIDE.md`
2. Save pages as HTML
3. Run the parser script

---

## 📁 All Your Files

```
kuccps-scraper/
├── BOOKMARKLET_METHOD.txt           ← Method 1 instructions
├── BROWSER_CONSOLE_METHOD.txt       ← Method 2 instructions
├── MANUAL_COLLECTION_GUIDE.md       ← Method 3 instructions
├── THIS_FILE.md                     ← You are here!
│
├── create_bookmarklet.py            ← Creates Method 1 code
├── create_console_script.py         ← Creates Method 2 code
├── parse_saved_html.py              ← Parses Method 3 HTML files
│
├── saved_pages/                     ← Save HTML files here (Method 3)
└── data/
    ├── kuccps_courses.json          ← Output JSON
    └── kuccps_courses.csv           ← Output CSV (Method 3 only)
```

---

## 🚀 Quick Start Guide

### If you want the fastest method:
```
1. Open BOOKMARKLET_METHOD.txt
2. Create the bookmark (1 minute)
3. Start clicking!
```

### If you're tech-savvy:
```
1. Open BROWSER_CONSOLE_METHOD.txt
2. Open Console (F12)
3. Copy/paste script
4. Visit pages
```

### If you want offline processing:
```
1. Open MANUAL_COLLECTION_GUIDE.md
2. Save pages as HTML
3. Run: python parse_saved_html.py
```

---

## ❓ Which Method Should I Use?

**Choose Bookmarklet if:**
- You want the fastest method
- You don't mind clicking a button on each page
- You want instant feedback
- You're collecting data from many pages

**Choose Console Script if:**
- You're comfortable with browser DevTools
- You want to see the extraction process
- You want more control
- You might need to debug

**Choose Save HTML if:**
- You want to save the pages permanently
- You need CSV format output
- You prefer offline processing
- You're not in a hurry

---

## 🎉 Bottom Line

Since automated scraping is blocked by your network, we're using **your browser as the automation tool**. All three methods work by:

1. **You navigate** to pages (your browser = logged in, trusted)
2. **JavaScript extracts** the data (runs in your browser)
3. **Data is saved** locally (no network calls)

This bypasses the firewall completely because we're not using Playwright or automation tools - we're using your real browser!

---

## 💬 Need Help?

All three methods are documented with:
- ✅ Step-by-step instructions
- ✅ Troubleshooting tips
- ✅ Example workflows
- ✅ Copy/paste ready code

Just open the instruction file for your chosen method and follow along!

**Start with `BOOKMARKLET_METHOD.txt` - it's the easiest and fastest!**

---

## 🔧 Technical Notes

All methods extract:
- Course title
- Entry requirements
- Subject requirements  
- Available programmes (institution, county, type, code, name, cutoffs, weights)

The data format is identical across all methods - choose based on your workflow preference!
