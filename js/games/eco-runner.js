/* ==========================================
   ECO-RUNNER GAME
   ========================================== */

let currentGame = null;
let gameCanvas, gameCtx;
let animationId;

function startEcoRunner() {
    document.getElementById('gameContainer').classList.remove('hidden');
    gameCanvas = document.getElementById('gameCanvas');
    gameCanvas.width = 800;
    gameCanvas.height = 400;
    gameCtx = gameCanvas.getContext('2d');
    
    currentGame = 'ecorunner';
    runEcoRunner();
}

function runEcoRunner() {
    const player = { x: 50, y: 175, width: 50, height: 50, speed: 5 };
    let carbonScore = 100;
    let items = [];
    let obstacles = [];
    let keys = {};

    window.addEventListener('keydown', (e) => { keys[e.key] = true; });
    window.addEventListener('keyup', (e) => { keys[e.key] = false; });

    function gameLoop() {
        if (currentGame !== 'ecorunner') return;

        // Player movement
        if (keys['ArrowUp'] && player.y > 0) player.y -= player.speed;
        if (keys['ArrowDown'] && player.y < 350) player.y += player.speed;

        // Spawn items
        if (Math.random() < 0.02) {
            items.push({ x: 800, y: Math.random() * 370, size: 30 });
        }
        if (Math.random() < 0.01) {
            obstacles.push({ x: 800, y: Math.random() * 360, size: 40 });
        }

        // Move and check collisions
        items = items.filter(item => {
            item.x -= 5;
            if (item.x < 0) return false;
            if (item.x < player.x + player.width && item.x + item.size > player.x &&
                item.y < player.y + player.height && item.y + item.size > player.y) {
                carbonScore = Math.max(0, carbonScore - 10);
                return false;
            }
            return true;
        });

        obstacles = obstacles.filter(obs => {
            obs.x -= 4;
            if (obs.x < 0) return false;
            if (obs.x < player.x + player.width && obs.x + obs.size > player.x &&
                obs.y < player.y + player.height && obs.y + obs.size > player.y) {
                carbonScore += 20;
                return false;
            }
            return true;
        });

        // Draw
        gameCtx.fillStyle = '#ffffff';
        gameCtx.fillRect(0, 0, 800, 400);

        // Player
        gameCtx.fillStyle = '#2196F3';
        gameCtx.fillRect(player.x, player.y, player.width, player.height);

        // Items (green circles)
        gameCtx.fillStyle = '#4CAF50';
        items.forEach(item => {
            gameCtx.beginPath();
            gameCtx.arc(item.x + item.size/2, item.y + item.size/2, item.size/2, 0, Math.PI * 2);
            gameCtx.fill();
        });

        // Obstacles (red squares)
        gameCtx.fillStyle = '#F44336';
        obstacles.forEach(obs => {
            gameCtx.fillRect(obs.x, obs.y, obs.size, obs.size);
        });

        // Score
        gameCtx.fillStyle = '#000';
        gameCtx.font = 'bold 24px Arial';
        gameCtx.fillText(`Carbon Score: ${carbonScore}`, 10, 30);

        // Win condition
        if (carbonScore <= 0) {
            gameCtx.fillStyle = '#4CAF50';
            gameCtx.fillRect(0, 0, 800, 400);
            gameCtx.fillStyle = '#fff';
            gameCtx.font = 'bold 36px Arial';
            gameCtx.fillText('YOU SAVED THE PLANET! 🎊', 150, 200);
            logActivity('Eco-Runner Victory', 50);
            ecoScore += 50;
            document.getElementById('ecoScore').textContent = ecoScore;
            setTimeout(closeGame, 3000);
            return;
        }

        animationId = requestAnimationFrame(gameLoop);
    }

    gameLoop();
}

function closeGame() {
    document.getElementById('gameContainer').classList.add('hidden');
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
    currentGame = null;
}
