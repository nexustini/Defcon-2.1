import pygame
import random
from pygame.math import Vector2
from constants import WIDTH, HEIGHT
from entities import City, Missile, AirDefense, Battleship, Bullet
import game_logic
import time

# Initialize Pygame
pygame.init()

# Initialize mixer
pygame.mixer.init()

# Constants
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

# Load explosion sound
try:
    explosion_sound = pygame.mixer.Sound('explosion_sound.wav')
except pygame.error as e:
    print(f"Unable to load explosion sound: {e}")
    explosion_sound = None

# Global variable for SFX volume
global sfx_volume
sfx_volume = 0.5  # Initial sound effect volume (50%)

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
    'selected_missile_type': "GGM",
    'start_time': 0,
    'total_time': 0,
    'player_air_defense': None,
    'ai_air_defense': None,
    'explosion_effects': {},
    'sfx_volume': 0.5,
    'player_battleships': [],
    'ai_battleships': [],
    'bullets': []
}

# Font for UI
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 100)
small_font = pygame.font.SysFont(None, 24)  # New smaller font for the air defense button

# Global variables for boundary editing
dragging = False
dragged_point = None
dragged_continent = None

def draw_hamburger_menu(screen, x, y, width, height):
    bar_height = height // 5
    gap = (height - 3 * bar_height) // 2
    for i in range(3):
        pygame.draw.rect(screen, WHITE, (x, y + i * (bar_height + gap), width, bar_height))

def draw_open_menu(screen, menu_rect):
    pygame.draw.rect(screen, BUTTON_COLOR, menu_rect)
    
    button_height = 40
    gap = 5
    buttons = [
        ("Missile Type", lambda: toggle_missile_type(game_state)),
        ("Place Air Defense", lambda: toggle_air_defense_placement(game_state)),
        ("Place Battleship", lambda: toggle_battleship_placement(game_state))
    ]
    
    for i, (text, _) in enumerate(buttons):
        button_rect = pygame.Rect(menu_rect.x, menu_rect.y + i * (button_height + gap), menu_rect.width, button_height)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR, button_rect)
        text_surf = small_font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)

    return [pygame.Rect(menu_rect.x, menu_rect.y + i * (button_height + gap), menu_rect.width, button_height) for i in range(len(buttons))]

def toggle_missile_type(game_state):
    game_state['selected_missile_type'] = "icbm" if game_state['selected_missile_type'] == "GGM" else "GGM"

def toggle_air_defense_placement(game_state):
    return game_state['player_air_defense'] is None

def toggle_battleship_placement(game_state):
    return len(game_state['player_battleships']) < 3

