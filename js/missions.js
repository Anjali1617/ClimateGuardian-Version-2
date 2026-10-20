/* ==========================================
   MISSION TRACKER
   ========================================== */

function logMission() {
    const select = document.getElementById('missionSelect');
    const points = parseInt(select.value);
    const action = select.options[select.selectedIndex].text.split(' (')[0];
    
    logActivity(action, points);
    ecoScore += points;
    document.getElementById('ecoScore').textContent = ecoScore;
    
    alert(`✅ Mission "${action}" logged! +${points} points`);
    updateMissionLog();
}

function updateMissionLog() {
    const logContent = document.getElementById('logContent');
    if (activityData.length === 0) {
        logContent.innerHTML = 'No missions logged yet.';
        return;
    }

    let html = '<div class="space-y-2">';
    activityData.slice(-5).reverse().forEach(item => {
        html += `
            <div class="p-2 bg-white rounded border-l-4 border-green-500">
                <strong>${item.action}</strong> - ${item.points} points
                <br><span class="text-xs text-gray-500">${item.date}</span>
            </div>
        `;
    });
    html += '</div>';
    logContent.innerHTML = html;
}
