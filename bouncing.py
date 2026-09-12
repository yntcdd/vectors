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
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls")

clock = pygame.time.Clock()


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


RADIUS = 25

# The square's border is the wall. The ball's center bounces when it is one
# radius away from the wall, so the ball never overlaps or passes the border.
LEFT_WALL = SQUARE_X + RADIUS
RIGHT_WALL = SQUARE_X + SQUARE_SIZE - RADIUS
TOP_WALL = SQUARE_Y + RADIUS
BOTTOM_WALL = SQUARE_Y + SQUARE_SIZE - RADIUS


class Ball:
    def __init__(self, position, velocity, radius=RADIUS):
        self.position = position
        self.velocity = velocity
        self.radius = radius

    def update(self):
        self.position = self.position.add(self.velocity)

    def bounce(self):
        # Left and right walls.
        if self.position.x < LEFT_WALL:
            self.position.x = LEFT_WALL
            self.velocity.x = -self.velocity.x
        elif self.position.x > RIGHT_WALL:
            self.position.x = RIGHT_WALL
            self.velocity.x = -self.velocity.x

        # Top and bottom walls.
        if self.position.y < TOP_WALL:
            self.position.y = TOP_WALL
            self.velocity.y = -self.velocity.y
        elif self.position.y > BOTTOM_WALL:
            self.position.y = BOTTOM_WALL
            self.velocity.y = -self.velocity.y

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            BLUE,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )


balls = [
    Ball(
        Vector(SQUARE_X + SQUARE_SIZE // 3, SQUARE_Y + SQUARE_SIZE // 2),
        Vector(4, -3),
    ),
    Ball(
        Vector(SQUARE_X + 2 * SQUARE_SIZE // 3, SQUARE_Y + SQUARE_SIZE // 2),
        Vector(-3, 5),
    ),
]

running = True

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
        ball.draw(screen)

    # The square's border is black.
    pygame.draw.rect(screen, BLACK, square_rect, 2)

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
