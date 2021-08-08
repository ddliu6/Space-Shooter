import pygame
import random
import os

# Constant Values
FPS = 60
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Init Setting
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter") # Cheange Title
score_font = os.path.join("PYGAME/Assets", "font.ttf")

# Load Images
bg_img = pygame.image.load(
    os.path.join("PYGAME/Assets/img", "background.png")
).convert()
player_img = pygame.image.load(
    os.path.join("PYGAME/Assets/img", "player.png")
).convert()
player_img.set_colorkey(BLACK)
Lives_img = pygame.transform.scale(player_img, (32, 24))
pygame.display.set_icon(Lives_img) # Change Icon
bullet_img = pygame.image.load(
    os.path.join("PYGAME/Assets/img", "bullet.png")
).convert()
bullet_img.set_colorkey(BLACK)
rock_imgs = []
for i in range(8):
    img = pygame.image.load(os.path.join("PYGAME/Assets/img", f"rock{i}.png")).convert()
    img.set_colorkey(BLACK)
    rock_imgs.append(img)
explode_ani = {}
explode_ani["rock"] = []
explode_ani["player"] = []
for i in range(9):
    img = pygame.image.load(os.path.join("PYGAME/Assets/img", f"expl{i}.png")).convert()
    img.set_colorkey(BLACK)
    explode_ani["rock"].append(img)
    img = pygame.image.load(
        os.path.join("PYGAME/Assets/img", f"player_expl{i}.png")
    ).convert()
    img.set_colorkey(BLACK)
    explode_ani["player"].append(img)
item_imgs = {
    "power": pygame.image.load(os.path.join("PYGAME/Assets/img", "gun.png")).convert(),
    "shield": pygame.image.load(
        os.path.join("PYGAME/Assets/img", "shield.png")
    ).convert(),
}
for img in item_imgs.values():
    img.set_colorkey(BLACK)

# Load Music
pygame.mixer.music.load(os.path.join("PYGAME/Assets/sound", "background.ogg"))
pygame.mixer.music.set_volume(0.8)
shoot_sfx = pygame.mixer.Sound(os.path.join("PYGAME/Assets/sound", "shoot.wav"))
die_sfx = pygame.mixer.Sound(os.path.join("PYGAME/Assets/sound", "rumble.ogg"))
explode_sfxs = []
for i in range(2):
    explode_sfxs.append(
        pygame.mixer.Sound(os.path.join("PYGAME/Assets/sound", f"expl{i}.wav"))
    )
item_sfxs = []
for i in range(2):
    item_sfxs.append(
        pygame.mixer.Sound(os.path.join("PYGAME/Assets/sound", f"pow{i}.wav"))
    )


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2 * 0.8
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.hp = 100
        self.lives = 3
        self.isHidden = False
        self.hideTime = 0
        self.powerTime = 0
        self.powerStartTime = 0

    def update(self):
        # Move
        input = pygame.key.get_pressed()
        if input[pygame.K_LEFT] or input[pygame.K_a]:
            self.rect.x -= self.speed
        if input[pygame.K_RIGHT] or input[pygame.K_d]:
            self.rect.x += self.speed
        # Check Edge
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        # Check Hidden
        if self.isHidden and pygame.time.get_ticks() - self.hideTime > 1000:
            self.rect.centerx = SCREEN_WIDTH / 2
            self.rect.bottom = SCREEN_HEIGHT - 10
            player.hp = 100
            self.isHidden = False
        # Power Timer
        now = pygame.time.get_ticks()
        if self.powerTime > 0 and now - self.powerStartTime > 1000:
            self.powerTime -= 1
            self.powerStartTime = now

    def shoot(self):
        if not self.isHidden:
            if self.powerTime > 0:
                bullet1 = Bullet(self.rect.left, self.rect.top)
                bullet2 = Bullet(self.rect.right, self.rect.top)
                sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                sprites.add(bullet)
                bullets.add(bullet)
            shoot_sfx.play()

    def hide(self):
        self.hideTime = pygame.time.get_ticks()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT + 500)
        self.isHidden = True

    def gotPower(self):
        if self.powerTime == 0:
            self.powerStartTime = pygame.time.get_ticks()
        self.powerTime += 3


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2 * 0.8
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedx = random.randrange(-3, 3)
        self.speedy = random.randrange(2, 5)
        self.rot_degree = random.randrange(-3, 3)
        self.total_degree = 0

    def rotate(self):
        self.total_degree += self.rot_degree
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree % 360)
        # re-center rotated image
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Respawn
        if (
            self.rect.top > SCREEN_HEIGHT
            or self.rect.left > SCREEN_WIDTH
            or self.rect.right < 0
        ):
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedx = random.randrange(-3, 3)
            self.speedy = random.randrange(2, 10)


