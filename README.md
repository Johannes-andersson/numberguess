# 🎮 Adaptive Number Guessing Game

An intelligent number guessing game that learns your playing patterns and adapts its hints and strategies to provide the best gaming experience.

## ✨ Features

### 🔥 Hot/Cold with Adaptive Learning
- **Dynamic threshold**: The game learns the optimal threshold for "hot" hints based on your performance
- **Smart feedback**: Adapts hint frequency based on your solving speed
- **Personalized experience**: Gets better at helping you solve puzzles efficiently

### 🎲 Bandit Learning for Hint Styles
- **Three hint styles**:
  - `hot_cold`: 🔥 HOT! / ❄️ COLD!
  - `higher_lower`: Higher! / Lower!
  - `range`: 🔥 Very close! / 🌤️ Lukewarm / ❄️ Far away!
- **Epsilon-greedy selection**: Balances exploration vs. exploitation
- **Performance tracking**: Learns which hint style works best for you

### 💾 User Profile & Persistence
- **JSON storage**: Saves your profile to `user_[username].json`
- **Learned parameters**: Remembers your preferences across gaming sessions
- **Session continuity**: Loads your profile when you return

### 🤖 Reverse Game Mode
- **Computer guesses**: You think of a number, the computer guesses it
- **Alpha-based bias**: Uses your learned number-picking patterns
- **Mind reading**: Gets better at predicting your choices over time

## 🚀 How to Play

1. **Install Python 3.7+**
2. **Run the game**: `python3 game.py`
3. **Enter username**: Creates or loads your profile
4. **Choose game mode**:
   - Mode 1: You guess (with adaptive hints)
   - Mode 2: Computer guesses (using your patterns)
   - Mode 3: View your stats
   - Mode 4: Save profile
   - Mode 5: Quit

## 🧠 How It Works

### Hot/Cold Learning
The game defines "hot" as distance < k × (current_range_size), where k is learned online to predict you'll solve in ≤3 more guesses.

### Hint Bandit
Uses UCB1-inspired epsilon-greedy strategy to select the most effective hint style for you.

### User Profiling
Tracks your number-picking bias (alpha) and adjusts difficulty based on performance.

## 📊 Game Statistics

The game tracks and displays:
- Games played
- Average attempts per game
- Current range size
- Your number bias (alpha)
- Hot/Cold threshold (k)
- Hint style performance

## 🔧 Technical Details

- **Language**: Python 3.7+
- **Dependencies**: Standard library only (random, json, os, math, typing)
- **Architecture**: Object-oriented with separate classes for different learning components
- **Data Storage**: JSON files for user persistence

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for improvements!

## 🎯 Future Enhancements

- [ ] UCB1 algorithm for hint selection
- [ ] More sophisticated prediction models
- [ ] Multiplayer support
- [ ] Web interface
- [ ] Machine learning integration

---

**Enjoy playing and watch as the game learns to read your mind! 🧠✨**
