import math
import random
import pygame

pygame.init()

WIDTH = 1920
HEIGHT = 1080

screen = pygame.display.set_mode((WIDTH, HEIGHT),  vsync=1)
pygame.display.set_caption("Fireworks")

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

    def draw(self, surface, color, radius):
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)


class Particle:
    def __init__(self, position, velocity, color, lifetime):
        self.position = position
        self.velocity = velocity
        self.color = color
        self.lifetime = lifetime

    def update(self):
        self.position = self.position.add(self.velocity)
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            self.position.draw(surface, self.color, 3)

class Firework:
    def __init__(self, position):
        self.position = position
        self.particles = []
        self.exploded = False

    def explode(self):
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            velocity = Vector(math.cos(angle) * speed, math.sin(angle) * speed)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            lifetime = random.randint(30, 60)
            self.particles.append(Particle(self.position, velocity, color, lifetime))

fireworks = [Firework(Vector(WIDTH // 2, HEIGHT // 2))]
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

    for firework in fireworks:
        if firework.exploded == False:
            firework.explode()
            firework.exploded = True

        for particle in firework.particles:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                firework.particles.remove(particle)
            
        if (firework.particles == []):
            fireworks.remove(firework)

    fps = clock.get_fps()
    
    fps_text = font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))

    clock.tick()

    pygame.display.flip()

pygame.quit()