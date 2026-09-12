import math
import pygame

pygame.init()

# Window is 540 x 960 (9:16 aspect ratio).
WIDTH = 540
HEIGHT = 960

# The 500 x 500 square, centered inside the window.
SQUARE_SIZE = 500
SQUARE_X = (WIDTH - SQUARE_SIZE) // 2    # 20
SQUARE_Y = (HEIGHT - SQUARE_SIZE) // 2   # 230

# Colors.
BEIGE = (245, 245, 220)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARKER_BLUE = (0, 0, 139)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 28)
label_font = pygame.font.Font(None, 32)


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


# Base radius, used by the damage ball (the boss ball scales off of this too).
RADIUS = 25


class Ball:
    def __init__(self, position, velocity, hp, damage, radius=RADIUS,
                 color=WHITE, outline_color=BLACK):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.hp = hp
        self.damage = damage
        self.color = color
        self.outline_color = outline_color

    def update(self):
        self.position = self.position.add(self.velocity)

    def take_damage(self, amount):
        self.hp -= amount

    def bounce(self):
        # The square's border is the wall. Each ball's center bounces when it
        # is one of its own radii away from the wall, so a larger ball still
        # can't pass through the border.
        left = SQUARE_X + self.radius
        right = SQUARE_X + SQUARE_SIZE - self.radius
        top = SQUARE_Y + self.radius
        bottom = SQUARE_Y + SQUARE_SIZE - self.radius

        # Left and right walls.
        if self.position.x < left:
            self.position.x = left
            self.velocity.x = -self.velocity.x
        elif self.position.x > right:
            self.position.x = right
            self.velocity.x = -self.velocity.x

        # Top and bottom walls.
        if self.position.y < top:
            self.position.y = top
            self.velocity.y = -self.velocity.y
        elif self.position.y > bottom:
            self.position.y = bottom
            self.velocity.y = -self.velocity.y

    def draw(self, surface):
        center = (int(self.position.x), int(self.position.y))

        # Body with an outline.
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, self.outline_color, center, self.radius, 2)

        # HP centered inside the ball (only for balls that have HP).
        if self.hp is not None:
            hp_text = font.render(str(self.hp), True, BLACK)
            surface.blit(hp_text, hp_text.get_rect(center=center))


damage_ball = Ball(
    Vector(SQUARE_X + SQUARE_SIZE // 3, SQUARE_Y + SQUARE_SIZE // 2),
    Vector(4, -3),
    hp=None,
    damage=1,
    radius=1.3 * RADIUS,
    color=LIGHT_BLUE,
    outline_color=DARKER_BLUE,
)
boss_ball = Ball(
    Vector(SQUARE_X + 2 * SQUARE_SIZE // 3, SQUARE_Y + SQUARE_SIZE // 2),
    Vector(-1, 1),
    hp=100,
    damage=0,
    radius=(3 * RADIUS) / 1.3,
)

balls = [damage_ball, boss_ball]

running = True
balls_colliding = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Outside of the square is beige.
    screen.fill(BEIGE)

    # Inside of the square is white.
    square_rect = pygame.Rect(SQUARE_X, SQUARE_Y, SQUARE_SIZE, SQUARE_SIZE)
    pygame.draw.rect(screen, WHITE, square_rect)

    for ball in balls:
        ball.update()
        ball.bounce()

    # Ball-to-ball collision: bounce apart and deal damage once per hit.
    difference = damage_ball.position.subtract(boss_ball.position)
    distance = difference.magnitude()
    min_distance = damage_ball.radius + boss_ball.radius

    if distance < min_distance and not balls_colliding:
        balls_colliding = True
        boss_ball.take_damage(damage_ball.damage)

        # Arcade bounce: swap directions but keep each ball's own speed, so
        # every ball's velocity magnitude stays constant.
        damage_speed = damage_ball.velocity.magnitude()
        boss_speed = boss_ball.velocity.magnitude()

        damage_direction = damage_ball.velocity.divide(damage_speed)
        boss_direction = boss_ball.velocity.divide(boss_speed)

        damage_ball.velocity = boss_direction.multiply(damage_speed)
        boss_ball.velocity = damage_direction.multiply(boss_speed)
    elif distance >= min_distance:
        balls_colliding = False

    for ball in balls:
        ball.draw(screen)

    # The square's border is black.
    pygame.draw.rect(screen, BLACK, square_rect, 2)

    # Damage display under the left side of the arena.
    damage_text = label_font.render(f"Damage: {damage_ball.damage}", True, RED)
    screen.blit(damage_text, (SQUARE_X, SQUARE_Y + SQUARE_SIZE + 20))

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
