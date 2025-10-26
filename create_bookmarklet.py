"""
Create a browser bookmark button that extracts course data with one click!

HOW TO CREATE THE BOOKMARKLET:

1. Open this file and copy the bookmarklet code below
2. In your browser, create a new bookmark (Ctrl+D or Bookmark Manager)
3. Name it: "Extract KUCCPS Course"
4. In the URL field, paste the bookmarklet code
5. Save the bookmark

HOW TO USE:

1. Navigate to a KUCCPS course page
2. Click the "Extract KUCCPS Course" bookmark
3. Data is automatically saved to browser storage
4. Visit all course pages (clicking the bookmark on each)
5. On the last page, click the bookmark twice to download all data

The bookmarklet code is below - copy everything starting with javascript:
"""

BOOKMARKLET = """javascript:(function(){function getText(s){const e=document.querySelector(s);return e?e.textContent.trim():''}function extractTable(t){const h=Array.from(document.querySelectorAll('h4')),r=h.find(e=>e.textContent.includes(t));if(!r)return[];const a=r.nextElementSibling;if(!a||a.tagName!=='TABLE')return[];return Array.from(a.querySelectorAll('tbody tr')).map(e=>Array.from(e.querySelectorAll('td, th')).map(t=>t.textContent.trim())).filter(e=>e.length>0)}const title=getText('h3')||'Unknown Course',entry=extractTable('Entry Requirements'),subject=extractTable('Subject Requirements'),progRows=extractTable('Available Programmes'),programmes=progRows.map(e=>{if(e.length<7)return null;let t=e[0],r=t,n='';const a=t.match(/\(([^)]+)\)$/);a?(n=a[1],r=t.substring(0,a.index).trim()):t.includes(',')&&(parts=t.split(','),r=parts[0].trim(),n=parts[1].trim());return{institution:r,county:n,type:e[1],programme_code:e[2],programme_name:e[3],kcse_2025_cutoff:e[4],kcse_2024_cutoff:e[5],kcse_2023_cutoff:e[6],cluster_weight:e[7]||''}}).filter(e=>e!==null),data={url:window.location.href,course_title:title,entry_requirements:entry,subject_requirements:subject,available_programmes:programmes,scraped_at:new Date().toISOString()};let courses=[];try{const e=localStorage.getItem('kuccps_scraped_courses');e&&(courses=JSON.parse(e))}catch(e){console.error('Error:',e)}const idx=courses.findIndex(e=>e.url===data.url);idx>=0?courses[idx]=data:courses.push(data);localStorage.setItem('kuccps_scraped_courses',JSON.stringify(courses));const msg=`✓ Saved! Total: ${courses.length} courses\\n${title}\\n${programmes.length} programmes\\n\\nClick again on last page to download`;if(courses.length>0&&confirm(msg+'\\n\\nDownload now?')){const e=new Blob([JSON.stringify(courses,null,2)],{type:'application/json'}),t=URL.createObjectURL(e),r=document.createElement('a');r.href=t,r.download='kuccps_courses_'+new Date().toISOString().split('T')[0]+'.json',document.body.appendChild(r),r.click(),document.body.removeChild(r),URL.revokeObjectURL(t),alert('Downloaded! '+courses.length+' courses')}else alert(msg)})();"""

# Readable version for understanding (not for bookmarking)
READABLE_VERSION = """
(function() {
    // Extract text helper
    function getText(selector) {
        const el = document.querySelector(selector);
        return el ? el.textContent.trim() : '';
    }
    
    // Extract table helper
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
    
    // Extract course data
    const title = getText('h3') || 'Unknown Course';
    const entry = extractTable('Entry Requirements');
    const subject = extractTable('Subject Requirements');
    const progRows = extractTable('Available Programmes');
    
    const programmes = progRows.map(row => {
        if (row.length < 7) return null;
        
        let institutionFull = row[0];
        let institution = institutionFull;
        let county = '';
        
        const countyMatch = institutionFull.match(/\(([^)]+)\)$/);
        if (countyMatch) {
            county = countyMatch[1];
            institution = institutionFull.substring(0, countyMatch.index).trim();
        } else if (institutionFull.includes(',')) {
            parts = institutionFull.split(',');
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
    const data = {
        url: window.location.href,
        course_title: title,
        entry_requirements: entry,
        subject_requirements: subject,
        available_programmes: programmes,
        scraped_at: new Date().toISOString()
    };
    
    // Load existing courses
    let courses = [];
    try {
        const existing = localStorage.getItem('kuccps_scraped_courses');
        if (existing) courses = JSON.parse(existing);
    } catch(e) {
        console.error('Error:', e);
    }
    
    // Add or update course
    const idx = courses.findIndex(c => c.url === data.url);
    if (idx >= 0) {
        courses[idx] = data;
    } else {
        courses.push(data);
    }
    
    // Save to localStorage
    localStorage.setItem('kuccps_scraped_courses', JSON.stringify(courses));
    
    // Show message
    const msg = `✓ Saved! Total: ${courses.length} courses
${title}
${programmes.length} programmes

Click again on last page to download`;
    
    // Ask if user wants to download
    if (courses.length > 0 && confirm(msg + '\\n\\nDownload now?')) {
        const blob = new Blob([JSON.stringify(courses, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'kuccps_courses_' + new Date().toISOString().split('T')[0] + '.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        alert('Downloaded! ' + courses.length + ' courses');
    } else {
        alert(msg);
    }
})();
"""

