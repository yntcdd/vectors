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

ball = Vector(WIDTH, HEIGHT // 3)
radius = 25
speed = 10

direction = Vector(-1, 0)
velocity = Vector(0, 0)
gravity = Vector(0, 0.05)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")


    pygame.draw.circle(
        screen,
        "black",
        (int(ball.x), int(ball.y)),
        radius
    )

    ball = ball.add(direction.multiply(speed))
    velocity = velocity.add(gravity)

    ball = ball.add(velocity)

    if ball.y + radius > HEIGHT:
        ball.y = HEIGHT // 3
        ball.x = WIDTH
        velocity = Vector(0, 0)
        speed = random.randint(5, 15)

    pygame.display.flip()

pygame.quit()