import pygame, random, sys, os
from collections import deque

# ------------------ INITIAL SETUP ------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival Queue — Final")

# Colors
WHITE, GREEN, YELLOW, RED, DARKGREY, BLACK = (255,255,255), (0,255,0), (255,255,0), (255,0,0), (25,25,25), (0,0,0)
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Image loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
player_img = pygame.image.load(os.path.join(BASE_DIR, "player.png"))
player_img = pygame.transform.scale(player_img, (50, 50))
zombie_img = pygame.image.load(os.path.join(BASE_DIR, "zombie.png"))
zombie_img = pygame.transform.scale(zombie_img, (50, 50))

# ------------------ PLAYER SETUP ------------------
player = pygame.Rect(375, 520, 50, 50)
player_hp = 100
bullets = []

# ------------------ DSA STRUCTURES ------------------
zombie_queue = deque()  # Queue for FIFO enemy spawn
zombies = []            # Array (list) for all active zombies

clock = pygame.time.Clock()
level = 1
zombies_per_level = 5
zombies_spawned = 0
zombie_timer = 0
SPAWN_INTERVAL = 60

# ------------------ FUNCTIONS ------------------
def spawn_zombie():
    """Spawn 1 or 2 zombies per wave depending on level."""
    global zombies_spawned
    for _ in range(2 if level >= 3 else 1):
        if zombies_spawned < zombies_per_level:
            x = random.randint(40, WIDTH - 90)
            y = -50
            hp = random.randint(30, 60) + level * 10
            zombie = {"rect": pygame.Rect(x, y, 50, 50), "hp": hp, "max_hp": hp}
            zombie_queue.append(zombie)
            zombies.append(zombie)
            zombies_spawned += 1

def draw_hp_bar(zombie):
    """Draw colored HP bar above zombie."""
    hp_ratio = zombie["hp"] / zombie["max_hp"]
    color = GREEN if hp_ratio > 0.6 else YELLOW if hp_ratio > 0.3 else RED
    bar_w, bar_h = 50, 6
    pygame.draw.rect(win, RED, (zombie["rect"].x, zombie["rect"].y - 8, bar_w, bar_h))
    pygame.draw.rect(win, color, (zombie["rect"].x, zombie["rect"].y - 8, bar_w * hp_ratio, bar_h))

def draw_window():
    """Main game window draw."""
    win.fill(DARKGREY)
    win.blit(player_img, player)
    for b in bullets:
        pygame.draw.rect(win, WHITE, b)
    for z in zombies:
        win.blit(zombie_img, z["rect"])
        draw_hp_bar(z)
    hp_text = font.render(f"HP: {player_hp}", True, WHITE)
    lvl_text = font.render(f"Level: {level}", True, WHITE)
    q_text = font.render(f"Zombies in Queue: {len(zombie_queue)}", True, WHITE)
    win.blit(hp_text, (10, 10))
    win.blit(lvl_text, (10, 40))
    win.blit(q_text, (10, 70))
    pygame.display.update()

def handle_movement(keys):
    if keys[pygame.K_LEFT] and player.left > 0: player.x -= 5
    if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += 5
    if keys[pygame.K_UP] and player.top > 0: player.y -= 5
    if keys[pygame.K_DOWN] and player.bottom < HEIGHT: player.y += 5

def handle_bullets():
    """Move bullets upward and detect hits."""
    global zombies
    for b in bullets[:]:
        b.y -= 8
        if b.y < 0:
            bullets.remove(b)
            continue
        for z in zombies[:]:
            if b.colliderect(z["rect"]):
                z["hp"] -= 25
                if z["hp"] <= 0:
                    zombies.remove(z)
                    if z in zombie_queue:
                        zombie_queue.remove(z)
                if b in bullets:
                    bullets.remove(b)
                break

def handle_zombies():
    """Zombie movement, collisions, and attacks."""
    global player_hp
    if not zombie_queue:
        return
    for z in list(zombie_queue):
        z["rect"].y += 1 + level * 0.3
        # Player collision
        if z["rect"].colliderect(player):
            z["hp"] -= 10
            player_hp -= 5
            if z["hp"] <= 0:
                zombie_queue.remove(z)
                zombies.remove(z)
        # If zombie crosses bottom edge
        elif z["rect"].y > HEIGHT - 60:
            player_hp -= 10
            if z in zombie_queue:
                zombie_queue.remove(z)
            if z in zombies:
                zombies.remove(z)

def level_cleared():
    global level, zombies_spawned
    if not zombie_queue and zombies_spawned >= zombies_per_level:
        level += 1
        zombies_spawned = 0
        return True
    return False

def show_message(text, color=WHITE, delay=1200):
    """Display center message."""
    win.fill(DARKGREY)
    label = big_font.render(text, True, color)
    win.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))
    pygame.display.update()
    pygame.time.delay(delay)

# ------------------ START MENU ------------------
def draw_button(text, x, y, w, h, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse):
        pygame.draw.rect(win, hover_color, rect)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(win, color, rect)
    txt = font.render(text, True, BLACK)
    win.blit(txt, (x + (w - txt.get_width())//2, y + (h - txt.get_height())//2))
    return False

def start_menu():
    while True:
        win.fill((20, 20, 20))
        title = big_font.render("🧟 Zombie Survival Queue 🧟", True, GREEN)
        win.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        if draw_button("START GAME", 300, 300, 200, 60, GREEN, YELLOW):
            return
        if draw_button("EXIT", 300, 400, 200, 60, RED, YELLOW):
            pygame.quit()
            sys.exit()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# ------------------ MAIN GAME LOOP ------------------
def main():
    global zombie_timer, player_hp, level, zombies_spawned
    run = True
    start_menu()  # show start screen
    show_message("Level 1 Starting...", GREEN, 1500)
    while run:
        clock.tick(60)
        zombie_timer += 1

        # Spawn zombies (up to level 5)
        if level <= 5 and zombies_spawned < zombies_per_level and zombie_timer >= SPAWN_INTERVAL:
            spawn_zombie()
            zombie_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.centerx - 5, player.top, 10, 20))

        keys = pygame.key.get_pressed()
        handle_movement(keys)
        handle_bullets()
        handle_zombies()
        draw_window()

        # --- Game Over ---
        if player_hp <= 0:
            show_message("💀 Game Over 💀", RED, 2000)
            pygame.quit()
            sys.exit()

        # --- Level Cleared ---
        if level_cleared():
            if level > 5:
                show_message("🎉 YOU WON THE GAME! 🎉", GREEN, 2000)
                pygame.quit()
                sys.exit()
            else:
                show_message(f"Level {level-1} Cleared!", YELLOW, 1500)
                show_message(f"Level {level} Starting...", GREEN, 1500)

# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    main()