def create_bookmarklet_instructions():
    """Create instructions file for the bookmarklet"""
    
    instructions = f"""
╔════════════════════════════════════════════════════════════════╗
║        KUCCPS DATA COLLECTION - ONE-CLICK BOOKMARKLET          ║
╚════════════════════════════════════════════════════════════════╝

The easiest way to collect data! Just click a bookmark button on
each course page.

═══════════════════════════════════════════════════════════════════

📋 SETUP INSTRUCTIONS (Do this once):

1. Copy the bookmarklet code below (the ENTIRE line starting with 
   javascript:)

2. In your browser, create a new bookmark:
   
   Chrome/Edge:
   - Press Ctrl+D (or click the star in address bar)
   - Or go to Bookmarks → Bookmark Manager → Add new bookmark
   
3. Fill in the bookmark details:
   - Name: Extract KUCCPS Course
   - URL: [Paste the bookmarklet code here]
   
4. Save the bookmark

5. Done! You now have a one-click extractor button.

═══════════════════════════════════════════════════════════════════

📝 BOOKMARKLET CODE (Copy this ENTIRE line):

{BOOKMARKLET}

═══════════════════════════════════════════════════════════════════

🎯 HOW TO USE:

1. Log in to KUCCPS in your browser

2. Navigate to a course detail page

3. Click your "Extract KUCCPS Course" bookmark

4. You'll see a popup: "✓ Saved! Total: 1 courses..."
   - Click "Cancel" to continue to next page
   
5. Go to the next course page and click the bookmark again

6. Repeat for all courses you want to scrape

7. On the LAST page, click the bookmark and then click "OK" 
   when asked "Download now?"

8. A JSON file will download automatically

9. Move the downloaded file to:
   C:\\Users\\kelvinnj\\Desktop\\kuccps-scraper\\data\\

10. Done! All your data is collected.

═══════════════════════════════════════════════════════════════════

💡 ADVANTAGES:

✓ One click per page - super fast
✓ No copy/pasting needed
✓ Works in any browser
✓ Data saved automatically
✓ Can't be blocked by network firewall
✓ Popup confirms each save

═══════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

Q: Bookmark doesn't work when clicked
A: Make sure you copied the ENTIRE bookmarklet code starting with
   "javascript:" - even the tiniest character missing will break it

Q: Popup doesn't appear
A: Check if your browser is blocking popups. Allow popups for
   the KUCCPS site

Q: Want to start over?
A: Clear browser localStorage or use Incognito mode

Q: Lost my progress?
A: Data is saved in browser localStorage. Don't clear browser data
   until you've downloaded the JSON file

═══════════════════════════════════════════════════════════════════

🔧 TECHNICAL DETAILS:

- Data is stored in browser's localStorage
- Each course is identified by its URL (no duplicates)
- The bookmarklet is pure JavaScript that runs in your browser
- No external servers - everything happens locally
- The code extracts all tables and data automatically
- JSON file is generated from localStorage when you confirm download

═══════════════════════════════════════════════════════════════════

🎉 WORKFLOW SUMMARY:

1. Create bookmark with bookmarklet code (once)
2. Visit course page → Click bookmark → Click "Cancel"
3. Repeat step 2 for all courses
4. On last page → Click bookmark → Click "OK" to download
5. Move downloaded JSON to data/ folder
6. Done!

═══════════════════════════════════════════════════════════════════

📊 WHAT GETS EXTRACTED:

For each course:
- Course title
- Entry requirements (all rows)
- Subject requirements (all rows)
- Available programmes:
  * Institution name
  * County
  * Programme type
  * Programme code
  * Programme name
  * KCSE 2025/2024/2023 cutoff points
  * Cluster weights

═══════════════════════════════════════════════════════════════════

This is the FASTEST manual method! Much quicker than saving HTML
files. Just one click per page!

═══════════════════════════════════════════════════════════════════
"""
    
    with open('BOOKMARKLET_METHOD.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✓ Created BOOKMARKLET_METHOD.txt")
    print("\nThis method is the FASTEST:")
    print("  1. Create one bookmark (one-time setup)")
    print("  2. Click it on each course page")
    print("  3. Download JSON on the last page")
    print("\nOpen BOOKMARKLET_METHOD.txt for complete instructions!")

if __name__ == "__main__":
    create_bookmarklet_instructions()
