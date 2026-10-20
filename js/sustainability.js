/* ==========================================
   SUSTAINABILITY PREDICTOR
   ========================================== */

function calculateImpact() {
    const transport = parseInt(document.getElementById('transport').value);
    const diet = parseInt(document.getElementById('diet').value);
    const energy = parseInt(document.getElementById('energy').value);
    
    const change = transport + diet + energy;
    carbonLevel += change;
    carbonLevel = Math.max(0, Math.min(200, carbonLevel));
    
    document.getElementById('carbonLevel').textContent = carbonLevel;
    
    const percentage = Math.min(100, (carbonLevel / 200) * 100);
    const progressBar = document.getElementById('carbonProgress');
    progressBar.style.width = percentage + '%';
    progressBar.textContent = Math.round(percentage) + '%';
    
    let status = '';
    let color = '';
    let message = '';
    
    if (carbonLevel <= 50) {
        status = '🌟 Eco Hero!';
        color = '#4CAF50';
        message = '🎉 Amazing! You\'re making excellent sustainable choices!';
        if (change < 0) {
            logActivity('Carbon Reduction', Math.abs(change) * 2);
        }
    } else if (carbonLevel <= 100) {
        status = '👍 Good Job!';
        color = '#FFC107';
        message = '👏 You\'re on the right track! Keep making green choices!';
    } else {
        status = '🔥 Need Improvement';
        color = '#F44336';
        message = '⚠️ Try choosing more eco-friendly options to reduce your impact!';
    }
    
    progressBar.style.background = color;
    document.getElementById('carbonStatus').textContent = status;
    document.getElementById('impactResult').innerHTML = `
        <p class="text-lg font-bold mb-2">${status}</p>
        <p class="text-gray-700">${message}</p>
        <p class="mt-3 text-sm">Carbon change: <strong>${change > 0 ? '+' : ''}${change} CO₂</strong></p>
    `;
}

function resetCarbon() {
    carbonLevel = 100;
    document.getElementById('carbonLevel').textContent = carbonLevel;
    document.getElementById('carbonProgress').style.width = '50%';
    document.getElementById('carbonProgress').textContent = '50%';
    document.getElementById('carbonStatus').textContent = 'CO₂ Units';
    document.getElementById('carbonProgress').style.background = 'linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%)';
    document.getElementById('impactResult').innerHTML = '<p class="text-gray-600">Make your daily choices above and calculate your impact!</p>';
}
