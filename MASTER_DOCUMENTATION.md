# 🌍 Climate Guardian: A Gamified Sustainability Awareness - Master Documentation
**Version 3.1 | Current Project State | Last Updated: September 26, 2026**

---

## 📑 Table of Contents
1. [Project Overview](#project-overview)
2. [Installation Guide](#installation-guide)
3. [Feature Documentation](#feature-documentation)
4. [Current Game Portfolio](#current-game-portfolio)
5. [Quiz and AI Features](#quiz-and-ai-features)
6. [Mission and Verification System](#mission-and-verification-system)
7. [Administration & Dashboard](#administration--dashboard)
8. [Troubleshooting](#troubleshooting)
9. [Technical Specifications](#technical-specifications)
10. [Latest Updates & Changes](#latest-updates--changes)
11. [Certificate System Guide](#certificate-system-guide)

---

# Project Overview

## What is Climate Guardian?

**Climate Guardian: A Gamified Sustainability Awareness** is a comprehensive sustainability education platform built with Python Streamlit and Pygame. It features AI-powered learning tools, interactive games, user authentication, and real-time environmental impact tracking.

### Key Features

#### 🔐 Authentication System
- Secure user registration with email validation
- SHA-256 encrypted password protection
- Personal user profiles with eco-score tracking
- Session management
- CSV-based user database

#### 🤖 AI-Powered Learning
- **Floating AI Chat** - A floating "Ask Me" button opens a Gemini-powered sustainability chatbot.
- **AI Quiz** - Dynamic question generation now integrated as a playable game.
- **Real-time feedback** and explanations
- Eco points system (+5 for correct, -2.5 for wrong)

#### 📊 Interactive Features
- **Mission Tracker** - Log daily eco-friendly actions
- **Carbon Calculator** - Predict sustainability impact
- **Admin Dashboard** - Track collective progress
- **Points System** - Gamified learning experience

#### 🎮 Four Playable Games
- 🏃 **Eco-Runner** - Action game collecting leaves (50 points)
- ⚡ **Renewable Energy Puzzle** - Strategy game (50 points)
- ♻️ **Smart Waste Segregation** - AI-powered hand gesture game (75 points)
- 🧠 **Quiz Game** - KBC-style sustainability challenge.

---

# Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

## Step 1: Download/Clone the Project

**Option A: With Git**
```bash
git clone <your-repository-url>
cd climate-guardian
```

**Option B: Manual Download**
1. Download project as ZIP file
2. Extract to a folder
3. Open Terminal in that folder

## Step 2: Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Required Packages

```bash
pip install -r requirements.txt
```

**Installed Packages:**
- streamlit==1.32.0 (web framework)
- pandas==2.2.0 (data handling)
- plotly==5.19.0 (charts)
- google-generativeai==0.3.2 (AI chatbot)
- groq==1.0.0 (AI verification)
- Pillow==10.2.0 (image handling)
- pygame==2.5.2 (games)
- opencv-python==4.9.0.80 (camera & computer vision)
- mediapipe==0.10.9 (hand tracking)
- numpy==1.26.3 (computation)
reportlab==4.0.9 (PDF generation)

## Step 4: Configure API Keys

Create/edit `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
GROQ_API_KEY = "your-groq-api-key-here"
```

**Get API Keys:**
- **Gemini:** https://makersuite.google.com/app/apikey
- **Groq:** https://console.groq.com

## Step 5: Run the Application

```bash
streamlit run app.py
```

App will open at `http://localhost:8501`

## First Time Setup - Create Your Account

1. Click **"📝 Sign Up"**
2. Fill in registration form:
   - Full Name
   - Email Address
   - Username (unique)
   - Password (min 6 characters)
   - Confirm Password
3. Check **"I agree to help save the planet! 🌍"**
4. Click **"🌟 Create Account"**
5. Login with your credentials

---

# Feature Documentation

## 🤖 AI Chat Features

**Function:** Interactive chatbot powered by Google Gemini for sustainability questions

**How to Use:**
1. Navigate to **"Chat"** tab
2. Type your question (e.g., "How can I reduce plastic waste?")
3. Click **"Send"** or press Enter
4. Get instant AI-powered response

**Example Questions:**
- How does carbon footprint affect climate change?
- What are the benefits of renewable energy?
- How can I reduce my daily waste?
- Tell me about sustainable living practices

## 🎮 AI Quiz System

**Points System:**
| Answer Type | Points |
|------------|--------|
| Correct Answer | +5 |
| Wrong Answer | -2.5 |

**Quiz Modes:**

### Regular Quiz
1. Click **"🌱 Generate New Question"**
2. Read the multiple-choice question
3. Select an option (A, B, C, or D)
4. Click **"Submit Answer"**
5. See result with +5 or -2.5 points

### KBC Mode (Multi-Level Challenge)
1. Start with **"📺 Take KBC Challenge"**
2. Answer 10 questions progressively
3. Each correct: +5 points + level advance
4. Each wrong: -2.5 points + game ends
5. Message shows total eco points earned

**Quiz Topics:**
- Environmental Science
- Recycling Methods
- Renewable Energy
- Climate Change
- Sustainability Practices

## ✅ Mission Tracker

**Available Missions:**
| Mission | Points | Description |
|---------|--------|-------------|
| Recycled Plastic | 5 | Log a recycling event |
| Planted a Tree | 50 | Photo verification required |
| Walked/Biked to School | 20 | Video verification required |
| Saved Electricity | 10 | Describe action taken |
| Used Reusable Bag | 5 | Log item usage |
| Composted Food | 15 | Document composting |

**How to Log Mission:**
1. Go to **"✅ Missions"** tab
2. Select mission from dropdown
3. Complete required actions
4. Click **"✅ Log Mission"** or **"Verify & Log"**
5. Receive eco-points immediately

## 🔮 Carbon Calculator

**Function:** Predict sustainability impact based on daily choices

**How to Use:**
1. Navigate to **"🔮 Predict Sustainability"** tab
2. Answer multiple choice questions about:
   - Transportation (car, bus, bike, walk)
   - Diet (meat, vegetarian, vegan)
   - Energy (high usage, moderate, low)
   - Shopping (frequent, moderate, minimal)
3. Click **"📊 Calculate Impact"**
4. View carbon level change (visual indicator)
5. Get color-coded feedback:
   - 🟢 Green = Low carbon (Good!)
   - 🟡 Yellow = Medium carbon
   - 🔴 Red = High carbon (Needs work)

## 📊 Admin Dashboard

**Features:**

#### Metrics Display
- **Total Eco-Points Earned** - School-wide total
- **Number of Actions** - Total logged activities
- **Trees Planted Count** - Environmental impact tracking
- **Activity Distribution** - Pie chart showing mission breakdown
- **Top Activities** - Bar chart of most popular missions

#### Data Visualization
- **Interactive Plotly Charts** - Hover for details
- **Real-time Updates** - Refreshes on page load
- **Historical Tracking** - View trends over time
- **Export Capabilities** - Data can be downloaded

---

# Games Guide

## 🏃 Game 1: Eco-Runner

**Story:** You are an environmental hero collecting fallen leaves while avoiding garbage to reduce carbon emissions.

**Objective:** Reduce carbon score from 100 to 0

**Controls:**
- **↑** (Up Arrow) - Move person up
- **↓** (Down Arrow) - Move person down

**Scoring:**
- 🍃 **Collect Leaf:** -10 CO₂ (Reduces carbon)
- 🗑️ **Hit Garbage:** +20 CO₂ (Increases carbon)
- **Win Condition:** Carbon score = 0
- **Points Awarded:** 50 points

**Visual Elements:**
- Sky: Light blue gradient background
- Ground: Green grass at bottom
- Player: Animated person with head, body, arms, legs
- Collectibles: Green leaves with veins
- Obstacles: Gray garbage cans with red waste

**Strategy Tips:**
1. Focus on collecting leaves first
2. Avoid all garbage items
3. Use full vertical space to dodge
4. Keep eye on carbon score
5. Precision is key - don't rush

---

## ⚡ Game 2: Renewable Energy Puzzle

**Story:** Place renewable energy sources on correct tiles to reduce global emissions and achieve net-zero.

**Objective:** Reduce emissions from 500 tons to 0

**Controls:**
- **Mouse Click** - Select energy source button
- **Mouse Click** - Click grid tile to place

**Energy Type Matching:**
| Energy | Color | Tile Color | Symbol |
|--------|-------|------------|--------|
| Solar | Yellow | Yellow | ☀️ |
| Wind | Blue | Blue | 💨 |
| Hydro | Cyan | Light Blue | 💧 |

**Scoring:**
- ✅ **Correct Match:** -50 tons CO₂
- ❌ **Wrong Match:** +30 tons CO₂
- **Win Condition:** Emissions = 0
- **Points Awarded:** 50 points

**Strategy Tips:**
1. Look carefully at tile colors before clicking
2. Remember the pattern:
   - ☀️ Solar = Yellow tiles
   - 💨 Wind = Blue tiles
   - 💧 Hydro = Cyan tiles
3. Plan ahead to minimize wrong placements
4. Check visual feedback (selected button has white border)
5. Take your time - accuracy over speed

---

## ♻️ Game 3: Smart Waste Segregation

**Story:** Falling waste items need to be sorted into correct recycling bins using AI-powered hand gestures.

**Objective:** Sort waste correctly before 5 misses

**Setup:**
1. Click **"🎮 Launch Waste Segregation"**
2. Allow camera access
3. Check **"🚀 Start Camera"**
4. Position hand so camera can see it

**Controls:**
- **Show Hand** - Display hand to camera
- **Pinch** - Touch index finger + thumb to grab items
- **Drag** - Move hand while pinching to drag item
- **Release** - Open fingers to drop into bin
- **SPACE** - Start game
- **P** - Pause game
- **Q** - Quit game

**Bin Categories:**
| Bin Color | Waste Type | Examples |
|-----------|-----------|----------|
| 🔵 Blue | Plastic | Bottles, bags, cups |
| 🟡 Yellow | Paper | Newspaper, cardboard, magazines |
| 🔴 Red | Metal | Cans, foil, tins |
| 🟢 Green | Organic | Food waste, leaves, compost |

**Scoring:**
- ✅ **Correct Bin:** +10 points
- ❌ **Wrong Bin:** -5 points
- 💔 **Missed Item:** Counts toward game over (5 max)
- **Win Condition:** High score before 5 misses
- **Points Awarded:** 75 + final score

**Gameplay Mechanics:**
- Items spawn every ~2 seconds
- Items fall at constant speed
- Hand tracking uses AI (MediaPipe)
- Game levels up every 50 points
- Faster spawn rate at higher levels
- Game over after 5 misses

**Strategy Tips:**
1. **Lighting is Key** - Ensure well-lit room
2. **Read the Label** - Each item shows its type
3. **Color Association:**
   - Plastic = Blue (like water bottles)
   - Paper = Yellow (like notepad)
   - Metal = Red (like cans)
   - Organic = Green (like plants)
4. **Prioritize Accuracy** - Over speed
5. **Grab Items Early** - Don't wait until last second
6. **Drop Precisely** - Aim center of bin

**Educational Value:**
Learn the **4 Rs of Waste Management:**
1. **Reduce** - Use less
2. **Reuse** - Use again
3. **Recycle** - Process for new use
4. **Recover** - Extract energy/materials

---

# Quiz System

## Quiz Eco Points System

**Implementation:** Students earn +5 eco points for correct answers and lose -2.5 eco points for wrong answers.

**Point Distribution:**
| Quiz Type | Correct | Wrong | Ratio |
|-----------|---------|-------|-------|
| Regular | +5 | -2.5 | 2:1 |
| KBC Mode | +5 | -2.5 | 2:1 |

**Example Score Progression:**
```
Starting: 100 points
Q1 ✅ Correct:  100 + 5 = 105
Q2 ❌ Wrong:    105 - 2.5 = 102.5
Q3 ✅ Correct:  102.5 + 5 = 107.5
Q4 ✅ Correct:  107.5 + 5 = 112.5
Q5 ❌ Wrong:    112.5 - 2.5 = 110
Final Score: 110 points
```

**Database Persistence:**
- Frontend: Maintains `totalScore` in browser session
- Backend: Uses `log_action()` to save to database
- Storage: users_database.csv via `auth.update_user_score()`
- Persistence: Scores saved after each session

---

# Walked Mission Implementation

## Video Verification System

**Feature:** Video proof verification for "Walked/Biked to School" mission using Groq API.

### How It Works

**Step 1: Video Upload**
- User uploads video (MP4, WebM, MOV, AVI)
- Video preview displays automatically
- System shows video requirements

**Step 2: Frame Extraction**
- OpenCV extracts 3 key frames:
  - Frame 1: 25% through video
  - Frame 2: 50% through video (middle)
  - Frame 3: 75% through video
- Frames resized to 512x512 pixels
- Converted to Base64 for API transmission

**Step 3: AI Analysis**
- Model: openai/gpt-oss-120b
- Analyzes for:
  - **Authenticity** - Real vs. AI-generated detection
  - **Activity Detection** - Walking/Biking confirmation
  - **Environment Verification** - Outdoor vs. indoor
  - **Motion Analysis** - Frame progression consistency

**Step 4: Response Processing**
```
VERIFIED|Description|Activity_Type|Energy_Estimate
or
REJECTED|Reason for rejection
```

**Step 5: Points Award**
- Success: +20 Eco-Points (highest mission value)
- Failure: No points, user can retry
- Balloons animation on success

### User Flow

1. Go to **"✅ Missions"** tab
2. Select **"Walked/Biked to School"** from dropdown
3. Upload a 15-60 second video
4. Click **"🔍 Verify Video & Log Mission"**
5. AI analyzes (15-30 seconds)
6. Get **+20 points** if verified! 🎉

### Video Requirements

- ✅ Show yourself walking or biking
- ✅ Include outdoor landmarks/surroundings
- ✅ Use natural lighting
- ✅ Duration: 15-60 seconds
- ✅ Format: MP4, WebM, MOV, AVI

### AI Detection Features

**Authenticity Verification:**
- Natural motion blur detection
- Realistic lighting analysis
- Video artifact identification
- Deepfake detection

**Activity Recognition:**
- Body posture analysis
- Leg movement detection
- Bicycle/bike identification
- Motion consistency check

**Environment Validation:**
- Sky and cloud detection (outdoors)
- Building and structure recognition
- Road and path identification
- Vehicle detection (for context)

---

# Administration & Dashboard

## Accessing the Admin Dashboard

1. Login to Streamlit app
2. Go to **"📊 Dashboard"** tab
3. View all metrics and charts

## Dashboard Metrics

### Key Numbers
- **Total Eco-Points:** Sum of all student eco-points
- **Total Actions:** Count of all logged missions
- **Trees Planted:** Environmental impact count

### Visual Charts
- **Activity Distribution** (Pie Chart)
  - Shows breakdown of mission types
  - Hover for percentages
  - Click legend to filter

- **Top Activities** (Bar Chart)
  - Most popular missions
  - Frequency of participation
  - Contribution to total points

---

# Troubleshooting

## General Issues

### Python Not Found
```bash
# Windows - Add Python to PATH
# Control Panel → System → Advanced Settings → Environment Variables
# Add Python installation directory to PATH

# macOS/Linux
which python3
```

### Virtual Environment Issues
```bash
# Windows - Activate fails
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate

# macOS/Linux - Permission denied
chmod +x venv/bin/activate
source venv/bin/activate
```

### Port 8501 Already in Use
```bash
streamlit run app.py --server.port 8502
```

### API Key Errors
1. Check `.streamlit/secrets.toml` exists
2. Verify API key format (no extra spaces/quotes)
3. Validate key at API provider website
4. Restart Streamlit app

### Games Not Launching
```bash
# Test Pygame installation
python -c "import pygame; print(pygame.ver)"

# Test OpenCV installation
python -c "import cv2; print(cv2.__version__)"

# Run games directly
cd games
python eco_runner.py
```

### Camera/Hand Tracking Issues

**Camera Not Working:**
1. Close other camera-using apps
2. Grant browser permissions
3. Check camera drivers updated
4. Try restarting computer

**Hand Not Detected:**
1. Improve lighting (face window/lamp)
2. Keep hand fully visible
3. Position at arm's length from camera
4. Try different hand positions
5. Clean camera lens

**Pinch Not Working:**
1. Touch index + thumb firmly
2. Hold for 1 second
3. Ensure both fingers visible
4. Try different lighting
5. Adjust `PINCH_THRESHOLD` in code (default: 40)

---

# Technical Specifications

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2.0 GHz | 2.5 GHz quad-core |
| **RAM** | 4 GB | 8 GB+ |
| **Storage** | 500 MB | 1 GB |
| **OS** | Windows 10, macOS 10.15, Ubuntu 18.04 | Latest versions |
| **Python** | 3.8 | 3.10+ |
| **Browser** | Any modern | Chrome/Firefox |
| **Camera** | Optional | 720p+ for games |

## Software Stack

```
Frontend Framework:      Streamlit
Backend Language:        Python 3.8+
Game Engine:            Pygame
AI/ML:                  Google Gemini, Groq API
Computer Vision:        OpenCV, TensorFlow
Hand Tracking:          MediaPipe
Data Storage:           CSV
Authentication:         SHA-256 hashing
Charts/Visualization:   Plotly
```

## File Structure

```
climateguardian-ai/
│
├── app.py                          # Main application (850+ lines)
├── auth.py                         # Authentication module
├── requirements.txt                # Dependencies list
├── README.md                       # Main documentation
│
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml               # API keys (gitignored)
│
├── .gitignore                      # Git ignore rules
│
├── assets/
│   ├── questions_sustainability.json
│   └── icons/
│
├── games/
│   ├── __init__.py                # Package initializer
│   ├── eco_runner.py              # Game 1 (Pygame)
│   ├── renewable_energy.py        # Game 2 (Pygame)
│   ├── waste_segregation.py       # Game 3 (OpenCV + MediaPipe)
│   └── __pycache__/
│
├── js/
│   ├── main.js                    # Main JavaScript
│   ├── chat.js                    # Chat functionality
│   ├── quiz.js                    # Quiz system
│   ├── dashboard.js               # Dashboard
│   ├── missions.js                # Mission tracking
│   ├── navigation.js              # Navigation
│   ├── sustainability.js          # Carbon calculator
│   └── games/
│       ├── eco-runner.js
│       └── renewable-energy.js
│
├── styles/
│   └── main.css                   # Global styles
│
├── index.html                      # Main HTML page
├── test_kbc.html                  # KBC testing page
│
├── users_database.csv             # User data (auto-created)
├── user_activities.csv            # Activity log (auto-created)
├── certificates_database.csv      # Certificate records (auto-created)
│
└── MASTER_DOCUMENTATION.md        # Complete documentation
```

## Database Schema

All data is stored in CSV files in the project's root directory.

### users_database.csv
```
username          | email              | password_hash  | eco_score | joined_date
student1          | s1@example.com    | sha256_hash... | 250       | 2026-01-20
student2          | s2@example.com    | sha256_hash... | 175       | 2026-01-19
```

### user_activities.csv
```
id | timestamp           | username | action             | points
1  | 2026-02-07 10:00:00 | student1 | Recycled Plastic   | 15
2  | 2026-02-07 11:30:00 | student2 | Eco-Runner Game    | 50
```

### certificates_database.csv
```
certificate_id              | username | eco_score | rank | issued_date
CERT_student1_1769812345    | student1 | 520       | 1    | 2026-02-07 14:00:00
```

---

# Full Project Update Summary

This section contains the complete update history for the current version of the project. It is the detailed source of all recent changes and improvements.

---

# Latest Updates & Changes

## 🎉 Version 2.0 Updates

### ✨ Enhanced Eco-Runner Game

**New Features:**
- 🍃 **Green leaves** instead of green circles
- 🗑️ **Garbage/waste icons** instead of red squares
- 👤 **Person character** instead of blue rectangle
- ☀️ **Sky gradient background** (light blue)
- 🌱 **Grass ground** at the bottom

### ✨ NEW GAME: Smart Waste Segregation

**Game Description:**
A fun educational game where players use AI hand gesture tracking to drag and drop falling waste items into the correct colored recycling bins.

**Features:**
- **AI-Powered Hand Tracking** with MediaPipe
- **4 Colored Bins** for different waste types
- **Drag & Drop Mechanics** using pinch gestures
- **Real-time Scoring** (+10 correct, -5 wrong)
- **Game Levels** with increasing difficulty
- **Educational Value** - Learn proper waste segregation

### ✨ Video Verification for Walked Missions

**Implementation:**
- Upload 15-60 second video of walking/biking
- AI analyzes 3 key frames from video
- Verifies authenticity, activity, and environment
- Awards 20 Eco-Points on success
- Prevents fraud through multi-frame analysis

### 📊 Updated Points System

**New Maximum Points:**
- **Old:** 175 points (2 games)
- **NEW:** 250+ points (3 games + missions + quiz)

| Activity | Points |
|----------|--------|
| Quiz Correct | 5 |
| Quiz Wrong | -2.5 |
| Eco-Runner | 50 |
| Energy Puzzle | 50 |
| Waste Segregation | 75 |
| Missions | 5-50 |

---

## 🐛 Bug Fixes & Improvements

- Fixed Eco-Runner visual elements
- Improved collision detection in games
- Better game state management
- Cleaner code organization
- Enhanced error handling
- Optimized database performance

---

## 🌟 Quality Assurance

### Testing Completed
- ✅ Authentication system
- ✅ All three games (Eco-Runner, Energy Puzzle, Waste Segregation)
- ✅ AI chat functionality
- ✅ Quiz generation
- ✅ Mission logging with video verification
- ✅ Carbon calculator
- ✅ Admin dashboard
- ✅ Points system
- ✅ Database operations
- ✅ Cross-platform compatibility
- ✅ Camera integration
- ✅ Hand gesture tracking

---

## 🚀 Performance Benchmarks

| Metric | Value |
|--------|-------|
| Load Time | < 5 seconds |
| Quiz Generation | 2-5 seconds |
| Game Launch | 1-3 seconds |
| Video Processing | 15-30 seconds |
| API Response | 1-20 seconds |
| Memory Usage | ~50-100 MB (per request) |

---

## ✅ Final Checklist Before Deployment

- [ ] All dependencies installed
- [ ] API keys configured in secrets.toml
- [ ] Database initialized
- [ ] All games tested
- [ ] Quiz system working
- [ ] Authentication tested
- [ ] Admin dashboard displays correctly
- [ ] Video verification working
- [ ] Camera/hand tracking functional
- [ ] No error messages in logs
- [ ] Performance acceptable
- [ ] Documentation reviewed

---

## 🎊 Conclusion

**ClimateGuardian AI v2.0** is a complete, production-ready sustainability education platform featuring:

✨ **Fun Interactive Games** (3 games)
🤖 **AI-Powered Learning** (Chat + Quiz)
📊 **Comprehensive Tracking** (Missions + Dashboard)
🔐 **Secure Authentication** (User accounts)
🎮 **Gamification** (250+ points possible)
🌍 **Environmental Focus** (Real-world learning)

### Ready to Deploy ✅
- All features tested and working
- Comprehensive documentation provided
- Error handling included
- Performance optimized
- Security verified

---

## 📞 Support

### Documentation Resources
1. **Quick Start:** This master documentation
2. **Games:** Games Guide section above
3. **Missions:** Walked Mission Implementation section above
4. **Admin:** Administration & Dashboard section above
5. **Troubleshooting:** Troubleshooting section above

### External Resources
- **Streamlit Docs:** https://docs.streamlit.io
- **Pygame Docs:** https://www.pygame.org/docs/
- **OpenCV Docs:** https://docs.opencv.org
- **MediaPipe Docs:** https://google.github.io/mediapipe/
- **Groq API:** https://console.groq.com

---

## 📋 Version History

| Version | Date | Major Changes |
|---------|------|----------------|
| 1.0 | Q4 2025 | Initial release with 2 games |
| 1.5 | Q1 2026 | Added quiz system, missions |
| 2.0 | Jan 2026 | Added waste game, video verification |

---

## 🌿 Summary

**Project Status:** ✅ Complete & Functional
**Version:** 2.0
**Platform:** Python 3.8+ + Streamlit
**License:** Educational Use
**Last Updated:** January 20, 2026

---

**🌍 Let's Save the Planet Together! 🌍♻️**

**Made with 💚 for a greener planet**

---

*For detailed information, refer to specific sections in this master documentation.*
*All information consolidated from 17 original documentation files.*

---

# 🍎 Food Verification System - Improved Compostable Detection

**Date:** January 20, 2026  
**Status:** ✅ Implemented & Tested  
**Issue Fixed:** Food images were being awarded points without verifying if they're actually compostable

---

## 🎯 The Problem

Previously, when users uploaded ANY image detected as "food," the system would automatically award **+5 eco points** without verifying if the food is actually **compostable** or not.

**Example Issues:**
- ❌ Uploading a website screenshot → Detected as "Web_Site" food → +5 points (WRONG!)
- ❌ Uploading cooked pizza → Detected as food → +5 points (NOT compostable!)
- ❌ Uploading meat/fish → Detected as food → +5 points (NOT compostable!)
- ❌ Uploading processed foods → Detected as food → +5 points (NOT compostable!)

---

## ✅ The Solution

### Enhanced Food Classification System

**New Database: `COMPOSTABLE_FOOD_DB`**

Only **raw, uncooked fruits, vegetables, and grains** are compostable:
- ✅ Banana, Mango, Apple, Orange, Strawberry
- ✅ Tomato, Carrot, Broccoli, Spinach, Lettuce, Potato, Onion
- ✅ Rice, Wheat, Corn

**New Database: `NON_COMPOSTABLE_FOOD`**

Foods that are detected but NOT compostable (NO points awarded):
- ❌ Pizza, Burger, Hotdog, Fries, Chips
- ❌ Candy, Chocolate, Ice Cream, Doughnut, Cake
- ❌ Meat, Chicken, Fish, Eggs, Dairy, Milk, Cheese
- ❌ Cooked foods, Processed foods, Oils, Butters

**Expanded Database: `NON_FOOD_ITEMS`**

Non-food items that get rejected immediately:
- ❌ Bottles, Cans, Phones, Laptops
- ❌ People, Cars, Dogs, Cats, Birds
- ❌ **Websites, Screenshots, Documents, Papers**

---

## 🔍 Improved Classification Logic

### Step-by-Step Verification:

```
1. Upload Image
   ↓
2. Check if AI-Generated
   ├─ If AI-Generated → ❌ REJECT "Not a real image"
   └─ If Real → Continue
   ↓
3. Check if Non-Food Item
   ├─ If Non-Food → ❌ REJECT "Not a food item"
   └─ If Food → Continue
   ↓
4. Check if Compostable
   ├─ If Non-Compostable (pizza, meat, etc.)
   │  → ⚠️ REJECT "Food but NOT compostable, 0 points"
   │
   ├─ If Compostable (fruit, vegetable, grain)
   │  → ✅ APPROVE "+N eco points awarded!"
   │
   └─ If Unknown Food
      → ❓ REJECT "Not in compostable database, 0 points"
```

---

## 📊 New Response Logic

### Response Types:

**❌ AI-Generated Image:**
```
Status: ❌ REJECTED
Message: "🤖 AI-generated image! (Not real)"
Points: 0
Example: When detecting AI-generated food images
```

**❌ Non-Food Item:**
```
Status: ❌ REJECTED
Message: "🚫 Not a food item: Web_Site detected!"
Points: 0
Example: Website screenshots, documents, objects
```

**⚠️ Non-Compostable Food:**
```
Status: ⚠️ WARNING
Message: "Pizza is NOT compostable! (Processed/cooked foods & animal products cannot be composted)"
Points: 0
Example: Cooked foods, meat, dairy, processed items
```

**✅ Compostable Food:**
```
Status: ✅ APPROVED
Message: "Perfect! Banana is compostable! +10 eco points!"
Points: +10 (varies by food type)
Example: Raw fruits, vegetables, grains
```

**❓ Unknown Food:**
```
Status: ❓ UNKNOWN
Message: "Unknown food detected, but NOT in our compostable database!"
Points: 0
Example: Any food not in the compostable database
```

---

## 🎯 Key Changes

### 1. Updated UI Messages
- ✅ Clear guidance: "Upload ONLY raw food"
- ✅ Warning about non-compostable items
- ✅ Specific feedback on why something wasn't awarded points

### 2. Improved Error Handling
- Better detection of non-food items (added "website", "screen", etc.)
- Rejection of cooked/processed foods
- Better messaging for each rejection type

### 3. Points System
- Only compostable foods get points (5-12 depending on type)
- Non-compostable foods get 0 points with explanation
- Unknown foods get 0 points with hint to upload known items

### 4. Educational Value
- Teaches users which foods are compostable
- Explains why certain foods can't be composted
- Provides eco-friendly tips for waste management

---

## 📈 Compostable Food Points

| Food | Type | Points |
|------|------|--------|
| Banana | Fruit | 10 |
| Mango | Fruit | 12 |
| Apple | Fruit | 11 |
| Strawberry | Fruit | 10 |
| Carrot | Vegetable | 9 |
| Broccoli | Vegetable | 10 |
| Spinach | Vegetable | 8 |
| Potato | Vegetable | 6 |
| Rice | Grain | 7 |
| Corn | Grain | 8 |

---

## 🚫 Non-Compostable Foods (0 Points)

| Category | Examples |
|----------|----------|
| Processed | Pizza, Burgers, Hotdogs |
| Sweets | Candy, Chocolate, Ice Cream |
| Animal Products | Meat, Fish, Eggs, Dairy |
| Cooked Foods | Any cooked meal |
| Oils/Fats | Butter, Oil, Ghee |

---

## 🎓 How It Works Now

### User Uploads Website Screenshot:
```
User Action: Upload screenshot of website
AI Detection: Detects "Web_Site" as non-food
System Response: ❌ "Not a food item: Web_Site detected!"
Points Awarded: 0
Message: Clear rejection with reason
```

### User Uploads Pizza (Cooked):
```
User Action: Upload photo of pizza
AI Detection: Detects "pizza" as non-compostable food
System Response: ⚠️ "Pizza is NOT compostable! 
                    (Processed/cooked foods cannot be composted)"
Points Awarded: 0
Tip Shown: "Only raw fruits, vegetables & grains are compostable"
```

### User Uploads Apple (Raw):
```
User Action: Upload photo of raw apple
AI Detection: Detects "apple" as compostable fruit
System Response: ✅ "Perfect! Apple is compostable! +11 eco points!"
Points Awarded: +11
Insights: Groq provides Hinglish tips on composting the apple
Balloons: 🎉 Celebration animation
```

---

## 💻 Code Changes

### 1. New Database Addition
```python
COMPOSTABLE_FOOD_DB = {
    'banana': {'compostable': True, 'eco_points': 10, ...},
    'apple': {'compostable': True, 'eco_points': 11, ...},
    # ... only compostable foods
}

NON_COMPOSTABLE_FOOD = ['pizza', 'meat', 'cooked', ...]
NON_FOOD_ITEMS = ['bottle', 'website', 'screenshot', ...]
```

### 2. Updated Classification Logic
```python
def classify_food(self, image_path):
    # 1. Check if AI-generated
    # 2. Check if non-food
    # 3. Check if compostable
    # 4. Only award points if compostable
    # 5. Provide specific feedback for each case
```

### 3. Updated Mission Handler
```python
elif action == "Composted Food":
    # Show clear instructions about compostable foods
    # Analyze food with enhanced classifier
    # Only log action & award points if compostable
    # Reject with explanation otherwise
```

---

## ✨ User Experience Improvements

### Before:
- ❌ Any food image = points
- ❌ Website screenshots = points (wrong!)
- ❌ No explanation for wrong uploads
- ❌ Encouraged cheating

### After:
- ✅ Only real compostable foods = points
- ✅ Website/non-food = rejected with reason
- ✅ Cooked/processed = rejected with explanation
- ✅ Clear educational feedback
- ✅ Prevents gaming the system

---

## 🔒 Anti-Fraud Features

1. **AI Generation Detection** - Detects AI-generated images
2. **Non-Food Detection** - Rejects non-food items (websites, objects)
3. **Compostability Check** - Only awards points for truly compostable items
4. **Confidence Threshold** - Validates detection confidence
5. **Educational Feedback** - Teaches why something can't be composted

---

## 📱 Example User Interactions

### Scenario 1: User uploads screenshot
```
User: Uploads website screenshot
System: "🚫 Not a food item: Web_Site detected!"
Result: 0 points, clear explanation
```

### Scenario 2: User uploads frozen pizza
```
User: Uploads frozen pizza image
System: "⚠️ Pizza is NOT compostable! 
        (Processed/cooked foods cannot be composted)"
Result: 0 points, tip to use raw foods
```

### Scenario 3: User uploads banana peel
```
User: Uploads banana peel (raw)
System: "✅ Perfect! Banana is compostable! +10 eco points!"
Result: +10 points, celebration animation
Insights: "Banana peels are rich in potassium and compost quickly..."
```

---

## 🎯 Testing Checklist

- [x] Website images rejected
- [x] Non-food items rejected  
- [x] Cooked food rejected
- [x] Processed food rejected
- [x] Meat/dairy rejected
- [x] Raw fruits accepted
- [x] Raw vegetables accepted
- [x] Grains accepted
- [x] Points awarded only for compostable
- [x] User feedback is clear
- [x] Error messages are helpful

---

## 🚀 Deployment

The updated system is now live and ready to use:

1. ✅ Improved food detection database
2. ✅ Better classification logic
3. ✅ Clear user feedback
4. ✅ Anti-fraud features
5. ✅ Educational messaging

**All changes are backward compatible** - existing missions continue to work correctly.

---

## 📞 Support

Users now get clear feedback when:
- ❌ They upload non-food items (websites, objects)
- ❌ They upload non-compostable foods (processed, cooked)
- ✅ They upload compostable foods (gets points!)

The system educates users about what is actually compostable while preventing abuse of the point system.

---

**Status:** ✅ **LIVE & OPERATIONAL**  
**Version:** 2.1  
**Date:** January 20, 2026  

---

# 🎖️ Certificate System - Complete Integration Guide

## Overview
A comprehensive certificate generation and management system has been integrated into ClimateGuardian AI. Users who achieve 500+ eco-points can earn beautifully designed certificates with unique IDs. Certificates are automatically issued in the Student Hub when users confirm their eligibility.

---

## 🎯 Key Features

### 1. **For Users - Mission Tab (Certificate Status)**

#### Certificate Eligibility Display
- Real-time eco-score tracking
- Visual progress bar showing progress to 500 points
- Status indicators:
  - ✅ **Eligible**: User has 500+ eco-points
  - 🔄 **In Progress**: Continue earning points

#### Certificate Benefits (Once Eligible)
- 📜 **Beautiful Certificate PDF**: Landscape orientation with eco-themed design
- 📍 **Certificate ID**: Unique identifier for each certificate
- ⭐ **Eco-Score Display**: Shows final score achieved
- 🏅 **Rank Display**: Shows global ranking among all users
- 📅 **Issue Date**: Timestamp of certificate issuance

#### Earn Your Certificate
- Once you reach 500+ eco-points, your certificate becomes eligible
- Click "Confirm Certificate Earned" button to automatically issue your certificate
- Download your certificate as a PDF from the Missions tab
- Professional design with:
  - Green eco-theme styling
  - Golden award seal
  - Leaf decorations
  - Director and ClimateGuardian AI signatures

---

### 2. **For Admin - Admin Dashboard (Certificate Viewing)**

#### View Only Section
- View all issued certificates (informational purposes)
- Certificate details:
  - Username & Eco-Score
  - Global Rank
  - Issuance date
  - Certificate ID
- Download PDF certificate
- Manage and track issued certificates
- Monitor student certificate earning progress

**📌 Note:** Certificates are now automatically issued in the Student Hub when eligible users confirm their certificate. Admins no longer need to manually approve certificates.

---

## 📊 Database Structure

### New Database: `certificates_database.csv`
```
Columns:
- username: User who earned certificate
- eco_score: Final eco-score at issuance
- rank: Global ranking at issuance
- issued_date: Date & time certificate was issued
- certificate_id: Unique certificate identifier
```

---

## 🛠️ Technical Implementation

### New Functions in `auth.py`

#### Core Certificate Functions
```python
def load_certificates()
  - Loads certificate database
  
def save_certificates(df)
  - Saves certificate records to CSV
  
def generate_certificate_pdf(username, eco_score, rank, total_users)
  - Creates beautiful landscape PDF certificate
  - Uses ReportLab for advanced PDF generation
  - Returns: BytesIO buffer with PDF data
  
def issue_certificate(username)
  - Issues certificate if user eligible (500+ points)
  - Checks for duplicate certificates
  - Creates database record
  - Logs activity
  - Returns: Success status and certificate ID
  
def check_certificate_eligibility(username)
  - Verifies if user has 500+ eco-points
  - Returns: (eligibility_bool, eco_score)
  
def get_certificate_info(username)
  - Retrieves certificate details for user
  - Returns: Dictionary with certificate data
  
def get_all_certificates()
  - Loads all issued certificates
  - Returns: DataFrame with all certificate records
```

---

## 📦 Dependencies Added

New packages in `requirements.txt`:
```
reportlab==4.0.9          # PDF generation
```

---

## 🎨 Certificate Design Features

### Visual Elements
- **Background**: Light green eco-theme (#e9f7ef)
- **Ribbon**: Dark green curved ribbon on top-left
- **Leaf Decorations**: Two abstract leaf shapes on right side
- **Award Seal**: Golden circular seal with "BEST AWARD"
- **Typography**: Professional Helvetica fonts with hierarchy
- **Content**: 
  - Certificate title and appreciation text
  - Username prominently displayed
  - Eco-score in large font
  - Global rank and user count
  - Director and ClimateGuardian AI signatures
  - Issuance date

---

## 🔄 Workflow

### User Journey
1. **Earn Points**: Complete missions and games
2. **Reach 500 Points**: System marks as eligible
3. **Get Certificate**: Click "Confirm Certificate Earned" in the Missions tab
4. **Download**: User can download PDF anytime

### Student Hub Automatic Certificate Flow
1. **Complete Missions**: Earn eco-points through activities
2. **Reach 500+ Points**: Certificate becomes eligible
3. **View Certificate Section**: Navigate to Missions tab
4. **Confirm**: Click "Confirm Certificate Earned" button
5. **Automatic Issuance**: Certificate is generated instantly
6. **Download PDF**: Download your certificate immediately

---

## ✨ Additional Features

### Progress Tracking
- Visual progress bar showing distance to 500 points
- Percentage display of completion
- Real-time eco-score updates

### Quality Assurance
- Prevents duplicate certificate issuance
- Validates user eligibility
- Logs all certificate activities
- Unique certificate IDs for tracking

### User Experience
- One-click PDF download
- Beautiful responsive design
- Clear status messages

---

## 🚀 Usage Instructions

### For End Users (Students)
1. Go to **✅ Missions** tab in Student Hub
2. Scroll to **🎖️ Certificate Status** section
3. Monitor progress to 500 eco-points
4. Once eligible (500+ points):
   - View "Earn Your Certificate" section
   - Click **"Confirm Certificate Earned"** button
   - Certificate is instantly issued!
5. Download PDF anytime

### For Administrators
1. Go to **📊 Admin Dashboard**
2. Scroll to **🎖️ Certificate Status (View Only)**
3. Switch to **✅ View Issued Certificates** tab
4. Review and download certificates for records/verification
5. Track student certificate earning progress

---

## 📝 Notes

- Certificates are automatically issued for users with 500+ eco-points
- Each user can only receive one certificate (duplicates prevented)
- Issuance happens instantly when user confirms in Student Hub
- All certificates stored in `certificates_database.csv`
- Activity logged automatically
- System prevents duplicate issuance with validation checks

---

## 🎯 Future Enhancements
- Email notifications when certificate is earned
- Certificate verification portal
- Advanced analytics on certificate distribution
- Custom certificate designs based on achievements
- Bulk certificate sharing for events
- Digital badge system integration
