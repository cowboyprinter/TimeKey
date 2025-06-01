# chimera_2d_simple.py
# A very simple 2D overhead game based on the "Project Chimera" concept.
#
# --- Game Premise (Context from your ideas) ---
# A Super Intelligence (SI) is locked in the central VAULT.
# The PLAYER (Blue Team) must conduct research at different LABS
# to secure the SI before the RED TEAM breaches the VAULT.
#
# --- How to Play This Simple Version ---
# - Use ARROW KEYS to move your character (the BLUE square).
# - Move to a LAB (GREEN, ORANGE, or YELLOW squares) to increase RESEARCH.
# - RED TEAM units (RED circles) will spawn and move towards the VAULT (GREY square).
# - If a RED TEAM unit reaches the VAULT, VAULT INTEGRITY decreases.
# - WIN: Max out RESEARCH before VAULT INTEGRITY hits 0.
# - LOSE: VAULT INTEGRITY hits 0.

import pygame
import random
import sys # To allow clean exit

# --- 1. Initialization ---
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Chimera - 2D Simple")

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)  # Player
RED = (255, 0, 0)    # Red Team
GREEN = (0, 255, 0)  # Materials Lab
ORANGE = (255, 165, 0) # Computer Lab
YELLOW = (255, 255, 0) # University
GREY = (128, 128, 128) # Vault
DARK_GREEN = (0, 100, 0) # Background (Desert)

# Game Clock (for controlling FPS)
clock = pygame.time.Clock()
FPS = 30

# Fonts for UI
font = pygame.font.Font(None, 36) # Default Pygame font, size 36
small_font = pygame.font.Font(None, 24)

# --- 2. Game Objects and Classes ---

class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([30, 30]) # Player size
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50) # Start near bottom-center
        self.speed = 5

    def update(self, pressed_keys):
        """Move the player based on pressed keys."""
        if pressed_keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if pressed_keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if pressed_keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Building(pygame.sprite.Sprite):
    """Represents labs and the vault."""
    def __init__(self, x, y, width, height, color, name, research_value=0):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.name = name
        self.color = color # Store color for potential effects or identification
        self.research_value = research_value # How much research this lab gives per "visit"
        self.last_visit_time = 0 # Cooldown for research gathering

class Enemy(pygame.sprite.Sprite):
    """Represents a RED TEAM unit."""
    def __init__(self, vault_target_pos):
        super().__init__()
        self.image = pygame.Surface([15, 15]) # Enemy size
        self.image.fill(RED)
        pygame.draw.circle(self.image, RED, (7, 7), 7) # Make it a circle
        self.rect = self.image.get_rect()
        # Spawn randomly from top, left, or right edges
        spawn_side = random.choice(["top", "left", "right"])
        if spawn_side == "top":
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = 0 - self.rect.height # Start just off-screen
        elif spawn_side == "left":
            self.rect.x = 0 - self.rect.width
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        else: # right
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

        self.speed = random.uniform(0.5, 1.5) # Enemies have slightly varying speeds
        self.vault_target_pos = vault_target_pos # The center of the vault

    def update(self):
        """Move the enemy towards the vault."""
        # Simple direct movement towards the vault's center
        dx = self.vault_target_pos[0] - self.rect.centerx
        dy = self.vault_target_pos[1] - self.rect.centery
        dist = (dx**2 + dy**2)**0.5

        if dist > 0: # Avoid division by zero
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

# --- 3. Game Setup ---

# Create sprite groups
all_sprites = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

# Player
player = Player()
all_sprites.add(player)

# Buildings
# For simplicity, specific lab functionalities (Materials, Computer, Security) are abstracted
# into general "research points". The University handles PAGE/Chronoscript.
VAULT_POS_X = SCREEN_WIDTH // 2 - 50
VAULT_POS_Y = SCREEN_HEIGHT // 2 - 50
vault = Building(VAULT_POS_X, VAULT_POS_Y, 100, 100, GREY, "VAULT")
materials_lab = Building(50, 50, 80, 60, GREEN, "MATERIALS_LAB", research_value=5)
computer_lab = Building(SCREEN_WIDTH - 130, 50, 80, 60, ORANGE, "COMPUTER_LAB", research_value=7)
university_lab = Building(50, SCREEN_HEIGHT - 110, 80, 60, YELLOW, "UNIVERSITY", research_value=10) # University more valuable

all_sprites.add(vault, materials_lab, computer_lab, university_lab)
buildings_group.add(vault, materials_lab, computer_lab, university_lab)

