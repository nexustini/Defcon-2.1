import pygame
from constants import WIDTH, HEIGHT

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
            color = (0, 0, 255) if self.is_icbm else (255, 0, 0)
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

class Battleship:
    def __init__(self, x, y, is_player):
        self.x = x
        self.y = y
        self.health = 10
        self.max_health = 10
        self.speed = 1  # Slow movement speed
        self.is_player = is_player
        self.cooldown = 0
        self.max_cooldown = 30  # Frames between shots
        self.width = 20
        self.height = 10

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        # Ensure the battleship stays within the screen boundaries
        self.x = max(self.width // 2, min(new_x, WIDTH - self.width // 2))
        self.y = max(self.height // 2, min(new_y, HEIGHT - self.height // 2))

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self):
        self.cooldown = self.max_cooldown

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True
        return False

    def draw(self, screen):
        color = (0, 0, 255) if self.is_player else (255, 0, 0)  # Blue for player, Red for AI
        pygame.draw.rect(screen, color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        
        # Draw health bar
        health_bar_width = 30
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (self.x - health_bar_width // 2, self.y - 15, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - health_bar_width // 2, self.y - 15, int(health_bar_width * health_ratio), health_bar_height))

    def get_position(self):
        return (self.x, self.y)

class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, is_player):
        self.x = start_x
        self.y = start_y
        self.speed = 5
        dx = target_x - start_x
        dy = target_y - start_y
        dist = (dx**2 + dy**2)**0.5
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed
        self.is_player = is_player

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def check_collision(self, ship):
        # Check if the bullet is within the ship's hitbox
        return abs(self.x - ship.x) < ship.width // 2 and abs(self.y - ship.y) < ship.height // 2

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def draw(self, screen):
        color = BLUE if self.is_player else RED
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)
