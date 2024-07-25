import pygame
import random
from entities import City, Missile, AirDefense
import game_logic
import time

# Initialize Pygame
pygame.init()

# Initialize mixer
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)
BUTTON_TEXT_COLOR = GREEN

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEFCON 2.1 - Nexustini")

# Load background image
try:
    background = pygame.image.load('map.jpg')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Unable to load image: {e}")
    pygame.quit()
    exit()

# Load and play background music
try:
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)  # Loop indefinitely
except pygame.error as e:
    print(f"Unable to load or play background music: {e}")

# Volume control slider
slider_rect = pygame.Rect(WIDTH - 200, 20, 150, 20)
volume = 0.5  # Initial volume
pygame.mixer.music.set_volume(volume)

# Setup clock
clock = pygame.time.Clock()
FPS = 60

# Define polygon shapes for each continent (you'll need to adjust these)
continent_shapes = {
    "North America": [(100, 50), (300, 50), (300, 200), (100, 200)],
    "South America": [(150, 250), (300, 250), (300, 450), (150, 450)],
    "Europe": [(400, 50), (500, 50), (500, 150), (400, 150)],
    "Africa": [(400, 200), (500, 200), (500, 400), (400, 400)],
    "Asia": [(550, 50), (900, 50), (900, 300), (550, 300)],
    "Oceania": [(750, 350), (950, 350), (950, 500), (750, 500)]
}

# Game state
game_state = {
    'cities': {},
    'missiles': [],
    'score': 0,
    'player_score': 0,
    'ai_score': 0,
    'selected_country': None,
    'ai_country': None,
    'selected_city': None,
    'continent_boundaries': game_logic.continent_boundaries,
    'target_city': None,
    'user_turn': True,
    'game_over': False,
    'winner_country': None,
    'player_won': False,
    'health_display': None,
    'health_display_time': 0,
    'selected_missile_type': "regular",
    'start_time': 0,
    'total_time': 0,
    'player_air_defense': None,
    'ai_air_defense': None
}

# Font for UI
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 100)
small_font = pygame.font.SysFont(None, 24)  # New smaller font for the air defense button

