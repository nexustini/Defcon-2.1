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

# Countries and their coordinate ranges (adjusted for the new map)
countries = {
    "North America": [(100, 100), (300, 250)],
    "South America": [(150, 300), (300, 500)],
    "Europe": [(450, 100), (550, 200)],
    "Africa": [(450, 250), (550, 450)],
    "Asia": [(600, 100), (900, 300)],
    "Oceania": [(800, 400), (1000, 550)]
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

def draw_ui():
    global slider_rect, volume
    score_text = font.render(f"Score: {game_state['score']}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if game_state['selected_country']:
        country_text = font.render(f"Your Country: {game_state['selected_country']}", True, WHITE)
        screen.blit(country_text, (10, 50))
    if game_state['ai_country']:
        ai_text = font.render(f"AI Country: {game_state['ai_country']}", True, WHITE)
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
    pygame.draw.rect(screen, BUTTON_COLOR, (WIDTH - 200, HEIGHT - 60, 190, 50))
    missile_type_text = font.render(f"{game_state['selected_missile_type'].upper()}", True, BUTTON_TEXT_COLOR)
    screen.blit(missile_type_text, (WIDTH - 190, HEIGHT - 55))
    
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
    player_score_text = font.render(f"{game_state['selected_country']}: {game_state['player_score']}", True, WHITE)
    ai_score_text = font.render(f"{game_state['ai_country']}: {game_state['ai_score']}", True, WHITE)
    screen.blit(player_score_text, (10, HEIGHT - 80))
    screen.blit(ai_score_text, (10, HEIGHT - 40))

    # Draw air defense count
    air_defense_text = font.render(f"Air Defense: {'Available' if game_state['player_air_defense'] is None else 'Placed'}", True, WHITE)
    screen.blit(air_defense_text, (10, HEIGHT - 120))

    # Draw air defense placement button
    air_defense_button = pygame.Rect(WIDTH - 200, HEIGHT - 120, 190, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, air_defense_button)
    air_defense_text = font.render("Place Air Defense", True, BUTTON_TEXT_COLOR)
    screen.blit(air_defense_text, (WIDTH - 190, HEIGHT - 115))

def place_air_defense(game_state, x, y, is_player=True):
    if is_player and game_state['player_air_defense'] is None:
        game_state['player_air_defense'] = AirDefense(x, y)
    elif not is_player and game_state['ai_air_defense'] is None:
        game_state['ai_air_defense'] = AirDefense(x, y)

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
            for country, city_list in game_state['cities'].items():
                for city in city_list:
                    color = GREEN if country == game_state['selected_country'] else RED
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

def generate_cities(country, num_cities=5):
    cities = []
    coords = countries[country]
    for _ in range(num_cities):
        x = random.randint(coords[0][0], coords[1][0])
        y = random.randint(coords[0][1], coords[1][1])
        cities.append(City(x, y))
    return cities

def show_intro():
    title_text = title_font.render("DEFCON 2.1", True, RED)
    text_rect = title_text.get_rect(center=(WIDTH // 2, -50))
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(200)
    
    start_time = pygame.time.get_ticks()
    duration = 3000  # 3 seconds for the animation
    
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        progress = (pygame.time.get_ticks() - start_time) / duration
        y_pos = -50 + progress * (HEIGHT // 2 + 50)
        text_rect.centery = int(y_pos)
        
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(title_text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Hold the title in the center for a moment
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
    for country, city_list in game_state['cities'].items():
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
