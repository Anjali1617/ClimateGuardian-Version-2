/* ==========================================
   AI QUIZ GENERATOR
   ========================================== */

let selectedOption = -1;
let currentQuiz = null;
let _questionPool = [];

let QUESTIONS = null; // Will be loaded from assets/questions_sustainability.json

// Small embedded fallback in case the JSON cannot be fetched
const EMBEDDED_FALLBACK_QUESTIONS = [
    { q: "What do the '3Rs' stand for in waste management?", options: ["Reduce, Reuse, Recycle", "Restore, Return, Refine", "Reuse, Repair, Replace", "Reduce, Refuse, Recycle"], ans: 0, exp: "Reduce waste generation, reuse items, and recycle materials to minimize landfill." },
    { q: "Which of the following is a renewable energy source?", options: ["Coal", "Oil", "Solar", "Natural Gas"], ans: 2, exp: "Solar power comes from sunlight and is renewable and low-carbon." },
    { q: "What greenhouse gas is most associated with human activities?", options: ["Oxygen", "Methane (CH₄)", "Carbon Dioxide (CO₂)", "Nitrogen"], ans: 2, exp: "CO₂ from fossil fuels is the primary greenhouse gas driving climate change." }
];

async function initQuestions() {
    try {
        const resp = await fetch('assets/questions_sustainability.json');
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        QUESTIONS = await resp.json();
    } catch (e) {
        console.warn('Failed to load questions JSON, using embedded fallback:', e);
        QUESTIONS = EMBEDDED_FALLBACK_QUESTIONS;
    }
    _refillPool();
}

// start loading questions immediately
initQuestions().then(() => {
    setupQuizControlsIfPresent();
});

function setupQuizControlsIfPresent() {
    const container = document.getElementById('quizContent');
    if (!container) return;

    const controlHtml = `
        <div class="mb-3 flex gap-2">
            <select id="topicFilter" class="p-2 border rounded">
                <option value="any">Topic: Any</option>
            </select>
            <select id="difficultyFilter" class="p-2 border rounded">
                <option value="any">Difficulty: Any</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
            </select>
            <button class="btn-primary" onclick="generateQuiz()">🌱 Generate</button>
            <button class="btn-secondary" onclick="startKBC()">🎯 Start KBC</button>
        </div>
        <div id="quizPanel">
            <div class="text-center py-6">
                <img src="https://cdn-icons-png.flaticon.com/512/4148/4148323.png" class="w-28 h-28 mx-auto mb-4">
                <p class="text-gray-600">Use filters or start KBC-style challenge!</p>
            </div>
        </div>
    `;

    container.innerHTML = controlHtml;

    // populate topic filter
    const topicSelect = document.getElementById('topicFilter');
    const topics = new Set();
    (QUESTIONS || EMBEDDED_FALLBACK_QUESTIONS).forEach(q => {
        if (!q.topic) q.topic = inferTopic(q.q);
        if (!q.difficulty) q.difficulty = inferDifficulty(q.q);
        topics.add(q.topic);
    });
    topics.forEach(t => {
        const opt = document.createElement('option'); opt.value = t; opt.textContent = t.charAt(0).toUpperCase() + t.slice(1); topicSelect.appendChild(opt);
    });
}


function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

function _refillPool() {
    if (!QUESTIONS || !Array.isArray(QUESTIONS)) {
        // Questions not ready yet; leave pool empty
        _questionPool = [];
        return;
    }
    _questionPool = QUESTIONS.slice();
    shuffleArray(_questionPool);
}

function inferTopic(text) {
    const s = text.toLowerCase();
    if (s.includes('energy') || s.includes('renewable') || s.includes('solar') || s.includes('wind') || s.includes('battery')) return 'energy';
    if (s.includes('waste') || s.includes('recycle') || s.includes("3r") || s.includes('plastic')) return 'waste';
    if (s.includes('water') || s.includes('wetland') || s.includes('eutrophication')) return 'water';
    if (s.includes('biodiversity') || s.includes('species') || s.includes('forest') || s.includes('peat')) return 'biodiversity';
    if (s.includes('transport') || s.includes('vehicle') || s.includes('transport')) return 'transport';
    if (s.includes('agri') || s.includes('soil') || s.includes('crop') || s.includes('farming')) return 'agriculture';
    if (s.includes('policy') || s.includes('agreement') || s.includes('sdg') || s.includes('paris')) return 'policy';
    return 'general';
}

