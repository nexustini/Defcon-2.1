import random
import pygame
from entities import City, Missile, AirDefense

# Define the continent boundaries
continent_boundaries = {
    "North America": [(50, 50), (350, 250)],
    "South America": [(150, 250), (300, 500)],
    "Europe": [(400, 50), (550, 200)],
    "Africa": [(400, 200), (550, 450)],
    "Asia": [(550, 50), (1100, 350)],
    "Oceania": [(900, 350), (1200, 550)]
}

def generate_cities():
    cities = {}
    for continent, coordinates in continent_boundaries.items():
        city_list = []
        for _ in range(5):
            x = random.randint(coordinates[0][0], coordinates[1][0])
            y = random.randint(coordinates[0][1], coordinates[1][1])
            city_list.append(City(x, y))
        cities[continent] = city_list
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
        x = random.randint(ai_continent_coords[0][0], ai_continent_coords[1][0])
        y = random.randint(ai_continent_coords[0][1], ai_continent_coords[1][1])
        game_state['ai_air_defense'] = AirDefense(x, y)

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
