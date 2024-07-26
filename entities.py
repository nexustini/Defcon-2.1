import pygame

# Define colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 3
        self.icbm_count = 3

    def hit(self, is_icbm):
        if is_icbm:
            self.health = 0
        else:
            self.health -= 1
        return self.health <= 0

class Missile:
    def __init__(self, start_city, target_city, is_icbm=False):
        self.start_pos = (start_city.x, start_city.y)
        self.target_pos = (target_city.x, target_city.y)
        self.position = list(self.start_pos)
        self.speed = 5 if not is_icbm else 10
        self.active = True
        self.rect = pygame.Rect(self.position[0] - 5, self.position[1] - 5, 10, 10)
        self.is_icbm = is_icbm

    def update(self):
        if self.active:
            dx = self.target_pos[0] - self.position[0]
            dy = self.target_pos[1] - self.position[1]
            dist = (dx**2 + dy**2) ** 0.5
            if dist < self.speed:
                self.position = list(self.target_pos)
                self.active = False
                return True  # Return True if missile reaches the target
            else:
                self.position[0] += self.speed * dx / dist
                self.position[1] += self.speed * dy / dist
            self.rect.center = self.position
        return False

    def draw(self, screen):
        if self.active:
            color = BLUE if self.is_icbm else RED
            pygame.draw.line(screen, color, self.start_pos, self.position, 2)

class AirDefense:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 50  # Reduced radius in pixels
        self.cooldown = 0
        self.max_cooldown = 60  # Frames between shots
        self.health = 2  # Health attribute
        self.target = None  # Store the currently targeted missile

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self):
        self.cooldown = self.max_cooldown

    def in_range(self, missile):
        distance = ((self.x - missile.position[0])**2 + (self.y - missile.position[1])**2)**0.5
        return distance <= self.range

    def take_damage(self, is_icbm=False):
        self.health -= 1
        if self.health <= 0:
            return True
        return False

    def target_missile(self, missile):
        self.target = missile
