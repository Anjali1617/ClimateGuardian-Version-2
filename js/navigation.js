/* ==========================================
   NAVIGATION & TAB MANAGEMENT
   ========================================== */

function showSection(section) {
    // Update sidebar button states
    document.querySelectorAll('.sidebar .nav-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Toggle sections
    if (section === 'student') {
        document.getElementById('student-section').style.display = 'block';
        document.getElementById('admin-section').style.display = 'none';
    } else {
        document.getElementById('student-section').style.display = 'none';
        document.getElementById('admin-section').style.display = 'block';
        updateDashboard();
    }
}

function showTab(tab) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Remove active state from all tab buttons
    document.querySelectorAll('#student-section .nav-btn').forEach(btn => btn.classList.remove('active'));
    
    // Activate clicked button
    event.target.classList.add('active');
    
    // Show selected tab
    document.getElementById(tab + '-tab').classList.add('active');
}