function inferDifficulty(text) {
    const s = text.toLowerCase();
    const hardHints = ['environmental impact assessment','eia','life cycle','lca','net-zero','pumped','peat','industrial','protocol','assessment'];
    if (hardHints.some(h => s.includes(h))) return 'hard';
    if (s.length < 80 || s.includes('what is') || s.includes("which is")) return 'easy';
    return 'medium';
}

function generateQuiz() {
    const panel = document.getElementById('quizPanel') || document.getElementById('quizContent');
    // If questions still loading, show message
    if ((!QUESTIONS || !QUESTIONS.length) && _questionPool.length === 0) {
        panel.innerHTML = `<div class="text-center py-12">Loading questions…</div>`;
        return;
    }

    // choose from filtered set if filters are present
    const topic = (document.getElementById('topicFilter') ? document.getElementById('topicFilter').value : 'any');
    const diff = (document.getElementById('difficultyFilter') ? document.getElementById('difficultyFilter').value : 'any');

    let pool = (QUESTIONS || []).filter(q => {
        let ok = true;
        if (topic && topic !== 'any') ok = ok && (q.topic === topic);
        if (diff && diff !== 'any') ok = ok && (q.difficulty === diff);
        return ok;
    });

    if (!pool || pool.length === 0) {
        panel.innerHTML = `<div class="text-center py-12">No questions found for selected filters.</div>`;
        return;
    }

    currentQuiz = pool[Math.floor(Math.random() * pool.length)];
    selectedOption = -1;

    let html = `
        <h4 class="text-xl font-bold mb-4">${currentQuiz.q}</h4>
        <div class="space-y-3">
    `;

    currentQuiz.options.forEach((opt, idx) => {
        html += `
            <div class="quiz-option" onclick="selectOption(${idx})">
                ${String.fromCharCode(65 + idx)}. ${opt}
            </div>
        `;
    });

    html += `
        </div>
        <div class="mt-6">
            <button onclick="submitQuiz()" class="btn-primary">Submit Answer</button>
            <button onclick="generateQuiz()" class="btn-secondary ml-4">Generate New Question</button>
        </div>
    `;

    panel.innerHTML = html;
}

function selectOption(idx) {
    selectedOption = idx;
    document.querySelectorAll('.quiz-option').forEach((opt, i) => {
        opt.classList.toggle('selected', i === idx);
    });
}

