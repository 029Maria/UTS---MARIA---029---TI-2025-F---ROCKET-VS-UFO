import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()

WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien vs Rocket")

WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128, 0, 128)
RED = (255,0,0)
YELLOW = (255,255,0)
NEON_GREEN = (57, 255, 20)

clock = pygame.time.Clock()

base_path = os.path.dirname(__file__)

def load_img(name):
    return pygame.image.load(os.path.join(base_path,name)).convert_alpha()

player_img = load_img("ROCKET.png")
enemy_img = load_img("UFO.png")
bullet_img = load_img("PELURU.png")

shoot_sound = pygame.mixer.Sound(os.path.join(base_path,"SHOOT.mp3"))
hit_sound = pygame.mixer.Sound(os.path.join(base_path,"HIT.mp3"))

try:
    bg = pygame.image.load(os.path.join(base_path,"BG.png"))
    bg = pygame.transform.scale(bg,(WIDTH,HEIGHT))
except:
    bg = None

bg_y = 0

class GameObject:
    def __init__(self,x,y,width,height,image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.transform.scale(image,(width,height))

    def draw(self,surface):
        surface.blit(self.image,(self.x,self.y))

    def get_rect(self):
        return pygame.Rect(self.x,self.y,self.width,self.height)

class Player(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y,60,60,player_img)
        self.speed = 6

    def move(self,keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.x = max(0,min(self.x,WIDTH-self.width))

class Enemy(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y,50,50,enemy_img)
        self.speed = 2

    def move(self):
        global lives
        self.y += self.speed

        if self.y > HEIGHT:
            self.y = -50
            self.x = random.randint(0,WIDTH-50)
            lives -= 1

class Bullet(GameObject):
    def __init__(self,x,y):
        super().__init__(x,y,15,25,bullet_img)
        self.speed = 8

    def move(self):
        self.y -= self.speed

def reset_game():
    global lives, explosions

    player = Player(370,420)

    enemies = []
    bullets = []

    for i in range(5):
        enemies.append(Enemy(random.randint(0,WIDTH-50),random.randint(-300,-50)))

    score = 0
    start_time = pygame.time.get_ticks()
    lives = 5
    explosions = []

    return player,enemies,bullets,score,start_time

player,enemies,bullets,score,start_time = reset_game()

font = pygame.font.SysFont(None,36)

target_score = 10
time_limit = 20

game_over = False
win = False

running = True
while running:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE and not game_over:
                bullets.append(Bullet(player.x+20,player.y))
                shoot_sound.play()

            if event.key == pygame.K_r and game_over:
                player,enemies,bullets,score,start_time = reset_game()
                game_over = False
                win = False

    keys = pygame.key.get_pressed()

    elapsed_time = (pygame.time.get_ticks() - start_time)/1000
    remaining_time = max(0,int(time_limit - elapsed_time))

    if not game_over:
        player.move(keys)

        for bullet in bullets:
            bullet.move()

        for enemy in enemies:
            enemy.speed = 2 + score // 10
            enemy.move()

        for bullet in bullets[:]:
            for enemy in enemies:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    score += 1
                    hit_sound.play()

                    explosions.append([enemy.x+25, enemy.y+25, 10])

                    enemy.y = -50
                    enemy.x = random.randint(0,WIDTH-50)

                    if bullet in bullets:
                        bullets.remove(bullet)

        if score >= target_score:
            win = True
            game_over = True

        if remaining_time <= 0 or lives <= 0:
            if score < target_score:
                win = False
                game_over = True

    if bg:
        bg_y += 1
        if bg_y >= HEIGHT:
            bg_y = 0
        screen.blit(bg,(0,bg_y))
        screen.blit(bg,(0,bg_y-HEIGHT))
    else:
        screen.fill(BLACK)

    player.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    for exp in explosions[:]:
        pygame.draw.circle(screen,(255,100,0),(exp[0],exp[1]),exp[2])
        exp[2] += 2
        if exp[2] > 30:
            explosions.remove(exp)

    screen.blit(font.render("Score: "+str(score),True,YELLOW),(10,10))
    screen.blit(font.render("Time: "+str(remaining_time),True,RED),(680,10))
    screen.blit(font.render("Lives: "+str(lives),True,NEON_GREEN),(350,10))

    if game_over:
        text = "MENANG!" if win else "KALAH!"
        screen.blit(font.render(text,True,WHITE),(330,220))
        screen.blit(font.render("Press R to Restart",True,WHITE),(280,260))

    pygame.display.update()

pygame.quit()
sys.exit()