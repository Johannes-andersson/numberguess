import random
import json
import os
import math
from typing import Dict, List, Tuple, Optional

class HotColdLearner:
    def __init__(self, target_guesses=3):
        self.k = 0.3  # initial hot threshold multiplier
        self.target_guesses = target_guesses
        self.learning_rate = 0.1
        self.history = []  # (actual_guesses, predicted_guesses) pairs
        
    def update_k(self, actual_guesses: int, predicted_guesses: int):
        """Update k based on prediction accuracy"""
        if actual_guesses <= self.target_guesses:
            # We want more hints, so increase k (make hot zone larger)
            self.k += self.learning_rate * (1 - predicted_guesses / self.target_guesses)
        else:
            # We want fewer hints, so decrease k (make hot zone smaller)
            self.k -= self.learning_rate * (actual_guesses / self.target_guesses - 1)
        
        # Keep k in reasonable bounds
        self.k = max(0.1, min(0.8, self.k))
    
    def is_hot(self, guess: int, secret: int, cur_lo: int, cur_hi: int) -> bool:
        """Determine if a guess is 'hot' based on learned threshold"""
        distance = abs(guess - secret)
        range_size = cur_hi - cur_lo + 1
        threshold = self.k * range_size
        return distance < threshold
    
    def record_game(self, actual_guesses: int):
        """Record game outcome for learning"""
        predicted_guesses = self.target_guesses  # Simple prediction for now
        self.history.append((actual_guesses, predicted_guesses))
        self.update_k(actual_guesses, predicted_guesses)

class HintBandit:
    def __init__(self, hint_styles: List[str], exploration_rate=0.1):
        self.hint_styles = hint_styles
        self.exploration_rate = exploration_rate
        self.attempts = {style: 0 for style in hint_styles}
        self.avg_attempts = {style: 0.0 for style in hint_styles}
        self.total_games = 0
        
    def select_hint_style(self) -> str:
        """Select hint style using epsilon-greedy strategy"""
        if random.random() < self.exploration_rate:
            return random.choice(self.hint_styles)
        
        # Exploit: choose style with lowest average attempts
        best_style = min(self.hint_styles, key=lambda x: self.avg_attempts[x])
        return best_style
    
    def update_stats(self, hint_style: str, attempts: int):
        """Update statistics for a hint style"""
        self.attempts[hint_style] += 1
        self.total_games += 1
        
        # Update running average
        if self.attempts[hint_style] == 1:
            self.avg_attempts[hint_style] = attempts
        else:
            self.avg_attempts[hint_style] = 0.8 * self.avg_attempts[hint_style] + 0.2 * attempts

class UserProfile:
    def __init__(self, username: str):
        self.username = username
        self.alpha = 0.5  # user's number picking bias
        self.avg_attempts = None
        self.range_size = 100
        self.games_played = 0
        self.hot_cold_learner = HotColdLearner()
        self.hint_bandit = HintBandit(['hot_cold', 'higher_lower', 'range'])
        
    def save_to_file(self):
        """Save user profile to JSON file"""
        data = {
            'username': self.username,
            'alpha': self.alpha,
            'avg_attempts': self.avg_attempts,
            'range_size': self.range_size,
            'games_played': self.games_played,
            'hot_cold_k': self.hot_cold_learner.k,
            'hint_style_stats': {
                style: {
                    'attempts': self.hint_bandit.attempts[style],
                    'avg_attempts': self.hint_bandit.avg_attempts[style]
                } for style in self.hint_bandit.hint_styles
            }
        }
        
        filename = f"user_{self.username}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self):
        """Load user profile from JSON file"""
        filename = f"user_{self.username}.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.alpha = data.get('alpha', 0.5)
                self.avg_attempts = data.get('avg_attempts')
                self.range_size = data.get('range_size', 100)
                self.games_played = data.get('games_played', 0)
                
                if 'hot_cold_k' in data:
                    self.hot_cold_learner.k = data['hot_cold_k']
                
                if 'hint_style_stats' in data:
                    for style, stats in data['hint_style_stats'].items():
                        if style in self.hint_bandit.hint_styles:
                            self.hint_bandit.attempts[style] = stats['attempts']
                            self.hint_bandit.avg_attempts[style] = stats['avg_attempts']
                
                print(f"Welcome back, {self.username}! I remember you.")
                return True
            except Exception as e:
                print(f"Couldn't load profile: {e}")
        return False