def draw_ui():
    global slider_rect, volume
    score_text = font.render(f"Score: {game_state['score']}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if game_state['selected_country']:
        country_text = font.render(f"Your Continent: {game_state['selected_country']}", True, WHITE)
        screen.blit(country_text, (10, 50))
    if game_state['ai_country']:
        ai_text = font.render(f"AI Continent: {game_state['ai_country']}", True, WHITE)
        screen.blit(ai_text, (10, 90))
    if game_state['selected_city']:
        city_text = font.render(f"Selected City: ({game_state['selected_city'].x}, {game_state['selected_city'].y})", True, WHITE)
        screen.blit(city_text, (10, 130))
        icbm_text = font.render(f"ICBMs: {game_state['selected_city'].icbm_count}", True, WHITE)
        screen.blit(icbm_text, (10, 170))
    if game_state['target_city']:
        target_text = font.render(f"Target City: ({game_state['target_city'].x}, {game_state['target_city'].y})", True, WHITE)
        screen.blit(target_text, (10, 210))
        
    # Draw missile selection box
    missile_button = pygame.Rect(WIDTH - 200, HEIGHT - 80, 190, 40)  # Moved down
    pygame.draw.rect(screen, BUTTON_COLOR, missile_button)
    missile_type_text = font.render(f"{game_state['selected_missile_type'].upper()}", True, BUTTON_TEXT_COLOR)
    missile_text_rect = missile_type_text.get_rect(center=missile_button.center)
    screen.blit(missile_type_text, missile_text_rect)
    
    # Draw and label volume slider
    pygame.draw.rect(screen, BUTTON_COLOR, slider_rect)
    pygame.draw.rect(screen, WHITE, (slider_rect.x + int(slider_rect.width * volume), slider_rect.y, 10, slider_rect.height))
    volume_label = font.render("Game Volume", True, BUTTON_TEXT_COLOR)
    screen.blit(volume_label, (slider_rect.x, slider_rect.y - 30))

    if game_state['health_display']:
        screen.blit(game_state['health_display'], game_state['health_display'].get_rect(center=(WIDTH//2, HEIGHT - 60)))

    # Draw stopwatch
    elapsed_time = int(time.time() - game_state['start_time'])
    minutes, seconds = divmod(elapsed_time, 60)
    stopwatch_text = font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
    screen.blit(stopwatch_text, (WIDTH // 2 - stopwatch_text.get_width() // 2, 10))

    # Draw scoreboard
    player_score_text = font.render(f"{game_state.get('player_username', game_state['selected_country'])}: {game_state['player_score']}", True, WHITE)
    ai_score_text = font.render(f"{game_state['ai_country']}: {game_state['ai_score']}", True, WHITE)
    screen.blit(player_score_text, (10, HEIGHT - 80))
    screen.blit(ai_score_text, (10, HEIGHT - 40))

    # Draw air defense count
    air_defense_text = font.render(f"Air Defense: {'Available' if game_state['player_air_defense'] is None else 'Placed'}", True, WHITE)
    screen.blit(air_defense_text, (10, HEIGHT - 120))

    # Draw air defense placement button
    air_defense_button = pygame.Rect(WIDTH - 200, HEIGHT - 140, 190, 40)  # Moved up
    pygame.draw.rect(screen, BUTTON_COLOR, air_defense_button)
    air_defense_text = small_font.render("Place Air Defense", True, BUTTON_TEXT_COLOR)
    text_rect = air_defense_text.get_rect(center=air_defense_button.center)
    screen.blit(air_defense_text, text_rect)

def place_air_defense(game_state, x, y, is_player=True):
    if is_player and game_state['player_air_defense'] is None:
        game_state['player_air_defense'] = AirDefense(x, y)
    elif not is_player and game_state['ai_air_defense'] is None:
        game_state['ai_air_defense'] = AirDefense(x, y)

def point_in_polygon(x, y, polygon):
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def generate_cities(continent, num_cities=5):
    cities = []
    bounds = game_state['continent_boundaries'][continent]
    
    for _ in range(num_cities):
        x = random.randint(bounds[0][0], bounds[1][0])
        y = random.randint(bounds[0][1], bounds[1][1])
        cities.append(City(x, y))
    
    return cities

def game_loop():
    global volume
    placing_air_defense = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game
            elif game_state['game_over'] and event.type == pygame.MOUSEBUTTONDOWN:
                button_rect = game_logic.draw_end_game_screen(screen, font, background, game_state)
                if button_rect.collidepoint(event.pos):
                    return True  # Restart the game
            elif game_state['user_turn'] and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                air_defense_button = pygame.Rect(WIDTH - 200, HEIGHT - 120, 190, 50)
                
                if air_defense_button.collidepoint(x, y):
                    placing_air_defense = True
                elif placing_air_defense:
                    place_air_defense(game_state, x, y, is_player=True)
                    placing_air_defense = False
                elif slider_rect.collidepoint(x, y):
                    volume = (x - slider_rect.x) / slider_rect.width
                    pygame.mixer.music.set_volume(volume)
                elif WIDTH - 200 <= x <= WIDTH - 10 and HEIGHT - 60 <= y <= HEIGHT - 10:
                    game_state['selected_missile_type'] = "icbm" if game_state['selected_missile_type'] == "regular" else "regular"
                elif game_state['selected_city'] is None:
                    if game_logic.handle_city_selection(game_state):
                        continue
                elif game_state['target_city'] is None:
                    if game_logic.handle_target_city_selection(game_state):
                        is_icbm = game_state['selected_missile_type'] == "icbm"
                        if is_icbm and game_state['selected_city'].icbm_count > 0:
                            game_state['selected_city'].icbm_count -= 1
                            game_logic.launch_missile(game_state['selected_city'], game_state['target_city'], True, game_state)
                        else:
                            game_logic.launch_missile(game_state['selected_city'], game_state['target_city'], False, game_state)
                        game_state['selected_city'] = None
                        game_state['target_city'] = None
                        game_state['user_turn'] = False

        if not game_state['user_turn'] and not game_state['game_over']:
            game_logic.ai_turn(game_state)
            game_state['user_turn'] = True

        for missile in game_state['missiles'][:]:  # Create a copy of the list to iterate over
            if missile.update():
                # Missile has reached its target
                handle_missile_hit(game_state, missile)
            else:
                # Check for air defense interception
                if game_state['player_air_defense'] and is_ai_missile(game_state, missile):
                    if handle_air_defense(game_state['player_air_defense'], missile):
                        game_state['missiles'].remove(missile)
                        continue
                
                if game_state['ai_air_defense'] and is_player_missile(game_state, missile):
                    if handle_air_defense(game_state['ai_air_defense'], missile):
                        game_state['missiles'].remove(missile)
                        continue

        game_logic.handle_missile_collisions(game_state)

        screen.blit(background, (0, 0))
        if game_state['game_over']:
            game_logic.draw_end_game_screen(screen, font, background, game_state)
        else:
            for continent, city_list in game_state['cities'].items():
                for city in city_list:
                    color = GREEN if continent == game_state['selected_country'] else RED
                    pygame.draw.circle(screen, color, (city.x, city.y), 4)
            for missile in game_state['missiles']:
                missile.draw(screen)
            if game_state['player_air_defense']:
                pygame.draw.circle(screen, BLUE, (game_state['player_air_defense'].x, game_state['player_air_defense'].y), 6)
                pygame.draw.circle(screen, BLUE, (game_state['player_air_defense'].x, game_state['player_air_defense'].y), game_state['player_air_defense'].range, 1)
            if game_state['ai_air_defense']:
                pygame.draw.circle(screen, ORANGE, (game_state['ai_air_defense'].x, game_state['ai_air_defense'].y), 6)
                pygame.draw.circle(screen, ORANGE, (game_state['ai_air_defense'].x, game_state['ai_air_defense'].y), game_state['ai_air_defense'].range, 1)
            draw_ui()

        if game_state['health_display'] and pygame.time.get_ticks() - game_state['health_display_time'] < 2000:
            screen.blit(game_state['health_display'], game_state['health_display'].get_rect(center=(WIDTH//2, HEIGHT - 60)))
        else:
            game_state['health_display'] = None

        pygame.display.flip()
        clock.tick(FPS)

    return False  # Exit the game

def show_intro():
    title_text = title_font.render("DEFCON 2.1", True, RED)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))  # Moved up slightly
    
    credit_font = pygame.font.SysFont(None, 36)
    credit_text = credit_font.render("Made by Nexustini", True, WHITE)
    credit_rect = credit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))  # Positioned below title
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(200)
    
    start_time = pygame.time.get_ticks()
    title_duration = 3000  # 3 seconds for the title animation
    credit_duration = 2000  # 2 seconds for the credit animation
    total_duration = title_duration + credit_duration
    
    while pygame.time.get_ticks() - start_time < total_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        current_time = pygame.time.get_ticks() - start_time
        
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        
        if current_time < title_duration:
            # Animate title
            progress = min(current_time / title_duration, 1)
            y_pos = -50 + progress * (HEIGHT // 2 + 20)  # Adjusted for new position
            title_rect.centery = int(y_pos)
        else:
            # Keep title in final position
            title_rect.centery = HEIGHT // 2 - 30
        
        screen.blit(title_text, title_rect)
        
        if current_time > title_duration:
            # Animate credit
            credit_progress = min((current_time - title_duration) / credit_duration, 1)
            credit_x = WIDTH + 200 - credit_progress * (WIDTH + 200)  # Start off-screen and move left
            temp_credit_rect = credit_rect.copy()
            temp_credit_rect.centerx = int(credit_x)
            screen.blit(credit_text, temp_credit_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Hold the final frame for a moment
    pygame.time.wait(1000)

def main():
    while True:
        show_intro()
        game_logic.handle_country_selection(game_state, background)
        
        # Generate 5 cities for the player and AI in their respective continents
        game_state['cities'] = {
            game_state['selected_country']: generate_cities(game_state['selected_country']),
            game_state['ai_country']: generate_cities(game_state['ai_country'])
        }
        
        game_state['start_time'] = time.time()
        
        if not game_loop():
            break
        
        # Reset the game state for a new game
        game_state.update({
            'cities': {},
            'missiles': [],
            'score': 0,
            'player_score': 0,
            'ai_score': 0,
            'selected_country': None,
            'ai_country': None,
            'selected_city': None,
            'target_city': None,
            'user_turn': True,
            'game_over': False,
            'winner_country': None,
            'player_won': False,
            'health_display': None,
            'health_display_time': 0,
            'selected_missile_type': "regular",
            'start_time': 0,
            'total_time': 0,
            'player_air_defense': None,
            'ai_air_defense': None
        })

    pygame.quit()

def is_player_missile(game_state, missile):
    return any(city.x == missile.start_pos[0] and city.y == missile.start_pos[1] 
               for city in game_state['cities'][game_state['selected_country']])

def is_ai_missile(game_state, missile):
    return any(city.x == missile.start_pos[0] and city.y == missile.start_pos[1] 
               for city in game_state['cities'][game_state['ai_country']])

def handle_air_defense(air_defense, missile):
    air_defense.update()
    if air_defense.can_shoot() and air_defense.in_range(missile):
        if random.random() < 0.7:  # 70% chance to shoot down
            air_defense.shoot()
            return True
    return False

def handle_missile_hit(game_state, missile):
    is_player_missile = any(city.x == missile.start_pos[0] and city.y == missile.start_pos[1] 
                            for city in game_state['cities'][game_state['selected_country']])
    
    if is_player_missile:
        game_state['player_score'] += 1
    else:
        game_state['ai_score'] += 1
    
    game_state['score'] += 1
    for continent, city_list in game_state['cities'].items():
        for city in city_list[:]:  # Create a copy of the list to iterate over
            if (city.x, city.y) == missile.target_pos:
                if city.hit(missile.is_icbm):
                    city_list.remove(city)
                game_logic.check_game_over(game_state)
                if game_state['game_over']:
                    game_state['total_time'] = int(time.time() - game_state['start_time'])
                break
    game_state['missiles'].remove(missile)  # Remove the missile after it has hit

if __name__ == "__main__":
    main()