function submitQuiz() {
    if (selectedOption === -1) {
        alert('Please select an answer!');
        return;
    }

    if (!window.kbcMode) {
        if (selectedOption === currentQuiz.ans) {
            // Correct answer: earn 5 eco points
            ecoScore += 5;
            document.getElementById('ecoScore').textContent = ecoScore;
            logActivity('AI Quiz Win', 5);
            
            alert('🎉 Correct! +5 Eco Points\n' + currentQuiz.exp);
            setTimeout(() => {
                const panel = document.getElementById('quizPanel') || document.getElementById('quizContent');
                panel.innerHTML = `
                    <div class="text-center py-12">
                        <img src="https://cdn-icons-png.flaticon.com/512/4148/4148323.png" class="w-32 h-32 mx-auto mb-6">
                        <button onclick="generateQuiz()" class="game-button">🌱 Generate New Question</button>
                    </div>
                `;
            }, 1200);
        } else {
            // Wrong answer: deduct 2.5 eco points
            ecoScore -= 2.5;
            document.getElementById('ecoScore').textContent = ecoScore;
            logActivity('AI Quiz Wrong', -2.5);
            
            alert('❌ Oops! -2.5 Eco Points\nCorrect answer: ' + currentQuiz.options[currentQuiz.ans] + '\n\n' + currentQuiz.exp);
            setTimeout(() => {
                const panel = document.getElementById('quizPanel') || document.getElementById('quizContent');
                panel.innerHTML = `
                    <div class="text-center py-12">
                        <img src="https://cdn-icons-png.flaticon.com/512/4148/4148323.png" class="w-32 h-32 mx-auto mb-6">
                        <button onclick="generateQuiz()" class="game-button">🌱 Generate New Question</button>
                    </div>
                `;
            }, 1400);
        }
        selectedOption = -1;
        return;
    }

    // KBC flow
    if (selectedOption === currentQuiz.ans) {
        // correct answer: earn 5 eco points
        ecoScore += 5;
        document.getElementById('ecoScore').textContent = ecoScore;
        logActivity('KBC Correct', 5);
        
        window.kbcLevel = (window.kbcLevel || 1) + 1;
        renderPrizeLadder();
        if (window.kbcLevel > window.kbcMaxLevel) {
            // won KBC
            const prize = window.kbcPrizeLadder[window.kbcMaxLevel - 1];
            showNotification(`🏆 Congratulations! You won ₹${prize}! +5 Eco Points`, 'success');
            endKBC(true);
            return;
        }
        showNotification('✅ Correct! +5 Eco Points | Moving to next level.', 'success');
        setTimeout(() => nextKBCQuestion(), 1200);
    } else {
        // wrong answer: deduct 2.5 eco points
        ecoScore -= 2.5;
        document.getElementById('ecoScore').textContent = ecoScore;
        logActivity('KBC Wrong', -2.5);
        
        const guaranteed = getGuaranteedPrize();
        showNotification(`❌ Wrong! -2.5 Eco Points | You leave with ₹${guaranteed}`, 'error');
        endKBC(false);
    }
}

// KBC helpers
function startKBC() {
    if (!QUESTIONS || QUESTIONS.length === 0) {
        alert('Questions are still loading. Try again in a moment.');
        return;
    }
    window.kbcMode = true;
    window.kbcLevel = 1;
    window.kbcMaxLevel = 10;
    window.kbcPrizeLadder = [1000,2000,3000,5000,10000,20000,40000,100000,300000,1000000];
    // lifelines: track if used
    window.kbcLifelines = { '5050': false, 'skip': false, 'audience': false };
    renderPrizeLadder();
    nextKBCQuestion();
}

function endKBC(won) {
    window.kbcMode = false;
    // reset lifelines
    window.kbcLifelines = { '5050': false, 'skip': false };
    renderPrizeLadder();
    const content = document.getElementById('quizPanel') || document.getElementById('quizContent');
    let earned = 0;
    if (won) earned = window.kbcPrizeLadder[window.kbcMaxLevel - 1];
    else earned = getGuaranteedPrize();
    content.innerHTML = `
        <div class="text-center py-8">
            <h3 class="text-xl font-bold">Game Over</h3>
            <p class="mt-4">You earned ₹${earned}</p>
            <button class="btn-primary mt-6" onclick="startKBC()">Play Again</button>
            <button class="btn-secondary mt-2" onclick="generateQuiz()">Back to Quiz</button>
        </div>
    `;
}

function getGuaranteedPrize() {
    // safe levels at 5 and 8 (1-based)
    const lvl = (window.kbcLevel || 1) - 1; // last completed
    if (lvl >= 8) return window.kbcPrizeLadder[7];
    if (lvl >= 4) return window.kbcPrizeLadder[4];
    return 0;
}

