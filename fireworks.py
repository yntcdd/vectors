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
        return math.sqrt(self.x * self.x + self.y * self.y)

gravity = Vector(0, 0.01)
launch_gravity = Vector(0, 0.12)

class Particle:
    def __init__(self, position, velocity, color, lifetime):
        self.position = position
        self.velocity = velocity
        self.color = color
        self.lifetime = lifetime

    def update(self):
        self.velocity = self.velocity.add(gravity)
        self.position = self.position.add(self.velocity)
        self.lifetime -= 0.05

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), 1)


    def trail(self, surface):
        if self.lifetime > 0:
            trail_length = 15

            for i in range(trail_length):
                trail_color = (self.color)
                trail_position = self.position.subtract(
                    self.velocity.multiply(i * 1.3)
                )

                pygame.draw.circle(
                    surface,
                    trail_color,
                    (int(trail_position.x), int(trail_position.y)),
                    2
                )

class Firework:
    def __init__(self, position):
        self.position = position
        self.particles = []
        self.exploded = False
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def explode(self):

        amount = random.randint(100, 200)

        for i in range(amount):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(amount / 200, amount / 100)
            velocity = Vector(math.cos(angle) * speed, math.sin(angle) * speed)
            color = self.color
            lifetime = random.randint(5, 10)
            self.particles.append(Particle(self.position, velocity, color, lifetime))

class Starter:
    def __init__(self, position):
        self.finalposition = position
        self.position = Vector(WIDTH / 2, HEIGHT)
        self.color = (255, 255, 255)
        self.age = 0

        displacement = self.finalposition.subtract(self.position)
        self.flight_time = max(20.0, min(130.0, displacement.magnitude() / 8))

        t = self.flight_time
        self.velocity = Vector(
            displacement.x / t,
            (displacement.y - 0.5 * launch_gravity.y * t * t) / t,
        )

    def update(self):
        self.age += 1
        self.velocity = self.velocity.add(launch_gravity)
        self.position = self.position.add(self.velocity)

        if self.age >= self.flight_time:
            fireworks.append(Firework(self.finalposition))
            starters.remove(self)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), 5)

    def trail(self, surface):
        trail_length = 30

        for i in range(trail_length):
            fade = max(0.0, 1.0 - i / trail_length)
            trail_color = (
                int(self.color[0] * fade),
                int(self.color[1] * fade),
                int(self.color[2] * fade),
            )

            trail_position = self.position.subtract(
                self.velocity.multiply(i * 0.8)
            )

            pygame.draw.circle(
                surface,
                trail_color,
                (int(trail_position.x), int(trail_position.y)),
                2
            )

fireworks = []
starters = []
radius = 25
speed = 3

direction = Vector(0, 0)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                starters.append(Starter(Vector(*event.pos)))

    screen.fill("black")

    for starter in starters[:]:
        starter.update()
        starter.draw(screen)
        starter.trail(screen)

    for firework in fireworks[:]:
        if not firework.exploded:
            firework.explode()
            firework.exploded = True

        for particle in firework.particles[:]:
            particle.update()
            particle.draw(screen)
            particle.trail(screen)

            if particle.lifetime <= 0:
                firework.particles.remove(particle)

        if not firework.particles:
            fireworks.remove(firework)

    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    clock.tick()

    pygame.display.flip()

pygame.quit()