import random
import pygame
import json
from entities import City, Missile, AirDefense, Battleship, Bullet
from constants import WIDTH, HEIGHT
from pygame.math import Vector2

dragging = False
dragged_point = None
dragged_continent = None

# Define the continent boundaries
continent_boundaries = {
    "North America": [
        (183, 147), (204, 162), (228, 180), (258, 205), (289, 231), (320, 260), (341, 288),
        (200, 130), (240, 170), (280, 210), (320, 250), (360, 290), (400, 330), (440, 370),
        (480, 410), (520, 450), (560, 490)
    ],
    "South America": [
        (378, 402), (395, 435), (412, 468), (429, 501), (445, 534), (462, 547),
        (390, 370), (420, 400), (450, 430), (480, 460), (510, 490), (540, 520), (570, 550),
        (600, 580), (630, 610), (660, 640)
    ],
    "Europe": [
        (624, 171), (648, 185), (672, 199), (696, 213), (720, 227), (743, 248),
        (610, 150), (650, 180), (690, 210), (730, 240), (770, 270), (810, 300), (850, 330),
        (890, 360), (930, 390), (970, 420)
    ],
    "Africa": [
        (610, 305), (636, 345), (662, 385), (688, 425), (714, 465), (740, 485), (764, 503),
        (590, 280), (630, 320), (670, 360), (710, 400), (750, 440), (790, 480), (830, 520),
        (870, 560), (910, 600), (950, 640)
    ],
    "Asia": [
        (774, 163), (824, 189), (874, 215), (924, 241), (974, 267), (1024, 293), (1058, 299),
        (800, 140), (850, 170), (900, 200), (950, 230), (1000, 260), (1050, 290), (1100, 320),
        (1150, 350), (1200, 380), (1250, 410)
    ],
    "Oceania": [
        (987, 406), (1027, 423), (1067, 440), (1107, 457), (1147, 474), (1192, 489),
        (970, 380), (1020, 410), (1070, 440), (1120, 470), (1170, 500), (1220, 530), (1270, 560),
        (1320, 590), (1370, 620), (1420, 650)
    ]
}

def save_continent_boundaries():
    with open('continent_boundaries.json', 'w') as f:
        json.dump(continent_boundaries, f)

def load_continent_boundaries():
    global continent_boundaries
    try:
        with open('continent_boundaries.json', 'r') as f:
            continent_boundaries = json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, use the default boundaries
        pass

# Call this function at the start of the game
load_continent_boundaries()

def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def generate_cities(continent):
    cities = []
    bounds = continent_boundaries[continent]
    
    for _ in range(5):
        while True:
            x = random.randint(min(p[0] for p in bounds), max(p[0] for p in bounds))
            y = random.randint(min(p[1] for p in bounds), max(p[1] for p in bounds))
            if point_inside_polygon(x, y, bounds):
                cities.append(City(x, y))
                break
    
    return cities

