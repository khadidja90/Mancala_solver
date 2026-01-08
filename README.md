# 🟤 Mancala Game with AI (Minimax + Alpha-Beta)

<img src="images/Screenshot 2026-01-08 221049.png" width="220" />
This project is a **Mancala board game** implemented in **Python using Pygame**, featuring:
- A full graphical interface
- Sound effects and background music
- Human vs AI mode
- AI vs AI mode
- Artificial Intelligence based on **Minimax with Alpha-Beta Pruning**
- Animated marble movements and hover tooltips

---

## 🎮 Game Features

- **Game Modes**
  - 👤 Human vs 🤖 AI
  - 🤖 AI vs 🤖 AI (two different AI depths)

- **AI Algorithm**
  - Minimax search
  - Alpha-Beta pruning
  - Adjustable search depth

- **User Interface**
  - Splash screen
  - Instructions screen
  - Mode selection
  - Animated gameplay
  - Score screen
  - Play again / Home menu

- **Visual Enhancements**
  - Marble animations
  - Highlighted AI-selected pits
  - Hover tooltips showing number of marbles
  - Custom board and UI images

- **Audio**
  - Background music
  - Click and marble drop sound effects

---

## 🧠 AI Logic Overview

The AI uses:
- **Minimax algorithm** to explore possible moves
- **Alpha-Beta pruning** to optimize performance
- Board evaluation based on:
AI Store − Human Store

yaml
Copy code

Two AI levels are used in AI vs AI mode:
- **MAX AI** → deeper search (stronger)
- **MIN AI** → shallower search (weaker)

🕹️ Controls
Mouse Click → Select pits and navigate menus

Hover over pits → See number of marbles

Game flow is fully mouse-based

🏆 Game Rules (Mancala)
Each pit starts with 4 marbles

Players pick marbles from one pit and distribute them counter-clockwise

Skip the opponent’s store

If the last marble lands in your store → extra turn

Capture happens if the last marble lands in an empty pit on your side

Game ends when one side is empty

Winner is the player with the most marbles in their store

📌 Educational Purpose
This project demonstrates:

Game development with Pygame

Implementation of search algorithms

Use of AI decision-making

State management and animation

Separation of logic (engine) and interface (UI)

Ideal for:

AI courses

Game development projects

Algorithm demonstrations

Academic assignments

📜 License
This project is for educational purposes.
Feel free to use, modify, and improve it.

✨ Author
Developed as a learning project combining:

Artificial Intelligence

Python programming

Game design with Pygame

## 📸 Screenshots

### Main Menu

<img src="images/Screenshot 2026-01-08 220847.png" width="220" />
<img src="images/Screenshot 2026-01-08 220951.png" width="220" />
<img src="images/Screenshot 2026-01-08 221020.png" width="220" />



### Gameplay
<img src="images/Screenshot 2026-01-08 221049.png" width="220" />

### Score Screen
<img src="images/Screenshot 2026-01-08 221112.png" width="220" />
<img src="images/Screenshot 2026-01-08 221137.png" width="220" />