function nextKBCQuestion() {
    // pick a question matching difficulty based on level
    const level = window.kbcLevel || 1;
    let diff = 'easy';
    if (level <= 4) diff = 'easy';
    else if (level <= 7) diff = 'medium';
    else diff = 'hard';

    const topicSel = document.getElementById('topicFilter');
    const topic = topicSel ? topicSel.value : 'any';
    const candidates = (QUESTIONS || []).filter(q => (q.difficulty === diff) && (topic === 'any' || q.topic === topic));
    if (!candidates || candidates.length === 0) {
        // fallback to any difficulty
        const alt = (QUESTIONS || []).filter(q => (topic === 'any' || q.topic === topic));
        if (!alt || alt.length === 0) {
            const panel = document.getElementById('quizPanel') || document.getElementById('quizContent');
            panel.innerHTML = `<div class="text-center py-12">No questions available for KBC with current filters.</div>`;
            return;
        }
        currentQuiz = alt[Math.floor(Math.random() * alt.length)];
    } else {
        currentQuiz = candidates[Math.floor(Math.random() * candidates.length)];
    }
    // display question in quizPanel with lifeline buttons
    const panel = document.getElementById('quizPanel') || document.getElementById('quizContent');
    let html = `<div class="mb-3 flex gap-2">`;
    html += `<button id="lifeline-5050" class="lifeline-btn" onclick="use5050()">50:50</button>`;
    html += `<button id="lifeline-audience" class="lifeline-btn" onclick="useAudience()">🎤 Ask Audience</button>`;
    html += `<button id="lifeline-skip" class="lifeline-btn" onclick="useSkip()">⏭ Skip</button>`;
    html += `</div>`;

    html += `<h4 class="text-xl font-bold mb-4">Level ${window.kbcLevel}: ${currentQuiz.q}</h4>`;
    html += `<div class="space-y-3">`;
    currentQuiz.options.forEach((opt, idx) => {
        html += `<div class="quiz-option" id="opt-${idx}" onclick="selectOption(${idx})">${String.fromCharCode(65 + idx)}. ${opt}</div>`;
    });
    html += '</div><div class="mt-6 flex gap-2"><button class="btn-primary" onclick="submitQuiz()">Submit</button><button class="btn-secondary" onclick="walkAway()">Walk Away</button></div>';
    panel.innerHTML = html;

    // set disabled/used states for lifeline buttons
    const lf = document.getElementById('lifeline-5050'); if (lf) lf.classList.toggle('used', window.kbcLifelines['5050']);
    const la = document.getElementById('lifeline-audience'); if (la) la.classList.toggle('used', window.kbcLifelines['audience']);
    const ls = document.getElementById('lifeline-skip'); if (ls) ls.classList.toggle('used', window.kbcLifelines['skip']);
}

function renderPrizeLadder() {
    // small ladder in quizPanel area (top-right not always available in this UI)
    const panel = document.getElementById('quizPanel') || document.getElementById('quizContent');
    const ladder = window.kbcPrizeLadder || [1000,2000,3000,5000,10000,20000,40000,100000,300000,1000000];
    const cur = window.kbcLevel || 1;
    // build ladder HTML with proper classes
    const ladderHtml = `<div class="mt-4 p-3 bg-white rounded shadow-sm"><h4 class="font-semibold mb-2">KBC Ladder</h4>` + ladder.map((amt, i) => `<div class="p-1 ${i+1 === cur ? 'kbc-current' : ''}">Level ${i+1}: ₹${amt}</div>`).reverse().join('') + `</div>`;
    // try to put next to content: if quizContent parent has a sibling, insert, else append
    const contentParent = document.getElementById('quizContent');
    if (contentParent && contentParent.parentElement) {
        const sidebar = contentParent.parentElement.querySelector('.kbc-sidebar');
        // remove existing
        if (sidebar) sidebar.remove();
        const div = document.createElement('div'); div.className = 'kbc-sidebar'; div.innerHTML = ladderHtml;
        contentParent.parentElement.appendChild(div);
        // add a subtle pulse to the current level to draw attention
        const curEl = div.querySelector('.kbc-current');
        if (curEl) {
            curEl.classList.add('pulse');
            setTimeout(() => curEl.classList.remove('pulse'), 2200);
        }
    } else {
        // fallback: append inside panel
        panel.innerHTML = (panel.innerHTML || '') + ladderHtml;
    }
}

