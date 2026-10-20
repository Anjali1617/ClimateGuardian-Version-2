/* ==========================================
   RENEWABLE ENERGY PUZZLE GAME
   ========================================== */

function startRenewableEnergy() {
    document.getElementById('gameContainer').classList.remove('hidden');
    gameCanvas = document.getElementById('gameCanvas');
    gameCanvas.width = 600;
    gameCanvas.height = 600;
    gameCtx = gameCanvas.getContext('2d');
    
    currentGame = 'renewable';
    runRenewableEnergy();
}

function runRenewableEnergy() {
    const GRID_SIZE = 5;
    const CELL = 80;
    const GRID_OFFSET_Y = 150;

    let mapGrid = [
        [0, 1, 0, 1, 0],
        [2, 0, 2, 0, 2],
        [0, 3, 0, 3, 0],
        [2, 0, 2, 0, 2],
        [0, 1, 0, 1, 0]
    ];

    let selected = null;
    let emissions = 500;
    let correctPlacements = 0;
    let wrongPlacements = 0;
    let gameOver = false;
    let particles = [];

    const buttons = [
        { x: 50, y: 70, w: 140, h: 60, color: '#FFC107', hoverColor: '#FFD54F', text: '☀️ SOLAR', value: 1 },
        { x: 220, y: 70, w: 140, h: 60, color: '#2196F3', hoverColor: '#64B5F6', text: '💨 WIND', value: 2 },
        { x: 390, y: 70, w: 140, h: 60, color: '#00BCD4', hoverColor: '#4DD0E1', text: '💧 HYDRO', value: 3 }
    ];

    // Particle class for visual effects
    class Particle {
        constructor(x, y, color) {
            this.x = x;
            this.y = y;
            this.color = color;
            this.size = 10;
            this.lifetime = 30;
            this.velocityY = -2;
        }
        
        update() {
            this.y += this.velocityY;
            this.lifetime -= 1;
            this.size = Math.max(0, this.size - 0.3);
        }
        
        draw(ctx) {
            if (this.size > 0) {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // Remove any existing click listeners
    const newCanvas = gameCanvas.cloneNode(true);
    gameCanvas.parentNode.replaceChild(newCanvas, gameCanvas);
    gameCanvas = newCanvas;
    gameCtx = gameCanvas.getContext('2d');
    gameCanvas.width = 600;
    gameCanvas.height = 600;

    function handleClick(e) {
        if (gameOver) return;
        
        const rect = gameCanvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Check button clicks
        buttons.forEach(btn => {
            if (x >= btn.x && x <= btn.x + btn.w && y >= btn.y && y <= btn.y + btn.h) {
                selected = btn.value;
            }
        });

        // Check grid clicks
        const gridX = Math.floor((x - 100) / CELL);
        const gridY = Math.floor((y - GRID_OFFSET_Y) / CELL);

        if (gridX >= 0 && gridX < GRID_SIZE && gridY >= 0 && gridY < GRID_SIZE && selected) {
            if (mapGrid[gridY][gridX] === selected) {
                emissions -= 50;
                correctPlacements++;
                mapGrid[gridY][gridX] = 0;
                
                // Add green particles for correct placement
                for (let i = 0; i < 10; i++) {
                    particles.push(new Particle(
                        100 + gridX * CELL + CELL / 2 + (Math.random() - 0.5) * 20,
                        GRID_OFFSET_Y + gridY * CELL + CELL / 2 + (Math.random() - 0.5) * 20,
                        '#4CAF50'
                    ));
                }
            } else if (mapGrid[gridY][gridX] !== 0) {
                emissions += 30;
                wrongPlacements++;
                
                // Add red particles for wrong placement
                for (let i = 0; i < 5; i++) {
                    particles.push(new Particle(
                        100 + gridX * CELL + CELL / 2 + (Math.random() - 0.5) * 20,
                        GRID_OFFSET_Y + gridY * CELL + CELL / 2 + (Math.random() - 0.5) * 20,
                        '#F44336'
                    ));
                }
            }
        }
    }

    gameCanvas.addEventListener('click', handleClick);

    function drawGame() {
        if (currentGame !== 'renewable') {
            gameCanvas.removeEventListener('click', handleClick);
            return;
        }

        // Update particles
        particles = particles.filter(p => {
            p.update();
            return p.lifetime > 0;
        });

        // Gradient background
        const gradient = gameCtx.createLinearGradient(0, 0, 0, 600);
        gradient.addColorStop(0, '#87CEEB');
        gradient.addColorStop(1, '#E0F7FA');
        gameCtx.fillStyle = gradient;
        gameCtx.fillRect(0, 0, 600, 600);

        // Title with shadow
        gameCtx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        gameCtx.shadowBlur = 5;
        gameCtx.shadowOffsetX = 2;
        gameCtx.shadowOffsetY = 2;
        gameCtx.fillStyle = '#006400';
        gameCtx.font = 'bold 32px Arial';
        gameCtx.fillText('🌍 Save The Planet!', 120, 40);
        gameCtx.shadowBlur = 0;
        gameCtx.shadowOffsetX = 0;
        gameCtx.shadowOffsetY = 0;

        // Buttons with hover effect
        buttons.forEach(btn => {
            // Draw button shadow
            gameCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            gameCtx.beginPath();
            roundRect(gameCtx, btn.x + 3, btn.y + 3, btn.w, btn.h, 10);
            gameCtx.fill();
            
            // Draw button
            gameCtx.fillStyle = btn.value === selected ? '#fff' : btn.color;
            gameCtx.beginPath();
            roundRect(gameCtx, btn.x, btn.y, btn.w, btn.h, 10);
            gameCtx.fill();
            
            // Draw border
            gameCtx.strokeStyle = btn.value === selected ? '#000' : '#333';
            gameCtx.lineWidth = btn.value === selected ? 4 : 3;
            gameCtx.stroke();
            
            // Draw text
            gameCtx.fillStyle = btn.value === selected ? btn.color : '#fff';
            gameCtx.font = 'bold 18px Arial';
            gameCtx.fillText(btn.text, btn.x + 20, btn.y + 38);
        });

        // Instructions
        gameCtx.fillStyle = '#333';
        gameCtx.font = '16px Arial';
        if (selected === null) {
            gameCtx.fillText('👆 Select an energy source above!', 170, 135);
        } else {
            gameCtx.fillText('👇 Click matching colored tiles below!', 160, 135);
        }

        // Grid with shadow
        gameCtx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        gameCtx.fillRect(105, GRID_OFFSET_Y + 5, GRID_SIZE * CELL, GRID_SIZE * CELL);

        for (let row = 0; row < GRID_SIZE; row++) {
            for (let col = 0; col < GRID_SIZE; col++) {
                let color = '#f0f0f0';
                let icon = '';

                if (mapGrid[row][col] === 1) {
                    color = '#FFEB3B';
                    icon = '☀️';
                } else if (mapGrid[row][col] === 2) {
                    color = '#2196F3';
                    icon = '💨';
                } else if (mapGrid[row][col] === 3) {
                    color = '#00BCD4';
                    icon = '💧';
                }

                const cellX = 100 + col * CELL;
                const cellY = GRID_OFFSET_Y + row * CELL;

                gameCtx.fillStyle = color;
                gameCtx.beginPath();
                roundRect(gameCtx, cellX, cellY, CELL, CELL, 5);
                gameCtx.fill();
                
                gameCtx.strokeStyle = '#505050';
                gameCtx.lineWidth = 2;
                gameCtx.stroke();

                if (icon) {
                    gameCtx.font = '32px Arial';
                    gameCtx.fillText(icon, cellX + 24, cellY + 50);
                }
            }
        }

        // Draw particles
        particles.forEach(p => p.draw(gameCtx));

        // Stats Panel
        const statsY = GRID_OFFSET_Y + GRID_SIZE * CELL + 20;
        
        // Bar background
        gameCtx.fillStyle = '#c8c8c8';
        gameCtx.beginPath();
        roundRect(gameCtx, 50, statsY, 500, 30, 15);
        gameCtx.fill();

        // Bar fill
        const emissionsWidth = Math.max(0, (emissions / 500) * 500);
        const barColor = emissions <= 100 ? '#4CAF50' : emissions <= 300 ? '#FFA500' : '#F44336';
        gameCtx.fillStyle = barColor;
        gameCtx.beginPath();
        roundRect(gameCtx, 50, statsY, emissionsWidth, 30, 15);
        gameCtx.fill();

        // Bar text
        gameCtx.fillStyle = '#000';
        gameCtx.font = 'bold 16px Arial';
        gameCtx.fillText(`💨 Emissions: ${emissions} tons CO2`, 180, statsY + 20);

        // Score
        gameCtx.fillStyle = '#333';
        gameCtx.fillText(`✅ Correct: ${correctPlacements}  ❌ Wrong: ${wrongPlacements}`, 150, statsY + 55);

        // Win condition
        if (emissions <= 0 && !gameOver) {
            gameOver = true;
            
            // Overlay
            gameCtx.fillStyle = 'rgba(0, 150, 0, 0.95)';
            gameCtx.fillRect(0, 0, 600, 600);
            
            gameCtx.fillStyle = '#fff';
            gameCtx.font = 'bold 40px Arial';
            gameCtx.shadowColor = 'rgba(0, 0, 0, 0.5)';
            gameCtx.shadowBlur = 10;
            gameCtx.fillText('🎉 NET-ZERO ACHIEVED! 🎉', 50, 280);
            
            gameCtx.font = 'bold 24px Arial';
            const finalScore = correctPlacements * 100 - wrongPlacements * 30;
            gameCtx.fillText(`Final Score: ${finalScore} points`, 160, 330);
            gameCtx.fillText(`Perfect Matches: ${correctPlacements}`, 160, 370);
            
            gameCtx.shadowBlur = 0;
            
            logActivity('Renewable Energy Victory', correctPlacements * 10);
            ecoScore += correctPlacements * 10;
            document.getElementById('ecoScore').textContent = ecoScore;
            
            setTimeout(() => {
                gameCanvas.removeEventListener('click', handleClick);
                closeGame();
            }, 5000);
            return;
        }

        animationId = requestAnimationFrame(drawGame);
    }

    // Helper function for rounded rectangles
    function roundRect(ctx, x, y, w, h, r) {
        if (w < 2 * r) r = w / 2;
        if (h < 2 * r) r = h / 2;
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.arcTo(x + w, y, x + w, y + h, r);
        ctx.arcTo(x + w, y + h, x, y + h, r);
        ctx.arcTo(x, y + h, x, y, r);
        ctx.arcTo(x, y, x + w, y, r);
        ctx.closePath();
        return ctx;
    }

    drawGame();
}
