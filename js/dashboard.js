/* ==========================================
   ADMIN DASHBOARD
   ========================================== */

function updateDashboard() {
    const totalPoints = activityData.reduce((sum, item) => sum + item.points, 0);
    const totalActions = activityData.length;
    const treesPlanted = activityData.filter(item => item.action.includes('Tree')).length;
    
    document.getElementById('totalPoints').textContent = totalPoints;
    document.getElementById('totalActions').textContent = totalActions;
    document.getElementById('treesPlanted').textContent = treesPlanted;
    
    const tableBody = document.getElementById('activityTableBody');
    if (activityData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" class="p-4 text-center text-gray-500">No activities yet. Start logging missions!</td></tr>';
        return;
    }
    
    let html = '';
    activityData.slice().reverse().forEach(item => {
        html += `
            <tr class="border-b hover:bg-green-50">
                <td class="p-3">${item.date}</td>
                <td class="p-3">${item.action}</td>
                <td class="p-3 font-bold text-green-600">${item.points}</td>
            </tr>
        `;
    });
    tableBody.innerHTML = html;
}
