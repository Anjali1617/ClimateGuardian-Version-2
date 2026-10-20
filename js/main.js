/* ==========================================
   CLIMATEGUARDIAN AI - MAIN JAVASCRIPT
   Global Variables & State Management
   ========================================== */

// Global Variables
let ecoScore = 0;
let carbonLevel = 100;
let activityData = [];
let currentQuiz = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateMissionLog();
    
    // Mission select change handler
    const missionSelect = document.getElementById('missionSelect');
    if (missionSelect) {
        missionSelect.addEventListener('change', function() {
            document.getElementById('missionPoints').textContent = this.value;
        });
    }
});

// Activity Logging Function
function logActivity(action, points) {
    const date = new Date().toLocaleDateString();
    activityData.push({ action, points, date });
    updateMissionLog();
}
