"""Economy system - money and lives management"""
from config import STARTING_MONEY, STARTING_LIVES


class Economy:
    """Manages money and lives"""
    
    def __init__(self):
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.max_lives = STARTING_LIVES
        
        # Stats
        self.total_earned = 0
        self.total_spent = 0
        self.enemies_killed = 0
        self.waves_completed = 0
    
    def can_afford(self, amount: int) -> bool:
        """Check if player can afford something"""
        return self.money >= amount
    
    def spend(self, amount: int) -> bool:
        """Spend money, returns True if successful"""
        if self.can_afford(amount):
            self.money -= amount
            self.total_spent += amount
            return True
        return False
    
    def earn(self, amount: int):
        """Earn money"""
        self.money += amount
        self.total_earned += amount
    
    def enemy_killed(self, reward: int):
        """Enemy killed, earn reward"""
        self.earn(reward)
        self.enemies_killed += 1
    
    def enemy_reached_end(self, damage: int = 1):
        """Enemy reached the end, lose lives"""
        self.lives -= damage
        if self.lives < 0:
            self.lives = 0
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.lives <= 0
    
    def wave_completed(self):
        """Wave finished - could give wave clear bonus here"""
        self.waves_completed += 1
        # Wave clear bonus
        bonus = 10 + self.waves_completed * 5
        self.earn(bonus)
    
    def reset(self):
        """Reset for new game"""
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.total_earned = 0
        self.total_spent = 0
        self.enemies_killed = 0
        self.waves_completed = 0