def draw_ui(game_state):
    global volume
    
    # Draw score
    score_text = font.render(f"Score: {game_state['score']}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw country information
    if game_state['selected_country']:
        country_text = font.render(f"Your Continent: {game_state['selected_country']}", True, WHITE)
        screen.blit(country_text, (10, 50))
    if game_state['ai_country']:
        ai_text = font.render(f"AI Continent: {game_state['ai_country']}", True, WHITE)
        screen.blit(ai_text, (10, 90))
        
    # Add missile type label
    missile_type = "GGM" if game_state['selected_missile_type'] == "GGM" else "ICBM"
    missile_text = font.render(f"Selected Missile: {missile_type}", True, WHITE)
    screen.blit(missile_text, (10, 130))
    
    # Adjust the y-coordinate of the following elements
    y_offset = 170
    
    # Draw selected city information
    if game_state['selected_city']:
        city_text = font.render(f"Selected City: ({game_state['selected_city'].x}, {game_state['selected_city'].y})", True, WHITE)
        screen.blit(city_text, (10, y_offset))
        icbm_text = font.render(f"ICBMs: {game_state['selected_city'].icbm_count}", True, WHITE)
        screen.blit(icbm_text, (10, y_offset + 40))
        y_offset += 80
    
    # Draw target city information
    if game_state['target_city']:
        target_text = font.render(f"Target City: ({game_state['target_city'].x}, {game_state['target_city'].y})", True, WHITE)
        screen.blit(target_text, (10, y_offset))
    
    # Draw and label volume slider for music
    pygame.draw.rect(screen, BUTTON_COLOR, slider_rect)
    pygame.draw.rect(screen, WHITE, (slider_rect.x + int(slider_rect.width * volume), slider_rect.y, 10, slider_rect.height))
    volume_label = font.render("Music Volume", True, BUTTON_TEXT_COLOR)
    volume_label_rect = volume_label.get_rect(midtop=(slider_rect.x + slider_rect.width // 2, slider_rect.y - 30))
    screen.blit(volume_label, volume_label_rect)

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

    # Draw air defense status
    air_defense_text = font.render(f"Air Defense: {'Placed' if game_state['player_air_defense'] else 'Available'}", True, WHITE)
    screen.blit(air_defense_text, (10, HEIGHT - 120))

    # Draw turn indicator
    turn_text = font.render("Your Turn" if game_state['user_turn'] else "AI Turn", True, GREEN if game_state['user_turn'] else RED)
    screen.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, HEIGHT - 40))

    # Draw health display (for temporary messages)
    if game_state['health_display']:
        screen.blit(game_state['health_display'], game_state['health_display'].get_rect(center=(WIDTH//2, HEIGHT - 60)))

    # Draw selected battleship indicator
    if game_state.get('selected_battleship'):
        selected_text = font.render("Selected Battleship", True, YELLOW)
        screen.blit(selected_text, (WIDTH - 220, HEIGHT - 240))

    # Draw remaining cities count
    player_cities = len(game_state['cities'][game_state['selected_country']])
    ai_cities = len(game_state['cities'][game_state['ai_country']])
    cities_text = font.render(f"Your Cities: {player_cities} | AI Cities: {ai_cities}", True, WHITE)
    screen.blit(cities_text, (WIDTH // 2 - cities_text.get_width() // 2, 50))

    # Draw cursor coordinates
    cursor_pos = pygame.mouse.get_pos()
    coord_text = f"Cursor: ({cursor_pos[0]}, {cursor_pos[1]})"
    coord_label = font.render(coord_text, True, WHITE)
    coord_label_rect = coord_label.get_rect(midtop=(slider_rect.x + slider_rect.width // 2, slider_rect.bottom + 10))
    screen.blit(coord_label, coord_label_rect)

    # Draw hamburger menu
    menu_button_rect = pygame.Rect(WIDTH - 50, HEIGHT - 50, 40, 40)
    draw_hamburger_menu(screen, menu_button_rect.x + 5, menu_button_rect.y + 5, 30, 30)
    
    if game_state.get('menu_open', False):
        menu_rect = pygame.Rect(WIDTH - 220, HEIGHT - 250, 200, 200)
        button_rects = draw_open_menu(screen, menu_rect)
        game_state['menu_button_rects'] = button_rects

def is_player_missile(game_state, missile):
    return any(city.x == missile.start_pos[0] and city.y == missile.start_pos[1] 
               for city in game_state['cities'][game_state['selected_country']])

def is_ai_missile(game_state, missile):
    return any(city.x == missile.start_pos[0] and city.y == missile.start_pos[1] 
               for city in game_state['cities'][game_state['ai_country']])

def handle_air_defense(air_defense, missile):
    air_defense.update()
    if air_defense.can_shoot() and air_defense.in_range(missile):
        air_defense.target_missile(missile)  # Set the current target
        if random.random() < 0.7:  # 70% chance to shoot down
            air_defense.shoot()
            if is_player_missile(game_state, missile):
                # AI air defense takes damage from player missiles
                if air_defense.take_damage():
                    # AI air defense is destroyed
                    game_state['ai_air_defense'] = None
                    return True
            else:
                # Player air defense takes damage from AI missiles
                if air_defense.take_damage(is_icbm=missile.is_icbm):
                    # Player air defense is destroyed
                    game_state['player_air_defense'] = None
                    return True
            return True
    else:
        air_defense.target = None  # Clear the target if not in range or can't shoot
    return False

def handle_missile_hit(game_state, missile):
    global sfx_volume
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
                    # Create the explosion effect
                    game_state['explosion_effects'][(city.x, city.y)] = {
                        'radius': 0,
                        'max_radius': 50,
                        'fade_rate': 2,
                        'creation_time': pygame.time.get_ticks()
                    }
                    
                    # Play the explosion sound
                    if explosion_sound:
                        explosion_sound.set_volume(sfx_volume)
                        explosion_sound.play()
                        
                game_logic.check_game_over(game_state)
                if game_state['game_over']:
                    game_state['total_time'] = int(time.time() - game_state['start_time'])
                break
    
    game_state['missiles'].remove(missile)  # Remove the missile after it has hit

def handle_boundary_editing(event, game_state):
    global dragging, dragged_point, dragged_continent

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left mouse button
            mouse_pos = Vector2(event.pos)
            for continent, points in game_state['continent_boundaries'].items():
                for i, point in enumerate(points):
                    if Vector2(point).distance_to(mouse_pos) < 10:
                        dragging = True
                        dragged_point = i
                        dragged_continent = continent
                        break
                if dragging:
                    break
    
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:  # Left mouse button
            dragging = False
            dragged_point = None
            dragged_continent = None
    
    elif event.type == pygame.MOUSEMOTION:
        if dragging:
            new_pos = event.pos
            game_state['continent_boundaries'][dragged_continent][dragged_point] = new_pos

def draw_edit_ui(screen, font):
    save_button = pygame.Rect(WIDTH - 100, 10, 90, 30)
    pygame.draw.rect(screen, (0, 255, 0), save_button)
    save_text = font.render("Save", True, (0, 0, 0))
    screen.blit(save_text, (WIDTH - 85, 15))
    return save_button

def draw_dev_mode_watermark(screen):
    font = pygame.font.SysFont(None, 100)  # Large font for the watermark
    watermark = font.render("DEV MODE", True, (255, 0, 0, 128))  # Red color with some transparency
    watermark_rect = watermark.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Create a surface for the watermark with per-pixel alpha
    watermark_surface = pygame.Surface(watermark.get_size(), pygame.SRCALPHA)
    watermark_surface.fill((255, 0, 0, 64))  # Red with 25% opacity
    
    # Blit the text onto the surface
    watermark_surface.blit(watermark, (0, 0))
    
    # Blit the surface onto the screen
    screen.blit(watermark_surface, watermark_rect)

def game_loop():
    global volume, sfx_volume, dragging, dragged_point, dragged_continent
    placing_air_defense = False
    placing_battleship = False
    selected_battleship = None
    editing_mode = False
    dragging = False
    dragged_point = None
    dragged_continent = None
    running = True
    menu_button_rect = pygame.Rect(WIDTH - 50, HEIGHT - 50, 40, 40)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game
            elif game_state['game_over'] and event.type == pygame.MOUSEBUTTONDOWN:
                button_rect = game_logic.draw_end_game_screen(screen, font, background, game_state)
                if button_rect.collidepoint(event.pos):
                    return True  # Restart the game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    editing_mode = not editing_mode
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN) and selected_battleship:
                    dx = event.key in (pygame.K_LEFT, pygame.K_RIGHT)
                    dy = event.key in (pygame.K_UP, pygame.K_DOWN)
                    direction = -1 if event.key in (pygame.K_LEFT, pygame.K_UP) else 1
                    selected_battleship.move(dx * direction, dy * direction)
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    selected_battleship = None
            elif editing_mode:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = Vector2(event.pos)
                        save_button = draw_edit_ui(screen, font)
                        if save_button.collidepoint(event.pos):
                            game_logic.save_continent_boundaries()
                            game_logic.continent_boundaries = game_state['continent_boundaries']
                            print("Continent boundaries saved!")
                        else:
                            for continent, points in game_state['continent_boundaries'].items():
                                for i, point in enumerate(points):
                                    if Vector2(point).distance_to(mouse_pos) < 10:
                                        dragging = True
                                        dragged_point = i
                                        dragged_continent = continent
                                        break
                                if dragging:
                                    break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        dragging = False
                        dragged_point = None
                        dragged_continent = None
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        new_pos = event.pos
                        game_state['continent_boundaries'][dragged_continent][dragged_point] = new_pos
            elif game_state['user_turn'] and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                if menu_button_rect.collidepoint(x, y):
                    game_state['menu_open'] = not game_state.get('menu_open', False)
                elif game_state.get('menu_open', False):
                    for i, button_rect in enumerate(game_state.get('menu_button_rects', [])):
                        if button_rect.collidepoint(x, y):
                            if i == 0:  # Missile Type
                                toggle_missile_type(game_state)
                            elif i == 1:  # Place Air Defense
                                placing_air_defense = toggle_air_defense_placement(game_state)
                            elif i == 2:  # Place Battleship
                                placing_battleship = toggle_battleship_placement(game_state)
                            game_state['menu_open'] = False
                            break
                    else:
                        game_state['menu_open'] = False
                elif slider_rect.collidepoint(x, y):
                    volume = (x - slider_rect.x) / slider_rect.width
                    pygame.mixer.music.set_volume(volume)
                elif placing_air_defense:
                    game_state['player_air_defense'] = AirDefense(x, y)
                    placing_air_defense = False
                elif placing_battleship:
                    if game_logic.handle_battleship_placement(game_state, x, y):
                        placing_battleship = False
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
                else:
                    for battleship in game_state['player_battleships']:
                        if abs(battleship.x - x) < 10 and abs(battleship.y - y) < 5:
                            selected_battleship = battleship
                            break

        if editing_mode and dragging:
            mouse_pos = pygame.mouse.get_pos()
            game_state['continent_boundaries'][dragged_continent][dragged_point] = mouse_pos

        if not game_state['user_turn'] and not game_state['game_over']:
            game_logic.ai_turn(game_state)
            game_state['user_turn'] = True

        # Update missiles
        for missile in game_state['missiles'][:]:
            if missile.update():
                handle_missile_hit(game_state, missile)
            else:
                if game_state['player_air_defense'] and is_ai_missile(game_state, missile):
                    if handle_air_defense(game_state['player_air_defense'], missile):
                        game_state['missiles'].remove(missile)
                        if game_state['player_air_defense']:
                            game_state['player_air_defense'].target = None
                        continue
                
                if game_state['ai_air_defense'] and is_player_missile(game_state, missile):
                    if handle_air_defense(game_state['ai_air_defense'], missile):
                        game_state['missiles'].remove(missile)
                        if game_state['ai_air_defense']:
                            game_state['ai_air_defense'].target = None
                        continue

        # Update bullets
        for bullet in game_state['bullets'][:]:
            bullet.update()
            if bullet.is_out_of_bounds():
                game_state['bullets'].remove(bullet)

        game_logic.handle_missile_collisions(game_state)
        game_logic.handle_battleship_combat(game_state)

        screen.blit(background, (0, 0))
        if game_state['game_over']:
            game_logic.draw_end_game_screen(screen, font, background, game_state)
        else:
            # Draw continent boundaries
            for continent, bounds in game_state['continent_boundaries'].items():
                color = GREEN if continent == game_state['selected_country'] else RED
                pygame.draw.polygon(screen, color, bounds, 2)
                
                poly_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(poly_surface, (*color, 50), bounds)
                screen.blit(poly_surface, (0, 0))

            # Draw cities
            for continent, city_list in game_state['cities'].items():
                for city in city_list:
                    color = GREEN if continent == game_state['selected_country'] else RED
                    pygame.draw.circle(screen, color, (city.x, city.y), 4)
            
            # Draw missiles
            for missile in game_state['missiles']:
                missile.draw(screen)
            
            # Draw air defenses
            if game_state['player_air_defense']:
                ad = game_state['player_air_defense']
                pygame.draw.circle(screen, BLUE, (ad.x, ad.y), 6)
                pygame.draw.circle(screen, BLUE, (ad.x, ad.y), ad.range, 1)
                if ad.target:
                    pygame.draw.line(screen, BLUE, (ad.x, ad.y), ad.target.position, 2)
            
            if game_state['ai_air_defense']:
                ad = game_state['ai_air_defense']
                pygame.draw.circle(screen, ORANGE, (ad.x, ad.y), 6)
                pygame.draw.circle(screen, ORANGE, (ad.x, ad.y), ad.range, 1)
                if ad.target:
                    pygame.draw.line(screen, ORANGE, (ad.x, ad.y), ad.target.position, 2)

            # Draw battleships
            for battleship in game_state['player_battleships']:
                battleship.draw(screen)
            for battleship in game_state['ai_battleships']:
                battleship.draw(screen)

            # Draw bullets
            for bullet in game_state['bullets']:
                bullet.draw(screen)

            # Draw and update the explosion effects
            for position, effect in list(game_state['explosion_effects'].items()):
                x, y = position
                radius = effect['radius']
                max_radius = effect['max_radius']
                fade_rate = effect['fade_rate']
                creation_time = effect['creation_time']
                
                effect['radius'] = min(radius + 2, max_radius)
                
                if pygame.time.get_ticks() - creation_time > 5000:
                    effect['radius'] = max(0, radius - fade_rate)
                    if effect['radius'] == 0:
                        del game_state['explosion_effects'][position]
                
                pygame.draw.circle(screen, WHITE, (x, y), int(effect['radius']), 1)
            
            draw_ui(game_state)

            if editing_mode:
                save_button = draw_edit_ui(screen, font)
                for continent, bounds in game_state['continent_boundaries'].items():
                    for point in bounds:
                        pygame.draw.circle(screen, YELLOW, point, 5)
                        pygame.draw.circle(screen, BLACK, point, 3)
                
                # Draw the DEV MODE watermark
                draw_dev_mode_watermark(screen)

        if game_state['health_display'] and pygame.time.get_ticks() - game_state['health_display_time'] < 2000:
            screen.blit(game_state['health_display'], game_state['health_display'].get_rect(center=(WIDTH//2, HEIGHT - 60)))
        else:
            game_state['health_display'] = None

        pygame.display.flip()
        clock.tick(FPS)
    return False  # Exit the game

def show_intro():
    title_text = title_font.render("DEFCON 2.1", True, RED)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    
    credit_font = pygame.font.SysFont(None, 36)
    credit_text = credit_font.render("Made by Nexustini", True, WHITE)
    credit_rect = credit_text.get_rect(center=(WIDTH // 2, title_rect.bottom + 50))
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(200)
    
    start_time = pygame.time.get_ticks()
    title_duration = 3000
    credit_duration = 2000
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
            progress = min(current_time / title_duration, 1)
            y_pos = -50 + progress * (HEIGHT // 2 - 30)
            title_rect.centery = int(y_pos)
        else:
            title_rect.centery = HEIGHT // 2 - 30

        screen.blit(title_text, title_rect)
        
        if current_time > title_duration:
            credit_progress = min((current_time - title_duration) / credit_duration, 1)
            credit_y = HEIGHT + 100 - credit_progress * (HEIGHT + 100 - title_rect.bottom - 50)
            temp_credit_rect = credit_rect.copy()
            temp_credit_rect.centery = int(credit_y)
            screen.blit(credit_text, temp_credit_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.time.wait(1000)

def main():
    while True:
        show_intro()
        game_logic.handle_country_selection(game_state, background)
        
        game_state['cities'] = {
            game_state['selected_country']: game_logic.generate_cities(game_state['selected_country']),
            game_state['ai_country']: game_logic.generate_cities(game_state['ai_country'])
        }
        
        ai_continent_coords = game_state['continent_boundaries'][game_state['ai_country']]
        for _ in range(3):
            x = random.randint(min(p[0] for p in ai_continent_coords), max(p[0] for p in ai_continent_coords))
            y = random.randint(min(p[1] for p in ai_continent_coords), max(p[1] for p in ai_continent_coords))
            game_state['ai_battleships'].append(Battleship(x, y, False))
        
        game_state['start_time'] = time.time()
        
        if not game_loop():
            break
        
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
            'selected_missile_type': "GGM",
            'start_time': 0,
            'total_time': 0,
            'player_air_defense': None,
            'ai_air_defense': None,
            'explosion_effects': {},
            'player_battleships': [],
            'ai_battleships': [],
            'bullets': []
        })

    pygame.quit()

if __name__ == "__main__":
    main()
