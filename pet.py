import time

class Pet:
    def __init__(self):
        self.hunger = 100
        self.energy = 100
        self.happiness = 100
        self.health = 5
        self.age = 0
        self.last_decay = time.time()
        self.last_age_up = time.time()

    def decay_stats(self):
        now = time.time()
        if now - self.last_decay >= 120:
            self.hunger -= 5
            self.happiness -= 5
            self.last_decay = now
            self.check_health()

        if now - self.last_age_up >= 300:
            self.age += 1
            self.last_age_up = now

    def check_health(self):
        if self.hunger <= 0 or self.happiness <= 0 or self.energy <= 0:
            self.health -= 1
            self.hunger = max(self.hunger, 0)
            self.happiness = max(self.happiness, 0)
            self.energy = max(self.energy, 0)

    def feed(self):
        self.hunger = min(self.hunger + 5, 100)

    def play(self):
        self.happiness = min(self.happiness + 5, 100)
        self.hunger = max(self.hunger - 5, 0)
        self.energy = max(self.energy - 5, 0)

    def rest(self):
        self.energy = min(self.energy + 5, 100)
