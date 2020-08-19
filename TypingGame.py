import sys, pygame
import os
import Sprite, GameScreen

pygame.init()

# Get window size to center screen
window_dim = pygame.display.Info()
window_width = window_dim.current_w
window_height = window_dim.current_h

size = screen_width, screen_height = 640, 360
currentSize = 1280, 720

# Get window position based on screen resolution and window size
pos_x = screen_width / 2 - window_width / 2
pos_y = screen_height / 2 - window_height / 2

os.environ['SDL_VIDEO_WINDOW_POS'] = '%i, %i' % (pos_x, pos_y)
os.environ['SDL_VIDEO_CENTERED'] = '0'

screen = pygame.display.set_mode(size)
baseScreen = screen.copy()

buffer = pygame.surface.Surface((screen_width, screen_height))
buffer.fill((100, 100, 100))

# Set title
pygame.display.set_caption("Typing Adventure")

# Variables

clock = pygame.time.Clock()

screenManager = GameScreen.ScreenManager(screen_width, screen_height)

# Game functions

def redrawGameWindow():
    buffer.fill((100, 100, 100))

    drawCurrentScreen()

    baseScreen.blit(buffer, (0, 0))
    screen = pygame.display.set_mode(currentSize)
    screen.blit(pygame.transform.scale(baseScreen, currentSize), (0, 0))
    pygame.display.flip()

def updateGame(events, elapsed):
    screenManager.update(events, elapsed)

def drawCurrentScreen():
    screenManager.draw(buffer)

# Game Loop

running = True
while screenManager.running == True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: 
            screenManager.running = False
      
    elapsed = clock.tick(30)

    updateGame(events, elapsed)
    redrawGameWindow()

pygame.quit()