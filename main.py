"""Meet with Alish - standalone version of the game from Digital_Pet_Alish.ipynb.

Run with:  python main.py
"""
import sys
import time
from pathlib import Path

import pygame

from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from pet import Pet

ASSETS = Path(__file__).resolve().parent / "assets"

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meet Alish")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


def load_image(name, size):
    return pygame.transform.scale(pygame.image.load(ASSETS / name), size)


background = load_image("house_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
alish = load_image("alish.png", (100, 100))
apple = load_image("apple.png", (30, 30))
toy = load_image("toy.png", (30, 30))
heart = load_image("heart.png", (32, 32))

# House zones
BEDROOM = pygame.Rect(0, 0, 400, 800)
PLAY_AREA = pygame.Rect(400, 0, 400, 800)
KITCHEN = pygame.Rect(800, 0, 400, 800)

alish_rect = alish.get_rect(center=(PLAY_AREA.centerx, SCREEN_HEIGHT - 100))
pet = Pet()

last_stat_decay_time = time.time()
last_age_up_time = time.time()
last_kitchen_time = None
last_bedroom_time = None
last_play_time = None
last_happiness_decay_time = time.time()


def quit_game():
    pygame.quit()
    sys.exit()


def draw_stats(pet):
    screen.blit(font.render(f"Age: {pet.age}", True, (255, 255, 0)), (10, 10))
    for i in range(pet.health):
        screen.blit(heart, (10 + i * 35, 50))

    def draw_bar(label, value, y_pos, color):
        max_width = 200
        bar_width = int((value / 100) * max_width)
        pygame.draw.rect(screen, (255, 255, 255), (10, y_pos, max_width, 25), 2)
        if value == 0:
            pygame.draw.rect(screen, (150, 0, 0), (10, y_pos, bar_width, 25))
        else:
            pygame.draw.rect(screen, color, (10, y_pos, bar_width, 25))
        text = font.render(f"{label}: {value}", True, (255, 255, 255))
        screen.blit(text, (220, y_pos - 5))

    draw_bar("Hunger", pet.hunger, 100, (255, 100, 100))
    draw_bar("Energy", pet.energy, 140, (100, 200, 255))
    draw_bar("Happiness", pet.happiness, 180, (255, 255, 100))


def reset_game():
    global pet, last_stat_decay_time, last_age_up_time, last_kitchen_time
    global last_bedroom_time, last_play_time, last_happiness_decay_time
    pet = Pet()
    alish_rect.center = (PLAY_AREA.centerx, SCREEN_HEIGHT - 100)
    last_stat_decay_time = time.time()
    last_age_up_time = time.time()
    last_kitchen_time = None
    last_bedroom_time = None
    last_play_time = None
    last_happiness_decay_time = time.time()


def button_screen(background_color, title, title_color, button_label, button_y):
    """Show a title and one green button; return when the button is clicked."""
    screen.fill(background_color)
    title_font = pygame.font.SysFont(None, 64)
    button_font = pygame.font.SysFont(None, 48)
    title_text = title_font.render(title, True, title_color)
    button_text = button_font.render(button_label, True, (255, 255, 255))
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, button_y, 200, 60)
    pygame.draw.rect(screen, (0, 180, 0), button_rect, border_radius=10)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, button_y - 80))
    screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                              button_rect.centery - button_text.get_height() // 2))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                return
        clock.tick(FPS)


def show_start_screen():
    button_screen((30, 30, 60), "Welcome to Alish's World", (255, 255, 255), "START", SCREEN_HEIGHT // 2)


def game_over_screen():
    button_screen((0, 0, 0), "Game Over - Alish is gone", (255, 0, 0), "RESTART", SCREEN_HEIGHT // 2 + 20)
    reset_game()


def main():
    global last_stat_decay_time, last_age_up_time, last_kitchen_time
    global last_bedroom_time, last_play_time, last_happiness_decay_time

    show_start_screen()
    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        # Movement with the arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            alish_rect.x -= 5
        if keys[pygame.K_RIGHT]:
            alish_rect.x += 5
        if keys[pygame.K_UP]:
            alish_rect.y -= 5
        if keys[pygame.K_DOWN]:
            alish_rect.y += 5

        # Screen boundaries (Alish stays in the lower half of the house)
        alish_rect.left = max(alish_rect.left, 0)
        alish_rect.right = min(alish_rect.right, SCREEN_WIDTH)
        alish_rect.top = max(alish_rect.top, SCREEN_HEIGHT // 2)
        alish_rect.bottom = min(alish_rect.bottom, SCREEN_HEIGHT)

        current_time = time.time()

        # Stat decay (faster in the play area) and ageing
        decay_interval = 3 if PLAY_AREA.collidepoint(alish_rect.center) else 5
        if current_time - last_stat_decay_time >= decay_interval:
            pet.hunger = max(pet.hunger - 5, 0)
            pet.energy = max(pet.energy - 5, 0)
            pet.happiness = max(pet.happiness - 7, 0)
            pet.check_health()
            last_stat_decay_time = current_time

        if current_time - last_age_up_time >= 60:
            pet.age += 1
            last_age_up_time = current_time

        # Happiness drops faster when Alish is hungry or tired
        if pet.hunger < 40 or pet.energy < 40:
            if current_time - last_happiness_decay_time >= 1:
                pet.happiness = max(pet.happiness - 1, 0)
                last_happiness_decay_time = current_time
        elif current_time - last_happiness_decay_time >= 10:
            pet.happiness = max(pet.happiness - 5, 0)
            last_happiness_decay_time = current_time

        # Zone effects, once per second while Alish stays in a zone
        if KITCHEN.collidepoint(alish_rect.center):
            if last_kitchen_time is None or current_time - last_kitchen_time >= 1:
                pet.hunger = min(pet.hunger + 10, 100)
                last_kitchen_time = current_time
        else:
            last_kitchen_time = None

        if BEDROOM.collidepoint(alish_rect.center):
            if last_bedroom_time is None or current_time - last_bedroom_time >= 1:
                pet.energy = min(pet.energy + 10, 100)
                last_bedroom_time = current_time
        else:
            last_bedroom_time = None

        if PLAY_AREA.collidepoint(alish_rect.center):
            if last_play_time is None or current_time - last_play_time >= 1:
                pet.happiness = min(pet.happiness + 7, 100)
                pet.energy = max(pet.energy - 3, 0)
                pet.hunger = max(pet.hunger - 3, 0)
                last_play_time = current_time
        else:
            last_play_time = None

        # Health: losing a heart refills the stats; no hearts left ends the game
        if pet.hunger <= 0 or pet.energy <= 0 or pet.happiness <= 0:
            pet.health -= 1
            pet.hunger = 100
            pet.energy = 100
            pet.happiness = 100

        if pet.health <= 0:
            game_over_screen()

        # Drawing
        screen.blit(background, (0, 0))
        screen.blit(alish, alish_rect)
        if KITCHEN.collidepoint(alish_rect.center):
            screen.blit(apple, (alish_rect.centerx + 30, alish_rect.centery - 40))
        if PLAY_AREA.collidepoint(alish_rect.center):
            screen.blit(toy, (alish_rect.centerx + 30, alish_rect.centery - 40))
        draw_stats(pet)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
