"""
Browser Console Script - Copy/Paste in Chrome DevTools

HOW TO USE:
1. Open a KUCCPS course detail page in your browser
2. Press F12 to open Developer Tools
3. Go to the "Console" tab
4. Copy and paste this ENTIRE script
5. Press Enter
6. The course data will be automatically saved to localStorage
7. After visiting all pages, run the export script to download all data

This script runs INSIDE your browser, so no network blocking issues!
"""

BROWSER_CONSOLE_SCRIPT = """
(function() {
    console.log('🔍 Extracting course data...');
    
    // Helper function to extract text from element
    function getText(selector) {
        const el = document.querySelector(selector);
        return el ? el.textContent.trim() : '';
    }
    
    // Helper function to extract table data
    function extractTable(headerText) {
        const headers = Array.from(document.querySelectorAll('h4'));
        const targetHeader = headers.find(h => h.textContent.includes(headerText));
        
        if (!targetHeader) return [];
        
        const table = targetHeader.nextElementSibling;
        if (!table || table.tagName !== 'TABLE') return [];
        
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        return rows.map(row => {
            const cells = Array.from(row.querySelectorAll('td, th'));
            return cells.map(cell => cell.textContent.trim());
        }).filter(row => row.length > 0);
    }
    
    // Extract course title
    const courseTitle = getText('h3') || 'Unknown Course';
    
    // Extract entry requirements
    const entryRequirements = extractTable('Entry Requirements');
    
    // Extract subject requirements
    const subjectRequirements = extractTable('Subject Requirements');
    
    // Extract available programmes
    const programmeRows = extractTable('Available Programmes');
    const programmes = programmeRows.map(row => {
        if (row.length < 7) return null;
        
        // Parse institution and county
        const institutionFull = row[0];
        let institution = institutionFull;
        let county = '';
        
        const countyMatch = institutionFull.match(/\(([^)]+)\)$/);
        if (countyMatch) {
            county = countyMatch[1];
            institution = institutionFull.substring(0, countyMatch.index).trim();
        } else if (institutionFull.includes(',')) {
            const parts = institutionFull.split(',');
            institution = parts[0].trim();
            county = parts[1].trim();
        }
        
        return {
            institution: institution,
            county: county,
            type: row[1],
            programme_code: row[2],
            programme_name: row[3],
            kcse_2025_cutoff: row[4],
            kcse_2024_cutoff: row[5],
            kcse_2023_cutoff: row[6],
            cluster_weight: row[7] || ''
        };
    }).filter(p => p !== null);
    
    // Create course object
    const courseData = {
        url: window.location.href,
        course_title: courseTitle,
        entry_requirements: entryRequirements,
        subject_requirements: subjectRequirements,
        available_programmes: programmes,
        scraped_at: new Date().toISOString()
    };
    
    // Save to localStorage
    const storageKey = 'kuccps_scraped_courses';
    let allCourses = [];
    
    try {
        const existing = localStorage.getItem(storageKey);
        if (existing) {
            allCourses = JSON.parse(existing);
        }
    } catch (e) {
        console.error('Error loading existing data:', e);
    }
    
    // Add this course (check for duplicates by URL)
    const existingIndex = allCourses.findIndex(c => c.url === courseData.url);
    if (existingIndex >= 0) {
        allCourses[existingIndex] = courseData;
        console.log('✓ Updated existing course');
    } else {
        allCourses.push(courseData);
        console.log('✓ Added new course');
    }
    
    // Save back to localStorage
    localStorage.setItem(storageKey, JSON.stringify(allCourses));
    
    console.log(`✓ Course saved! Total courses: ${allCourses.length}`);
    console.log('Course:', courseTitle);
    console.log('Programmes:', programmes.length);
    console.log('\\nTo export all data, run: exportKuccpsData()');
    
    // Make export function available globally
    window.exportKuccpsData = function() {
        const data = localStorage.getItem(storageKey);
        if (!data) {
            console.error('No data found!');
            return;
        }
        
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'kuccps_courses_' + new Date().toISOString().split('T')[0] + '.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✓ Data exported!');
    };
    
    window.clearKuccpsData = function() {
        if (confirm('Clear all scraped data?')) {
            localStorage.removeItem(storageKey);
            console.log('✓ Data cleared!');
        }
    };
    
})();
"""

# Export function to run AFTER visiting all pages
EXPORT_SCRIPT = """
// Run this after visiting all course pages to download the collected data
exportKuccpsData();
"""

# Clear function if needed
CLEAR_SCRIPT = """
// Run this to clear all collected data and start fresh
clearKuccpsData();
"""

def create_instructions_file():
    """Create a simple text file with instructions"""
    instructions = f"""
╔════════════════════════════════════════════════════════════════╗
║          KUCCPS DATA COLLECTION - BROWSER CONSOLE METHOD       ║
╚════════════════════════════════════════════════════════════════╝

This method uses your browser's Developer Console to extract data
directly from the page. No network blocking, no automation detection!

═══════════════════════════════════════════════════════════════════

📋 STEP-BY-STEP INSTRUCTIONS:

1. Open Chrome/Edge and log in to KUCCPS
   → Navigate to: https://students.kuccps.net/

2. Open Developer Tools
   → Press F12 (or Right-click → Inspect)
   → Click the "Console" tab

3. Copy the extraction script below and paste into Console
   → Press Enter to run it

4. Visit each course page
   → The script runs automatically when you paste it once
   → OR paste and run the script on each page
   → You'll see "✓ Course saved!" message

5. After visiting all courses, run the export command:
   → Type in Console: exportKuccpsData()
   → Press Enter
   → A JSON file will download automatically

6. Move the downloaded JSON file to this folder:
   → C:\\Users\\kelvinnj\\Desktop\\kuccps-scraper\\data\\

7. Done! Your data is collected.

═══════════════════════════════════════════════════════════════════

📝 EXTRACTION SCRIPT (Copy everything below the line):

───────────────────────────────────────────────────────────────────
{BROWSER_CONSOLE_SCRIPT}
───────────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════════

📥 EXPORT COMMAND (After visiting all pages):

{EXPORT_SCRIPT}

═══════════════════════════════════════════════════════════════════

🗑️ CLEAR DATA (To start fresh):

{CLEAR_SCRIPT}

═══════════════════════════════════════════════════════════════════

💡 TIPS:

- The script saves data in your browser's localStorage
- You can close and reopen the browser - data persists
- Visit pages in any order - duplicates are handled automatically
- You'll see a counter showing how many courses are saved
- The export function downloads a JSON file with all data

═══════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

Q: "exportKuccpsData is not defined"
A: Run the extraction script first, then try export again

Q: Nothing happens when I paste the script
A: Make sure you're in the Console tab, not Elements or Network

Q: Can I automate this?
A: Unfortunately, your network blocks automation. This manual
   method is the most reliable way to collect data.

═══════════════════════════════════════════════════════════════════

🎯 WORKFLOW SUMMARY:

1. Open Console (F12)
2. Paste extraction script → Enter
3. Visit course pages (script auto-saves)
4. Type: exportKuccpsData() → Enter
5. Download appears → Move to data/ folder
6. Done!

═══════════════════════════════════════════════════════════════════
"""
    
    with open('BROWSER_CONSOLE_METHOD.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✓ Created BROWSER_CONSOLE_METHOD.txt")
    print("\nThis file contains:")
    print("  - Complete instructions")
    print("  - The extraction script to copy/paste")
    print("  - Export and clear commands")
    print("\nOpen BROWSER_CONSOLE_METHOD.txt to get started!")

if __name__ == "__main__":
    create_instructions_file()
