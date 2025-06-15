import pygame
import random

# Game constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
GROUND_HEIGHT = 100
BIRD_SIZE = 32
PIPE_WIDTH = 52
PIPE_GAP = 100
FPS = 60

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.vel = 0
        self.gravity = 0.5
        self.flap_power = -7

    def update(self):
        self.vel += self.gravity
        self.y += self.vel

    def flap(self):
        self.vel = self.flap_power

    def get_rect(self):
        return pygame.Rect(self.x, self.y, BIRD_SIZE, BIRD_SIZE)

def create_pipe_pair():
    gap_y = random.randint(50, SCREEN_HEIGHT - GROUND_HEIGHT - 50 - PIPE_GAP)
    top = pygame.Rect(SCREEN_WIDTH, 0, PIPE_WIDTH, gap_y)
    bottom = pygame.Rect(SCREEN_WIDTH, gap_y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - gap_y - PIPE_GAP - GROUND_HEIGHT)
    return top, bottom

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    bird = Bird()
    pipes = []
    pipe_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.flap()

        bird.update()
        pipe_timer += 1
        if pipe_timer > 90:
            pipes.append(create_pipe_pair())
            pipe_timer = 0

        for pipe_pair in pipes:
            pipe_pair[0].x -= 2
            pipe_pair[1].x -= 2

        pipes = [p for p in pipes if p[0].right > 0]

        # Collision detection
        for top, bottom in pipes:
            if bird.get_rect().colliderect(top) or bird.get_rect().colliderect(bottom):
                running = False
        if bird.y + BIRD_SIZE > SCREEN_HEIGHT - GROUND_HEIGHT:
            running = False

        screen.fill((135, 206, 250))
        for top, bottom in pipes:
            pygame.draw.rect(screen, (0, 255, 0), top)
            pygame.draw.rect(screen, (0, 255, 0), bottom)

        pygame.draw.rect(screen, (255, 255, 0), bird.get_rect())
        pygame.draw.rect(screen, (222, 184, 135), pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
