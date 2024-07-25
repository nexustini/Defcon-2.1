import random
import pygame
from entities import City, Missile, AirDefense

# Define the countries and their coordinate ranges
countries = {
    "North America": [(50, 50), (250, 200)],
    "South America": [(100, 250), (200, 500)],
    "Europe": [(300, 50), (400, 200)],
    "Africa": [(300, 200), (400, 450)],
    "Asia": [(450, 50), (700, 300)],
    "Oceania": [(600, 350), (750, 500)]
}

def generate_cities():
    cities = {}
    for country, coordinates in countries.items():
        city_list = []
        for _ in range(5):
            x = random.randint(coordinates[0][0], coordinates[1][0])
            y = random.randint(coordinates[0][1], coordinates[1][1])
            city_list.append(City(x, y))
        cities[country] = city_list
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

    player_score_text = font.render(f"{game_state['selected_country']} Score: {game_state['player_score']}", True, (255, 255, 255))
    ai_score_text = font.render(f"{game_state['ai_country']} Score: {game_state['ai_score']}", True, (255, 255, 255))

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

def handle_country_selection(game_state, background):
    screen = pygame.display.get_surface()
    font = pygame.font.SysFont(None, 36)
    selected_country = None
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))

    # Create buttons for each country
    button_height = 50
    button_width = 200
    start_y = 100
    buttons = []
    for i, country in enumerate(countries.keys()):
        button_rect = pygame.Rect((screen.get_width() - button_width) // 2, 
                                  start_y + i * (button_height + 10), 
                                  button_width, button_height)
        buttons.append((button_rect, country))

    while selected_country is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, country in buttons:
                    if button.collidepoint(event.pos):
                        selected_country = country
                        game_state['selected_country'] = country
                        game_state['ai_country'] = random.choice([c for c in countries if c != country])
                        break

        # Draw background
        screen.blit(background, (0, 0))

        # Draw semi-transparent overlay
        screen.blit(overlay, (0, 0))

        # Draw buttons and country names
        for button, country in buttons:
            pygame.draw.rect(screen, (100, 100, 255), button)  # Light blue color
            text = font.render(country, True, (255, 255, 255))
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)

        instruction_text = font.render("Select your country", True, (255, 255, 255))
        screen.blit(instruction_text, ((screen.get_width() - instruction_text.get_width()) // 2, 50))

        pygame.display.flip()

def handle_city_selection(game_state):
    screen = pygame.display.get_surface()
    for country, city_list in game_state['cities'].items():
        for city in city_list:
            if pygame.mouse.get_pos()[0] in range(city.x - 5, city.x + 5) and pygame.mouse.get_pos()[1] in range(city.y - 5, city.y + 5):
                if country == game_state['selected_country']:
                    game_state['selected_city'] = city
                    return True
    return False

def handle_target_city_selection(game_state):
    screen = pygame.display.get_surface()
    for country, city_list in game_state['cities'].items():
        for city in city_list:
            if pygame.mouse.get_pos()[0] in range(city.x - 5, city.x + 5) and pygame.mouse.get_pos()[1] in range(city.y - 5, city.y + 5):
                if country != game_state['selected_country']:
                    game_state['target_city'] = city
                    return True
    return False

def launch_missile(start_city, target_city, is_icbm, game_state):
    missile = Missile(start_city, target_city, is_icbm)
    game_state['missiles'].append(missile)

def ai_turn(game_state):
    available_cities = [city for city_list in game_state['cities'].values() for city in city_list if city != game_state['target_city']]
    if available_cities:
        target_city = random.choice(available_cities)
        ai_cities = game_state['cities'][game_state['ai_country']]
        if ai_cities:
            start_city = random.choice(ai_cities)
            launch_missile(start_city, target_city, False, game_state)

    # Place AI air defense
    if game_state['ai_air_defense'] is None and random.random() < 0.2:  # 20% chance to place air defense
        ai_country_coords = countries[game_state['ai_country']]
        x = random.randint(ai_country_coords[0][0], ai_country_coords[1][0])
        y = random.randint(ai_country_coords[0][1], ai_country_coords[1][1])
        game_state['ai_air_defense'] = AirDefense(x, y)

def check_game_over(game_state):
    player_cities = game_state['cities'][game_state['selected_country']]
    ai_cities = game_state['cities'][game_state['ai_country']]

    if len(player_cities) == 0 or len(ai_cities) == 0:
        game_state['game_over'] = True
        
        if len(player_cities) == 0 and len(ai_cities) == 0:
            if game_state['player_score'] > game_state['ai_score']:
                game_state['winner_country'] = game_state['selected_country']
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
            game_state['winner_country'] = game_state['selected_country']
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
