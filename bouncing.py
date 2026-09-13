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

# Challenge text values (edit these to change the challenge).
DAMAGE_BALL_NAME = "FIBONACCI"
BOSS_HP = "10000"  # stored as a decimal string to support very large numbers
TARGET_DAMAGE = BOSS_HP  # the target is to deal the boss's full HP in damage
TIME_LIMIT = 60

# The challenge text updates automatically from the values above. It is split
# into two lines so it can be drawn big and still fit the window. Each line is
# a list of (text, color) segments; the name is highlighted in red.
challenge_lines = [
    [("Can ", BLACK), (DAMAGE_BALL_NAME, RED),
     (f" deal {TARGET_DAMAGE} damage", BLACK)],
    [(f"in {TIME_LIMIT} seconds?", BLACK)],
]

# Countdown timer: a ring on the right that drains as time runs out.
TIMER_RADIUS = 28
TIMER_BORDER = 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 28)
label_font = pygame.font.Font(None, 36)
challenge_font = pygame.font.Font(None, 38)  # the sentence, pushed left
timer_font = pygame.font.Font(None, 36)      # the countdown number


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

    def dot(self, other):
        return self.x * other.x + self.y * other.y


def reflect(velocity, normal):
    # Reflect velocity across the surface with the given unit normal. This
    # changes the direction but keeps the speed (magnitude) unchanged.
    return velocity.subtract(normal.multiply(2 * velocity.dot(normal)))


def render_text(segments, font):
    # Render a list of (text, color) segments side by side into one surface.
    pieces = [font.render(text, True, color) for text, color in segments]
    width = sum(piece.get_width() for piece in pieces)
    height = max(piece.get_height() for piece in pieces)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    x = 0
    for piece in pieces:
        surface.blit(piece, (x, 0))
        x += piece.get_width()
    return surface


def strip_zeros(number):
    # Remove leading zeros but always keep at least "0".
    stripped = number.lstrip("0")
    return stripped if stripped else "0"


def subtract_string(a, b):
    # Subtract two non-negative decimal strings digit by digit, like written
    # subtraction. This works for any number of digits and never uses int().
    a = strip_zeros(a)
    b = strip_zeros(b)

    # HP never goes below zero, so a bigger b simply gives "0".
    if len(a) < len(b) or (len(a) == len(b) and a < b):
        return "0"

    # Pad b with leading zeros so both strings have the same length.
    b = b.rjust(len(a), "0")

    result = []
    borrow = 0
    for i in range(len(a) - 1, -1, -1):
        digit = (ord(a[i]) - ord("0")) - (ord(b[i]) - ord("0")) - borrow
        if digit < 0:
            digit += 10
            borrow = 1
        else:
            borrow = 0
        result.append(chr(ord("0") + digit))

    result.reverse()
    return strip_zeros("".join(result))


def add_string(a, b):
    # Add two non-negative decimal strings digit by digit, like written
    # addition. This works for any number of digits and never uses int().
    a = strip_zeros(a)
    b = strip_zeros(b)

    # Pad the shorter string with leading zeros so both have the same length.
    length = max(len(a), len(b))
    a = a.rjust(length, "0")
    b = b.rjust(length, "0")

    result = []
    carry = 0
    for i in range(length - 1, -1, -1):
        total = (ord(a[i]) - ord("0")) + (ord(b[i]) - ord("0")) + carry
        result.append(chr(ord("0") + (total % 10)))
        carry = total // 10

    if carry:
        result.append(chr(ord("0") + carry))

    result.reverse()
    return strip_zeros("".join(result))


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
        self.hp = subtract_string(self.hp, amount)

    def is_alive(self):
        # A ball without HP (like the damage ball) is always alive; otherwise
        # it lives until its HP reaches zero.
        return self.hp is None or self.hp != "0"

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
            hp_text = font.render(self.hp, True, BLACK)
            surface.blit(hp_text, hp_text.get_rect(center=center))


class DamageBall(Ball):
    # A ball that deals damage to the boss. It has no HP of its own.
    def __init__(self, position, velocity, damage="1",
                 radius=1.3 * RADIUS, color=LIGHT_BLUE,
                 outline_color=DARKER_BLUE):
        super().__init__(position, velocity, hp=None, damage=damage,
                         radius=radius, color=color, outline_color=outline_color)

    def deal_damage(self, target):
        # Apply this ball's damage to the target once.
        target.take_damage(self.damage)


class FibonacciBall(DamageBall):
    # A damage ball whose damage IS the Fibonacci sequence: 1, 1, 2, 3, 5, 8...
    def __init__(self, position, velocity):
        super().__init__(position, velocity, damage="1")
        self.fib_prev = "1"         # the previous Fibonacci number in the sequence
        self.fib_before_prev = "0"  # the Fibonacci number before that

    def next_fib(self):
        # Advance to the next Fibonacci number and return it.
        next_fib = add_string(self.fib_prev, self.fib_before_prev)
        self.fib_before_prev = self.fib_prev
        self.fib_prev = next_fib
        return next_fib

    def deal_damage(self, target):
        # Deal the current damage, then advance to the next Fibonacci number.
        target.take_damage(self.damage)
        self.damage = self.next_fib()


