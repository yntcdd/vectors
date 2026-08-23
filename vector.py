import math
import random
import pygame

pygame.init()

WIDTH = 1920
HEIGHT = 1080

screen = pygame.display.set_mode((WIDTH, HEIGHT),  vsync=1)
pygame.display.set_caption("Vectors")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def subtract(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def multiply(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def divide(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

ball = Vector(WIDTH // 2, HEIGHT // 2)
radius = 25
speed = 3

direction = Vector(0, 0)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    mouse_pos = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0]:
        direction = Vector(
            mouse_pos[0] - ball.x,
            mouse_pos[1] - ball.y
        )

    distance = direction.magnitude()

    if distance > 0:
        direction = direction.divide(distance)
        ball = ball.add(direction.multiply(speed))

    pygame.draw.circle(
        screen,
        "black",
        (int(ball.x), int(ball.y)),
        radius
    )

    fps = clock.get_fps()
    
    fps_text = font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))

    clock.tick()

    pygame.display.flip()

pygame.quit()