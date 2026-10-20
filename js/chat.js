/* ==========================================
   AI CHAT INTERFACE
   ========================================== */

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;

    const container = document.getElementById('chatContainer');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.textContent = message;
    container.appendChild(userMsg);

    // Simulate AI response
    setTimeout(() => {
        const aiMsg = document.createElement('div');
        aiMsg.className = 'chat-message assistant';
        aiMsg.textContent = getAIResponse(message);
        container.appendChild(aiMsg);
        container.scrollTop = container.scrollHeight;
    }, 1000);

    input.value = '';
    container.scrollTop = container.scrollHeight;
}

function getAIResponse(message) {
    const responses = [
        "🌿 Great question! Recycling helps reduce waste and conserves natural resources.",
        "🌍 You can reduce your carbon footprint by using public transport and renewable energy!",
        "♻️ Did you know? Composting food waste reduces methane emissions from landfills!",
        "🌱 Planting trees is one of the best ways to combat climate change. Each tree absorbs about 48 lbs of CO₂ per year!",
        "💡 Switching to LED bulbs can save up to 75% energy compared to traditional bulbs!",
        "🚴 Biking or walking instead of driving reduces emissions and keeps you healthy!",
        "🌊 Ocean cleanup is crucial! Plastic pollution harms marine life and ecosystems.",
        "🔋 Solar panels are getting cheaper every year and can save you money while saving the planet!",
        "🌳 Urban forests help cool cities and improve air quality significantly!",
        "♻️ Remember: Reduce first, then Reuse, and finally Recycle!"
    ];
    return responses[Math.floor(Math.random() * responses.length)];
}