def draw_end_game_screen(screen, font, background, game_state):
    screen.blit(background, (0, 0))

    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {game_state['score']}", True, (255, 255, 255))
    winner_text = font.render(f"Winner: {game_state['winner_country']}", True, (255, 255, 0))

    # Add total time text
    minutes, seconds = divmod(game_state['total_time'], 60)
    time_text = font.render(f"Total Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))

    player_score_text = font.render(f"{game_state['player_username']}: {game_state['player_score']}", True, (255, 255, 255))
    ai_score_text = font.render(f"{game_state['ai_country']}: {game_state['ai_score']}", True, (255, 255, 255))

    screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 150))
    screen.blit(score_text, (screen.get_width() // 2 - score_text.get_width() // 2, 200))
    screen.blit(winner_text, (screen.get_width() // 2 - winner_text.get_width() // 2, 250))
    screen.blit(time_text, (screen.get_width() // 2 - time_text.get_width() // 2, 300))
    screen.blit(player_score_text, (screen.get_width() // 2 - player_score_text.get_width() // 2, 350))
    screen.blit(ai_score_text, (screen.get_width() // 2 - ai_score_text.get_width() // 2, 400))

    # Create "Play Again" button with the same style as country buttons
    button_width = 200
    button_height = 50
    button_rect = pygame.Rect((screen.get_width() - button_width) // 2, 450, button_width, button_height)
    pygame.draw.rect(screen, (100, 100, 255), button_rect)  # Light blue color

    button_text = font.render("Play Again", True, (255, 255, 255))
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    pygame.display.flip()
    return button_rect

def ask_for_username(screen, font):
    username = ""
    input_rect = pygame.Rect((screen.get_width() - 200) // 2, 400, 200, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return username
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
        
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)
        username_surface = font.render(username, True, (255, 255, 255))
        screen.blit(username_surface, (input_rect.x + 5, input_rect.y + 5))
        
        prompt_text = font.render("Enter your username:", True, (255, 255, 255))
        screen.blit(prompt_text, ((screen.get_width() - prompt_text.get_width()) // 2, 350))
        
        pygame.display.flip()

def handle_country_selection(game_state, background):
    screen = pygame.display.get_surface()
    font = pygame.font.SysFont(None, 36)
    selected_country = None
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))

    # Create buttons for each continent
    button_height = 50
    button_width = 200
    start_y = 100
    buttons = []
    for i, continent in enumerate(continent_boundaries.keys()):
        button_rect = pygame.Rect((screen.get_width() - button_width) // 2,
                                  start_y + i * (button_height + 10),
                                  button_width, button_height)
        buttons.append((button_rect, continent))

    while selected_country is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, continent in buttons:
                    if button.collidepoint(event.pos):
                        selected_country = continent
                        game_state['selected_country'] = continent
                        game_state['ai_country'] = random.choice([c for c in continent_boundaries if c != continent])
                        
                        # Prompt for username
                        username = ask_for_username(screen, font)
                        game_state['player_username'] = username
                        
                        break

        # Draw background
        screen.blit(background, (0, 0))

        # Draw semi-transparent overlay
        screen.blit(overlay, (0, 0))

        # Draw buttons and continent names
        for button, continent in buttons:
            pygame.draw.rect(screen, (100, 100, 255), button)  # Light blue color
            text = font.render(continent, True, (255, 255, 255))
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)

        instruction_text = font.render("Select your continent", True, (255, 255, 255))
        screen.blit(instruction_text, ((screen.get_width() - instruction_text.get_width()) // 2, 50))

        pygame.display.flip()

def handle_city_selection(game_state):
    screen = pygame.display.get_surface()
    for continent, city_list in game_state['cities'].items():
        for city in city_list:
            if pygame.mouse.get_pos()[0] in range(city.x - 5, city.x + 5) and pygame.mouse.get_pos()[1] in range(city.y - 5, city.y + 5):
                if continent == game_state['selected_country']:
                    game_state['selected_city'] = city
                    return True
    return False

def handle_target_city_selection(game_state):
    screen = pygame.display.get_surface()
    for continent, city_list in game_state['cities'].items():
        for city in city_list:
            if pygame.mouse.get_pos()[0] in range(city.x - 5, city.x + 5) and pygame.mouse.get_pos()[1] in range(city.y - 5, city.y + 5):
                if continent != game_state['selected_country']:
                    game_state['target_city'] = city
                    return True
    return False

def launch_missile(start_city, target_city, is_icbm, game_state):
    missile = Missile(start_city, target_city, is_icbm)
    game_state['missiles'].append(missile)

def ai_turn(game_state):
    # Get a list of available cities that are not the target city
    available_cities = [city for city_list in game_state['cities'].values() 
                        for city in city_list if city != game_state['target_city']]
    
    # Filter out the AI's own cities
    available_enemy_cities = [city for city in available_cities 
                              if city not in game_state['cities'][game_state['ai_country']]]
    
    if available_enemy_cities:
        target_city = random.choice(available_enemy_cities)
        ai_cities = game_state['cities'][game_state['ai_country']]
        if ai_cities:
            start_city = random.choice(ai_cities)
            launch_missile(start_city, target_city, False, game_state)

    # Place AI air defense
    if game_state['ai_air_defense'] is None and random.random() < 0.2:  # 20% chance to place air defense
        ai_continent_coords = game_state['continent_boundaries'][game_state['ai_country']]
        x = random.randint(min(p[0] for p in ai_continent_coords), max(p[0] for p in ai_continent_coords))
        y = random.randint(min(p[1] for p in ai_continent_coords), max(p[1] for p in ai_continent_coords))
        game_state['ai_air_defense'] = AirDefense(x, y)

    # Move AI battleships
    for battleship in game_state['ai_battleships']:
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        battleship.move(dx, dy)

def check_game_over(game_state):
    player_cities = game_state['cities'][game_state['selected_country']]
    ai_cities = game_state['cities'][game_state['ai_country']]

    if len(player_cities) == 0 or len(ai_cities) == 0:
        game_state['game_over'] = True
        
        if len(player_cities) == 0 and len(ai_cities) == 0:
            if game_state['player_score'] > game_state['ai_score']:
                game_state['winner_country'] = game_state['player_username']
                game_state['player_won'] = True
            elif game_state['ai_score'] > game_state['player_score']:
                game_state['winner_country'] = game_state['ai_country']
                game_state['player_won'] = False
            else:
                game_state['winner_country'] = "Tie"
                game_state['player_won'] = False
        elif len(player_cities) == 0:
            game_state['winner_country'] = game_state['ai_country']
            game_state['player_won'] = False
        else:
            game_state['winner_country'] = game_state['player_username']
            game_state['player_won'] = True

def handle_missile_collisions(game_state):
    for missile in game_state['missiles'][:]:
        for other_missile in game_state['missiles'][:]:
            if missile != other_missile and missile.rect.colliderect(other_missile.rect):
                if missile in game_state['missiles']:
                    game_state['missiles'].remove(missile)
                if other_missile in game_state['missiles']:
                    game_state['missiles'].remove(other_missile)
                break

def handle_battleship_placement(game_state, x, y):
    if len(game_state['player_battleships']) < 3:  # Limit to 3 battleships
        game_state['player_battleships'].append(Battleship(x, y, True))
        return True
    return False

def handle_battleship_combat(game_state):
    for player_ship in game_state['player_battleships']:
        for ai_ship in game_state['ai_battleships']:
            distance = ((player_ship.x - ai_ship.x)**2 + (player_ship.y - ai_ship.y)**2)**0.5
            if distance < 100:  # Combat range
                if player_ship.can_shoot():
                    game_state['bullets'].append(Bullet(player_ship.x, player_ship.y, ai_ship.x, ai_ship.y, True))
                    player_ship.shoot()
                if ai_ship.can_shoot():
                    game_state['bullets'].append(Bullet(ai_ship.x, ai_ship.y, player_ship.x, player_ship.y, False))
                    ai_ship.shoot()

    # Update bullets and check for hits
    for bullet in game_state['bullets'][:]:
        bullet.update()
        for ship in game_state['player_battleships'] + game_state['ai_battleships']:
            if bullet.check_collision(ship):
                if ship.take_damage(0.5):
                    if ship in game_state['player_battleships']:
                        game_state['player_battleships'].remove(ship)
                    else:
                        game_state['ai_battleships'].remove(ship)
                game_state['bullets'].remove(bullet)
                break
        if bullet not in game_state['bullets']:
            continue
        if bullet.is_out_of_bounds():
            game_state['bullets'].remove(bullet)

def get_continent_for_coordinates(x, y):
    for continent, bounds in continent_boundaries.items():
        if point_inside_polygon(x, y, bounds):
            return continent
    return None

def add_boundary_point(continent, x, y):
    continent_boundaries[continent].append((x, y))

def remove_boundary_point(continent, index):
    if len(continent_boundaries[continent]) > 3:  # Ensure at least 3 points remain
        del continent_boundaries[continent][index]

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
                        return
    
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:  # Left mouse button
            dragging = False
            dragged_point = None
            dragged_continent = None
    
    elif event.type == pygame.MOUSEMOTION:
        if dragging:
            new_pos = event.pos
            game_state['continent_boundaries'][dragged_continent][dragged_point] = new_pos

def move_boundary_point(continent, index, x, y):
    continent_boundaries[continent][index] = (x, y)

# The save_continent_boundaries and load_continent_boundaries functions are already defined earlier in the file

# You may want to add any additional helper functions or game logic here

if __name__ == "__main__":
    # You can add any initialization or testing code here
    pass