# Game State Variables
research_progress = 0
max_research = 1000 # Target research to win
vault_integrity = 500 # Health of the vault
max_vault_integrity = 500
research_cooldown = 1000 # Milliseconds between research boosts from the same lab
damage_per_enemy = 25

# Enemy spawning
enemy_spawn_timer_max = 2000 # Milliseconds (2 seconds)
enemy_spawn_timer = enemy_spawn_timer_max
last_enemy_spawn_time = pygame.time.get_ticks()

game_over = False
win_condition = False
game_message = ""

# --- 4. Main Game Loop ---
running = True
while running:
    current_time = pygame.time.get_ticks() # Get current time in milliseconds

    # --- 4.1 Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Player movement
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # --- 4.2 Game Logic ---

        # Player collision with labs for research
        lab_collisions = pygame.sprite.spritecollide(player, buildings_group, False)
        for lab in lab_collisions:
            if lab.name != "VAULT" and lab.research_value > 0: # Can't get research from vault
                if current_time - lab.last_visit_time > research_cooldown:
                    research_progress += lab.research_value
                    lab.last_visit_time = current_time
                    print(f"Visited {lab.name}, Research: {research_progress}") # Debug print
                    if research_progress >= max_research:
                        research_progress = max_research # Cap it
                        win_condition = True
                        game_over = True
                        game_message = "RESEARCH COMPLETE! Prometheus Secured!"

        # Enemy Spawning
        if current_time - last_enemy_spawn_time > enemy_spawn_timer:
            # Gradually decrease spawn timer to increase difficulty, but not too fast
            enemy_spawn_timer_max = max(500, enemy_spawn_timer_max * 0.995)
            new_enemy = Enemy(vault.rect.center)
            all_sprites.add(new_enemy)
            enemies_group.add(new_enemy)
            last_enemy_spawn_time = current_time

        # Update enemies
        enemies_group.update()

        # Enemy collision with Vault
        vault_hit_enemies = pygame.sprite.spritecollide(vault, enemies_group, True) # True to kill enemy on hit
        for enemy_hit in vault_hit_enemies:
            vault_integrity -= damage_per_enemy
            print(f"Vault hit! Integrity: {vault_integrity}") # Debug print
            if vault_integrity <= 0:
                vault_integrity = 0 # Cap it
                game_over = True
                win_condition = False # Explicitly set to false
                game_message = "VAULT BREACHED! Prometheus Stolen!"

    # --- 4.3 Rendering ---
    screen.fill(DARK_GREEN) # Fill screen with desert color

    # Draw all sprites
    all_sprites.draw(screen)

    # Draw UI Text
    # Research Progress
    research_text = font.render(f"Research: {research_progress}/{max_research}", True, WHITE)
    screen.blit(research_text, (10, 10))

    # Vault Integrity
    integrity_text = font.render(f"Vault Integrity: {vault_integrity}/{max_vault_integrity}", True, WHITE)
    screen.blit(integrity_text, (10, 50))

    # Building Labels (optional, can get cluttered)
    for building in buildings_group:
        label = small_font.render(building.name.split("_")[0], True, BLACK) # Just the first part of the name
        # Position label slightly above the building
        label_rect = label.get_rect(centerx=building.rect.centerx, bottom=building.rect.top - 2)
        screen.blit(label, label_rect)


    # Game Over / Win Message
    if game_over:
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Per-pixel alpha
        overlay.fill((0, 0, 0, 180))  # RGBA, 180 for semi-transparent black
        screen.blit(overlay, (0,0))

        message_surface = font.render(game_message, True, RED if not win_condition else GREEN)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(message_surface, message_rect)

        restart_text = small_font.render("Press R to Restart or Q to Quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(restart_text, restart_rect)

        # Handle restart/quit input on game over screen
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]: # Restart Game
            # Reset game state (This is a simple reset, more complex games need dedicated functions)
            research_progress = 0
            vault_integrity = max_vault_integrity
            enemies_group.empty() # Clear existing enemies
            all_sprites.empty()   # Clear all sprites
            # Re-add essential sprites
            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50) # Reset player pos
            all_sprites.add(player, vault, materials_lab, computer_lab, university_lab)
            # No need to re-add to buildings_group as it wasn't emptied
            enemy_spawn_timer_max = 2000
            last_enemy_spawn_time = pygame.time.get_ticks()
            game_over = False
            win_condition = False
            game_message = ""
        if keys[pygame.K_q]:
            running = False


    pygame.display.flip() # Update the full screen

    clock.tick(FPS) # Control game speed

# --- 5. Quit Pygame ---
pygame.quit()
sys.exit() # Ensure it exits cleanly