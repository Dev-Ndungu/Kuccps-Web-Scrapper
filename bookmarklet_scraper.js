// KUCCPS Scraper - Run this in your browser console
// Instructions:
// 1. Go to https://students.kuccps.net/programmes/search/?group=cluster_1
// 2. Press F12 to open DevTools
// 3. Go to Console tab
// 4. Copy and paste this entire script
// 5. Press Enter and wait for it to finish

(async function() {
    console.log('KUCCPS Scraper Started!');
    console.log('This will scrape all 20 clusters. Please wait...\n');
    
    const allData = [];
    const baseUrl = 'https://students.kuccps.net';
    
    // Helper function to wait
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
    // Extract course data from current page
    function extractCourseData() {
        const title = document.querySelector('h3.text-center')?.innerText?.trim() || '';
        const cluster = document.querySelector('.btn-danger')?.innerText?.trim() || '';
        
        // Extract entry requirements
        const entryReqs = [];
        const entryRows = document.querySelectorAll('h3:contains("Minimum Entry Requirements") ~ table tbody tr, h3.box-title .text-megna:contains("Minimum Entry Requirements") ~ table tbody tr');
        document.querySelectorAll('table tbody tr').forEach(row => {
            const cells = row.querySelectorAll('th, td');
            if (cells.length >= 2 && cells[0].innerText.includes('Cluster Subject')) {
                entryReqs.push({
                    requirement: cells[0].innerText.trim(),
                    value: cells[1].innerText.trim()
                });
            }
        });
        
        // Extract subject requirements
        const subjectReqs = [];
        document.querySelectorAll('table tbody tr').forEach(row => {
            const cells = row.querySelectorAll('th, td');
            if (cells.length >= 2 && cells[0].innerText.includes('Subject') && !cells[0].innerText.includes('Cluster')) {
                subjectReqs.push({
                    requirement: cells[0].innerText.trim(),
                    value: cells[1].innerText.trim(),
                    grade: cells.length > 2 ? cells[2].innerText.trim() : ''
                });
            }
        });
        
        // Extract available programmes
        const programmes = [];
        const progRows = document.querySelectorAll('h4:contains("Available Programmes") ~ div table tbody tr, .table-responsive table tbody tr');
        document.querySelectorAll('.table-responsive table tbody tr').forEach(row => {
            const cells = row.querySelectorAll('td, th');
            if (cells.length >= 8) {
                const instText = cells[0].innerText.trim();
                const lines = instText.split('\n').filter(l => l.trim());
                
                programmes.push({
                    institution: lines[0] || '',
                    county: lines[1] || '',
                    institution_type: cells[1].innerText.trim(),
                    programme_code: cells[2].innerText.trim(),
                    programme_name: cells[3].innerText.trim(),
                    kcse2025_cutoff: cells[4].innerText.trim(),
                    kcse2024_cutoff: cells[5].innerText.trim(),
                    kcse2023_cutoff: cells[6].innerText.trim(),
                    cluster_weight: cells[7].innerText.trim()
                });
            }
        });
        
        return {
            title,
            cluster,
            entry_requirements: entryReqs,
            subject_requirements: subjectReqs,
            available_programmes: programmes,
            url: window.location.href
        };
    }
    
    // Scrape all clusters
    for (let clusterNum = 1; clusterNum <= 20; clusterNum++) {
        console.log(`\n=== Scraping Cluster ${clusterNum} ===`);
        
        // Navigate to cluster
        const clusterUrl = `${baseUrl}/programmes/search/?group=cluster_${clusterNum}`;
        window.location.href = clusterUrl;
        await wait(3000); // Wait for page to load
        
        // Find all course rows
        const rows = document.querySelectorAll('table tbody tr');
        console.log(`Found ${rows.length} courses`);
        
        for (let i = 0; i < rows.length; i++) {
            console.log(`  [${i+1}/${rows.length}] `, { end: '' });
            
            // Re-query rows after navigation
            const currentRows = document.querySelectorAll('table tbody tr');
            if (i >= currentRows.length) break;
            
            const row = currentRows[i];
            const link = row.querySelector('a');
            const cells = row.querySelectorAll('td');
            
            let courseUrl = null;
            let courseName = '';
            
            if (link) {
                courseUrl = link.href;
                courseName = link.innerText.trim();
            } else if (cells.length > 1) {
                courseName = cells[1].innerText.trim();
                // Try clicking the cell
                cells[1].click();
                await wait(2000);
                courseUrl = window.location.href;
            }
            
            if (!courseUrl) {
                console.log('No URL, skipping');
                continue;
            }
            
            // Navigate to course page
            if (link) {
                window.location.href = courseUrl;
                await wait(2000);
            }
            
            // Extract data
            const courseData = extractCourseData();
            courseData.cluster_number = clusterNum;
            courseData.course_name = courseName;
            allData.push(courseData);
            
            console.log(`${courseName.substring(0, 40)}... (${courseData.available_programmes.length} programmes)`);
            
            // Go back to cluster list
            window.location.href = clusterUrl;
            await wait(2000);
        }
    }
    
    console.log('\n\n=== SCRAPING COMPLETE! ===');
    console.log(`Total courses scraped: ${allData.length}`);
    console.log('\nData is saved in the variable: scrapedData');
    console.log('To download as JSON, run: downloadJSON()');
    console.log('To download as CSV, run: downloadCSV()');
    
    // Make data available globally
    window.scrapedData = allData;
    
    // Download functions
    window.downloadJSON = function() {
        const dataStr = JSON.stringify(allData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'kuccps_courses.json';
        link.click();
        console.log('Downloaded kuccps_courses.json');
    };
    
    window.downloadCSV = function() {
        const rows = [];
        // Header
        rows.push([
            'Cluster', 'Course Name', 'Course Title', 'Entry Requirements', 'Subject Requirements',
            'Institution', 'County', 'Institution Type', 'Programme Code', 'Programme Name',
            'KCSE 2025 Cutoff', 'KCSE 2024 Cutoff', 'KCSE 2023 Cutoff', 'Cluster Weight', 'URL'
        ]);
        
        allData.forEach(course => {
            const entryReqStr = course.entry_requirements.map(r => `${r.requirement}: ${r.value}`).join(' | ');
            const subjectReqStr = course.subject_requirements.map(r => `${r.requirement}: ${r.value} ${r.grade}`).join(' | ');
            
            if (course.available_programmes.length > 0) {
                course.available_programmes.forEach(prog => {
                    rows.push([
                        course.cluster_number,
                        course.course_name,
                        course.title,
                        entryReqStr,
                        subjectReqStr,
                        prog.institution,
                        prog.county,
                        prog.institution_type,
                        prog.programme_code,
                        prog.programme_name,
                        prog.kcse2025_cutoff,
                        prog.kcse2024_cutoff,
                        prog.kcse2023_cutoff,
                        prog.cluster_weight,
                        course.url
                    ]);
                });
            } else {
                rows.push([
                    course.cluster_number,
                    course.course_name,
                    course.title,
                    entryReqStr,
                    subjectReqStr,
                    '', '', '', '', '', '', '', '', '', course.url
                ]);
            }
        });
        
        const csvContent = rows.map(row => 
            row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
        ).join('\n');
        
        const dataBlob = new Blob([csvContent], {type: 'text/csv'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'kuccps_courses.csv';
        link.click();
        console.log('Downloaded kuccps_courses.csv');
    };
    
})();