class FibonacciSumBall(FibonacciBall):
    # A damage ball whose damage is a running SUM of the Fibonacci sequence, so
    # it goes 1, 2, 4, 7, 12, 20... (each hit adds the next Fibonacci number).
    def deal_damage(self, target):
        # Deal the current damage, then add the next Fibonacci number to it.
        target.take_damage(self.damage)
        self.damage = add_string(self.damage, self.next_fib())


damage_ball = FibonacciBall(
    Vector(SQUARE_X + SQUARE_SIZE // 3, SQUARE_Y + SQUARE_SIZE // 2),
    Vector(4, -3),
)
boss_ball = Ball(
    Vector(SQUARE_X + 2 * SQUARE_SIZE // 3, SQUARE_Y + SQUARE_SIZE // 2),
    Vector(-1, 1),
    hp=BOSS_HP,
    damage="0",
    radius=(3 * RADIUS) / 1.3,
)

balls = [damage_ball, boss_ball]

running = True
balls_colliding = False
start_ticks = pygame.time.get_ticks()  # when the countdown starts

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
        if ball.is_alive():
            ball.update()
            ball.bounce()

    # Ball-to-ball collision: bounce apart and deal damage once per hit.
    if boss_ball.is_alive():
        difference = damage_ball.position.subtract(boss_ball.position)
        distance = difference.magnitude()
        min_distance = damage_ball.radius + boss_ball.radius

        if distance < min_distance:
            # Unit normal pointing from the boss ball toward the damage ball.
            normal = difference.divide(distance)
            overlap = min_distance - distance

            # Push the balls apart so they never overlap or pass through each other.
            damage_ball.position = damage_ball.position.add(normal.multiply(overlap / 2))
            boss_ball.position = boss_ball.position.subtract(normal.multiply(overlap / 2))

            if not balls_colliding:
                balls_colliding = True
                damage_ball.deal_damage(boss_ball)

                # Arcade bounce: reverse each ball's motion along the normal
                # only when it is moving toward the other ball. This keeps each
                # ball's speed constant and always bounces them apart.
                if damage_ball.velocity.dot(normal) < 0:
                    damage_ball.velocity = reflect(damage_ball.velocity, normal)
                if boss_ball.velocity.dot(normal) > 0:
                    boss_ball.velocity = reflect(boss_ball.velocity, normal)
        else:
            balls_colliding = False

    for ball in balls:
        if ball.is_alive():
            ball.draw(screen)

    # The square's border is black.
    pygame.draw.rect(screen, BLACK, square_rect, 2)

    # Damage display under the left side of the arena.
    damage_text = label_font.render(f"Damage: {damage_ball.damage}", True, RED)
    screen.blit(damage_text, (SQUARE_X, SQUARE_Y + SQUARE_SIZE + 20))

    # Challenge text pushed to the left, vertically centered above the arena.
    line_height = challenge_font.get_height()
    total_height = line_height * len(challenge_lines)
    start_y = SQUARE_Y // 2 - total_height // 2
    for i, segments in enumerate(challenge_lines):
        line_surface = render_text(segments, challenge_font)
        screen.blit(line_surface, (SQUARE_X, start_y + i * line_height))

    # Countdown timer: a thick ring on the right that slowly loses its
    # circumference as time runs out, with the seconds left inside.
    timer_center = (WIDTH - TIMER_RADIUS - 10, SQUARE_Y // 2)  # 10px from the right edge
    timer_rect = (timer_center[0] - TIMER_RADIUS, timer_center[1] - TIMER_RADIUS,
                  TIMER_RADIUS * 2, TIMER_RADIUS * 2)
    time_left = max(0, TIME_LIMIT - (pygame.time.get_ticks() - start_ticks) // 1000)
    remaining = time_left / TIME_LIMIT  # 1.0 at the start, 0.0 at the end

    if remaining > 0.999:
        # Full ring before any time has visibly drained.
        pygame.draw.circle(screen, BLACK, timer_center, TIMER_RADIUS, TIMER_BORDER)
    else:
        # The remaining arc is anchored at the top (12 o'clock) and sweeps
        # clockwise; its length shrinks as time runs out.
        start_angle = math.pi / 2 - 2 * math.pi * remaining
        pygame.draw.arc(screen, BLACK, timer_rect, start_angle, math.pi / 2,
                        TIMER_BORDER)

    timer_text = timer_font.render(str(time_left), True, BLACK)
    screen.blit(timer_text, timer_text.get_rect(center=timer_center))

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