function use5050() {
    if (!window.kbcMode || window.kbcLifelines['5050']) return;
    window.kbcLifelines['5050'] = true;
    const btn = document.getElementById('lifeline-5050'); if (btn) btn.classList.add('used');
    const correct = currentQuiz.ans;
    const wrongIdxs = currentQuiz.options.map((o, i) => i).filter(i => i !== correct);
    shuffleArray(wrongIdxs);
    const toHide = wrongIdxs.slice(0, 2);
    toHide.forEach(i => {
        const el = document.getElementById('opt-' + i);
        if (el) el.style.visibility = 'hidden';
    });
}

function useSkip() {
    if (!window.kbcMode || window.kbcLifelines['skip']) return;
    window.kbcLifelines['skip'] = true;
    const btn = document.getElementById('lifeline-skip'); if (btn) btn.classList.add('used');
    showNotification('⏭ Skipped question, moving to next.', 'info');
    nextKBCQuestion();
}

function useAudience() {
    if (!window.kbcMode || window.kbcLifelines['audience']) return;
    window.kbcLifelines['audience'] = true;
    const btn = document.getElementById('lifeline-audience'); if (btn) btn.classList.add('used');

    // compute distribution
    const visibleOptions = []; // options not hidden by 50:50
    currentQuiz.options.forEach((o, i) => {
        const el = document.getElementById('opt-' + i);
        if (!el || el.style.visibility !== 'hidden') visibleOptions.push(i);
    });
    // difficulty bias
    const diff = currentQuiz.difficulty || inferDifficulty(currentQuiz.q);
    let baseCorrect = 50;
    if (diff === 'easy') baseCorrect = 72;
    else if (diff === 'medium') baseCorrect = 55;
    else baseCorrect = 42;

    // if 50:50 used and only two options remain, increase confidence
    if (visibleOptions.length === 2) baseCorrect += 12;

    // allocate percentages
    const correctIdx = currentQuiz.ans;
    const percentages = {};
    let remaining = 100;
    // assign to correct if visible
    if (visibleOptions.includes(correctIdx)) {
        const variance = Math.floor((Math.random() * 11) - 5); // -5..+5
        const assigned = Math.max(30, Math.min(95, baseCorrect + variance));
        percentages[correctIdx] = assigned;
        remaining -= assigned;
    }
    // distribute remaining to other visible options randomly
    const others = visibleOptions.filter(i => i !== correctIdx);
    shuffleArray(others);
    for (let i = 0; i < others.length; i++) {
        if (i === others.length - 1) percentages[others[i]] = remaining;
        else {
            const take = Math.max(0, Math.floor(Math.random() * (remaining - (others.length - i - 1))));
            percentages[others[i]] = take;
            remaining -= take;
        }
    }
    // if correct wasn't visible, just split evenly
    if (!visibleOptions.includes(correctIdx)) {
        const per = Math.floor(100 / visibleOptions.length);
        visibleOptions.forEach((i, idx) => percentages[i] = idx === visibleOptions.length - 1 ? 100 - per * (visibleOptions.length - 1) : per);
    }

    // render modal
    const modal = document.createElement('div'); modal.className = 'audience-modal'; modal.id = 'audienceModal';
    let inner = `<h4>Audience Poll</h4><div class="audience-bars">`;
    ['A','B','C','D'].forEach((label, idx) => {
        if (!currentQuiz.options[idx]) return;
        const pct = percentages[idx] || 0;
        inner += `<div class="audience-bar"><div class="label">${label}</div><div class="bar"><i style="width:${pct}%"></i></div><div class="label">${pct}%</div></div>`;
    });
    inner += `</div><div class="audience-note">Audience poll is a simulated hint, not a guarantee.</div><div style="text-align:right;margin-top:10px;"><button class="btn-secondary" onclick="closeAudience()">Close</button></div>`;
    modal.innerHTML = inner;
    document.body.appendChild(modal);
}

function closeAudience() {
    const m = document.getElementById('audienceModal'); if (m) m.remove();
}

function walkAway() {
    const prize = getGuaranteedPrize();
    showNotification(`🏃 You walked away with ₹${prize}`, 'info');
    endKBC(true);
}