class AdaptiveGame:
    def __init__(self, username: str):
        self.user = UserProfile(username)
        self.user.load_from_file()
        
    def get_hint(self, guess: int, secret: int, cur_lo: int, cur_hi: int, hint_style: str) -> str:
        """Generate hint based on selected style"""
        if hint_style == 'hot_cold':
            if self.user.hot_cold_learner.is_hot(guess, secret, cur_lo, cur_hi):
                return "🔥 HOT!"
            else:
                return "❄️ COLD!"
        elif hint_style == 'higher_lower':
            if guess < secret:
                return "Higher!"
            else:
                return "Lower!"
        elif hint_style == 'range':
            distance = abs(guess - secret)
            range_size = cur_hi - cur_lo + 1
            if distance < range_size * 0.1:
                return "🔥 Very close!"
            elif distance < range_size * 0.3:
                return "🔥 Getting warm!"
            elif distance < range_size * 0.5:
                return "🌤️ Lukewarm"
            else:
                return "❄️ Far away!"
        return "Invalid hint style"
    
    def play_user_guesses(self):
        """User guesses the computer's number"""
        lo, hi = 1, self.user.range_size
        secret = random.randint(lo, hi)
        attempts = 0
        cur_lo, cur_hi = lo, hi
        
        print(f"\n🎯 I'm thinking of a number between {lo} and {hi}.")
        print(f"💡 Based on your profile, I think you'll pick numbers around position {self.user.alpha:.2f}")
        
        hint_style = self.user.hint_bandit.select_hint_style()
        print(f"🎲 Using hint style: {hint_style}")
        
        while True:
            try:
                guess = int(input(f"Your guess [{cur_lo}-{cur_hi}]: "))
            except ValueError:
                print("Numbers only, please!")
                continue
            
            if guess < cur_lo or guess > cur_hi:
                print(f"Stay in range [{cur_lo}, {cur_hi}].")
                continue
            
            attempts += 1
            
            # Update user's alpha based on their guess position
            if cur_hi > cur_lo:
                pos = (guess - cur_lo) / (cur_hi - cur_lo)
                self.user.alpha = 0.9 * self.user.alpha + 0.1 * pos
            
            hint = self.get_hint(guess, secret, cur_lo, cur_hi, hint_style)
            print(f"💡 {hint}")
            
            if guess == secret:
                print(f"🎉 Bang! You got it in {attempts} attempts!")
                self.user.hot_cold_learner.record_game(attempts)
                self.user.hint_bandit.update_stats(hint_style, attempts)
                self.update_user_stats(attempts)
                break
            elif guess < secret:
                print("Higher.")
                cur_lo = max(cur_lo, guess + 1)
            else:
                print("Lower.")
                cur_hi = min(cur_hi, guess - 1)
    
    def play_computer_guesses(self):
        """Computer guesses the user's number using learned alpha"""
        lo, hi = 1, self.user.range_size
        attempts = 0
        cur_lo, cur_hi = lo, hi
        
        print(f"\n🤔 Think of a number between {lo} and {hi}.")
        print(f"🧠 I'll try to read your mind using my learned alpha: {self.user.alpha:.2f}")
        input("Press Enter when you're ready...")
        
        while True:
            # Use alpha to bias guess toward user's preferred position
            if cur_hi > cur_lo:
                bias_pos = cur_lo + (cur_hi - cur_lo) * self.user.alpha
                guess = round(bias_pos)
            else:
                guess = cur_lo
            
            # Ensure guess is in valid range
            guess = max(cur_lo, min(cur_hi, guess))
            
            attempts += 1
            print(f"🤖 My guess #{attempts}: {guess}")
            
            try:
                response = input("Is it (h)igher, (l)ower, or (c)orrect? ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGame interrupted.")
                return
            
            if response == 'c':
                print(f"🎯 Got it in {attempts} attempts!")
                break
            elif response == 'h':
                cur_lo = max(cur_lo, guess + 1)
                print(f"Higher than {guess}. Range: [{cur_lo}, {cur_hi}]")
            elif response == 'l':
                cur_hi = min(cur_hi, guess - 1)
                print(f"Lower than {guess}. Range: [{cur_lo}, {cur_hi}]")
            else:
                print("Please enter h, l, or c.")
                continue
            
            if cur_lo > cur_hi:
                print("Something's wrong with the range!")
                break
    
    def update_user_stats(self, attempts: int):
        """Update user statistics after a game"""
        if self.user.avg_attempts is None:
            self.user.avg_attempts = attempts
        else:
            self.user.avg_attempts = 0.8 * self.user.avg_attempts + 0.2 * attempts
        
        self.user.games_played += 1
        
        # Adjust range size based on performance
        if self.user.avg_attempts < 4:
            self.user.range_size = min(10000, int(self.user.range_size * 1.2))
        elif self.user.avg_attempts > 8:
            self.user.range_size = max(10, int(self.user.range_size * 0.8))
    
    def show_stats(self):
        """Display current user statistics"""
        print(f"\n📊 {self.user.username}'s Stats:")
        print(f"   Games played: {self.user.games_played}")
        print(f"   Average attempts: {self.user.avg_attempts:.1f}" if self.user.avg_attempts else "   Average attempts: N/A")
        print(f"   Current range size: {self.user.range_size}")
        print(f"   Alpha (number bias): {self.user.alpha:.3f}")
        print(f"   Hot/Cold threshold (k): {self.user.hot_cold_learner.k:.3f}")
        print(f"   Hint style performance:")
        for style in self.user.hint_bandit.hint_styles:
            avg = self.user.hint_bandit.avg_attempts[style]
            count = self.user.hint_bandit.attempts[style]
            if count > 0:
                print(f"     {style}: {avg:.1f} attempts ({count} games)")
    
    def save_profile(self):
        """Save user profile"""
        self.user.save_to_file()
        print(f"💾 Profile saved for {self.user.username}")

def main():
    print("🎮 Adaptive Number Guessing Game")
    print("=" * 40)
    
    username = input("Enter your username: ").strip() or "Player"
    game = AdaptiveGame(username)
    
    while True:
        print(f"\n🎯 Game Modes:")
        print("1. You guess my number (with adaptive hints)")
        print("2. I guess your number (I learn your patterns)")
        print("3. Show my stats")
        print("4. Save profile")
        print("5. Quit")
        
        try:
            choice = input(f"\n{username}, what would you like to do? (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if choice == '1':
            game.play_user_guesses()
        elif choice == '2':
            game.play_computer_guesses()
        elif choice == '3':
            game.show_stats()
        elif choice == '4':
            game.save_profile()
        elif choice == '5':
            game.save_profile()
            print("👋 Thanks for playing! Your profile has been saved.")
            break
        else:
            print("Please enter 1-5.")

if __name__ == "__main__":
    main()