class Item(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.image = item_imgs[self.type]
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2
        self.rect.center = pos
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, type, size, pos):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.size = size
        self.image = pygame.transform.scale(
            explode_ani[self.type][0], (self.size, self.size)
        )
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.frame = 0
        self.frameRate = 60
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.lastUpdate > self.frameRate:
            self.lastUpdate = now
            self.frame += 1
            if self.frame == len(explode_ani[self.type]):
                self.kill()
            else:
                self.image = pygame.transform.scale(
                    explode_ani[self.type][self.frame], (self.size, self.size)
                )


class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bg_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.top = -SCREEN_HEIGHT


def DrawText(surface, text, size, x, y):
    font = pygame.font.Font(score_font, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surface.blit(text_surface, text_rect)


def DrawHP(surface, hp, x, y):
    BAR_LENGTH = 150
    BAR_HEIGHT = 15
    fill = (hp / 100) * BAR_LENGTH
    outline = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fillbar = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fillbar)
    pygame.draw.rect(surface, WHITE, outline, 2)


def DrawLives(surface, lives):
    for i in range(lives):
        surface.blit(Lives_img, (SCREEN_WIDTH - 120 + i * 40, 8))


def NewRock():
    rock = Rock()
    sprites.add(rock)
    rocks.add(rock)


def DrawInit():
    screen.blit(bg_img, (0, 0))
    DrawText(screen, "Space Shooter", 64, SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.25)
    DrawText(
        screen,
        "Use arrow/AD keys to move left or right",
        24,
        SCREEN_WIDTH * 0.5,
        SCREEN_HEIGHT * 0.5,
    )
    if not hasGameOver:
        DrawText(
            screen,
            "Push any keys to start!",
            24,
            SCREEN_WIDTH * 0.5,
            SCREEN_HEIGHT * 0.75,
        )
    else:
        DrawText(
            screen,
            "You will do better next time!",
            24,
            SCREEN_WIDTH * 0.5,
            SCREEN_HEIGHT * 0.7,
        )
        DrawText(
            screen,
            "Push any keys to restart!",
            24,
            SCREEN_WIDTH * 0.5,
            SCREEN_HEIGHT * 0.75,
        )
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYUP:
                waiting = False
                return False

# Game Variables
clock = pygame.time.Clock()
running = True
showInit = True
hasGameOver = False

# BGM Start
pygame.mixer.music.play(-1, 0, 1000)
# Game Loop
while running:
    if showInit:
        if DrawInit():
            break
        # Initialize
        sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        items = pygame.sprite.Group()
        player = Player()
        sprites.add(Background(0, -SCREEN_HEIGHT))
        sprites.add(Background(0, 0))
        sprites.add(player)
        for i in range(8):
            NewRock()
        score = 0
        showInit = False
    clock.tick(FPS)
    sprites.update()
    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    # Bullet Hit Rock
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        score += hit.radius
        NewRock()
        ani = Explosion("rock", int(hit.radius * 2), hit.rect.center)
        sprites.add(ani)
        explode_sfxs[0].play()
        # Random Items
        if random.random() < 0.1:
            itemType = random.choice(list(item_imgs.keys()))
            item = Item(itemType, hit.rect.center)
            sprites.add(item)
            items.add(item)
    # Player Got Hit
    hits = pygame.sprite.spritecollide(
        player, rocks, True, pygame.sprite.collide_circle
    )
    for hit in hits:
        NewRock()
        player.hp -= hit.radius
        ani = Explosion("rock", int(hit.radius * 2), hit.rect.center)
        sprites.add(ani)
        explode_sfxs[1].play()
        # Check Game Over
        if player.hp < 0:
            player.lives -= 1
            player.hp = 0
            die_ani = Explosion("player", 250, player.rect.center)
            sprites.add(die_ani)
            die_sfx.play()
            player.hide()
    # Wait Animation End
    if player.lives == 0 and not (die_ani.alive()):
        showInit = True
        hasGameOver = True
    # Player Got Items
    hits = pygame.sprite.spritecollide(
        player, items, True, pygame.sprite.collide_circle
    )
    for hit in hits:
        if hit.type == "power":
            player.gotPower()
            item_sfxs[1].play()
        elif hit.type == "shield":
            player.hp += 20
            if player.hp > 100:
                player.hp = 100
            item_sfxs[0].play()
    # Update Screen
    sprites.draw(screen)
    DrawText(screen, "Score: " + str(int(score)), 22, SCREEN_WIDTH / 2, 2)
    DrawHP(screen, player.hp, 10, 10)
    DrawLives(screen, player.lives)
    pygame.display.update()
pygame.quit()
