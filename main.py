import pygame, sys, time
from levels import level1, level2, level3, level4, level5 
from random import randint
from button import Button
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 32
PLAYS = True
bullets = []
objects = []

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)

mpDestroy = pygame.mixer.Sound('sounds/destroy.wav')
mpStart = pygame.mixer.Sound('sounds/level_start.mp3')
mpFinish = pygame.mixer.Sound('sounds/level_finish.mp3')
mpLive = pygame.mixer.Sound('sounds/live.wav')
mpShot = pygame.mixer.Sound('sounds/shot.wav')
mpStar = pygame.mixer.Sound('sounds/star.wav')

imgStart = pygame.image.load('images/START.png')
imgLvl1 = pygame.image.load('images/LVL1.png')
imgLvl2 = pygame.image.load('images/LVL2.png')
imgLvl3 = pygame.image.load('images/LVL3.png')
imgLvl4 = pygame.image.load('images/LVL4.png')
imgLvl5 = pygame.image.load('images/LVL5.png')
imgBack = pygame.image.load('images/BACK.png')
imgQuit = pygame.image.load('images/QUIT.png')
imgBrick = pygame.image.load('images/block_brick.png')
imgWall = pygame.image.load('images/block_armor.png')
imgBush = pygame.image.load('images/block_bushes.png')
imgTanks = [
    pygame.image.load('images/tank1.png'),
    pygame.image.load('images/tank2.png'),
    pygame.image.load('images/tank3.png'),
    pygame.image.load('images/tank4.png'),
    pygame.image.load('images/tank5.png'),
    pygame.image.load('images/tank6.png'),
    pygame.image.load('images/tank7.png'),
    pygame.image.load('images/tank8.png'),
    ]
imgBangs = [
    pygame.image.load('images/bang1.png'),
    pygame.image.load('images/bang2.png'),
    pygame.image.load('images/bang3.png'),
    ]
imgBonuses = [
    pygame.image.load('images/bonus_star.png'),
    pygame.image.load('images/bonus_tank.png'),
    ]

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

MOVE_SPEED =    [1, 2, 2, 1, 2, 3, 3, 2]
BULLET_SPEED =  [4, 5, 6, 5, 5, 5, 6, 7]
BULLET_DAMAGE = [1, 1, 2, 3, 2, 2, 3, 4]
SHOT_DELAY =    [60, 50, 30, 40, 30, 25, 25, 30]

class UI:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        i = 0
        for obj in objects:
            if obj.type == 'tank':
                hp_label = fontUI.render('HP: ' + str(obj.hp), True, obj.color)
                tank_label = fontUI.render('Tank Rank: ' + str(obj.rank), True, obj.color)
                if i == 0:
                    window.blit(hp_label, (16, 16))
                    window.blit(tank_label, (16, 34))
                if i == 1:
                    window.blit(hp_label, (WIDTH - 150, 16))
                    window.blit(tank_label, (WIDTH - 150, 34))
                i += 1              

class Tank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'

        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.hp = 5
        self.shotTimer = 0

        self.moveSpeed = 5
        self.shotDelay = 60
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]

        self.rank = 0
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center = self.rect.center)

    def update(self):
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 3))
        self.rect = self.image.get_rect(center = self.rect.center)

        self.moveSpeed = MOVE_SPEED[self.rank]
        self.shotDelay = SHOT_DELAY[self.rank]
        self.bulletSpeed = BULLET_SPEED[self.rank]
        self.bulletDamage = BULLET_DAMAGE[self.rank]

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        
        oldX, oldY = self.rect.topleft
        if keys[self.keyLEFT]:
            self.rect.x -= self.moveSpeed
            self.direct = 3
        elif keys[self.keyRIGHT]:
            self.rect.x += self.moveSpeed
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y -= self.moveSpeed
            self.direct = 0
        elif keys[self.keyDOWN]:
            self.rect.y += self.moveSpeed
            self.direct = 2

        for obj in objects:
            if obj != self and obj.type == 'block' and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.keySHOT] and self.shotTimer == 0:
            mpShot.play()
            dx = DIRECTS[self.direct][0] * self.bulletSpeed
            dy = DIRECTS[self.direct][1] * self.bulletSpeed
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)
            self.shotTimer = self.shotDelay

        if self.shotTimer > 0: self.shotTimer -= 1

    def draw(self):
        pygame.draw.rect(window, self.color, self.rect)
        window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            game_over(self.color)

class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        bullets.append(self)
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage

    def update(self):
        self.px += self.dx
        self.py += self.dy

        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                if obj != self.parent and obj.type != 'bang' and obj.type != 'bonus':
                    if obj.rect.collidepoint(self.px, self.py):
                        obj.damage(self.damage)
                        bullets.remove(self)
                        Bang(self.px, self.py)
                        break

    def draw(self):
        pygame.draw.circle(window, 'yellow', (self.px, self.py), 2)

class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.2
        if self.frame >= 3: objects.remove(self)

    def draw(self):
        image = imgBangs[int(self.frame)]
        rect = image.get_rect(center = (self.px, self.py))
        window.blit(image, rect)
    
class Block:
    def __init__(self, px, py, size, hp, img):
        objects.append(self)
        self.type = 'block'
        self.img= img
        self.rect = pygame.Rect(px, py, size, size)
        self.hp = hp

    def update(self):
        pass

    def draw(self):
        window.blit(self.img, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0: 
            mpDestroy.play()
            objects.remove(self)

class Bonus:
    def __init__(self, px, py, bonusNum):
        objects.append(self)
        self.type = 'bonus'

        self.image = imgBonuses[bonusNum]
        self.rect = self.image.get_rect(center = (px, py))

        self.timer = 600
        self.bonusNum = bonusNum

    def update(self):
        if self.timer > 0: self.timer -= 1
        else: objects.remove(self)

        for obj in objects:
            if obj.type == 'tank' and self.rect.colliderect(obj.rect):
                if self.bonusNum == 0:
                    if obj.rank < len(imgTanks) - 1:
                        obj.rank += 1
                        mpStar.play()
                        objects.remove(self)
                        break
                elif self.bonusNum == 1:
                    obj.hp += 1
                    mpLive.play()
                    objects.remove(self)
                    break

    def draw(self):
        if self.timer % 30 < 15:
            window.blit(self.image, self.rect)

Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
Tank('red', 650, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN))
ui = UI()

'''for _ in range(50):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect): fined = True

        if not fined: break

    Block(x, y, TILE, 1)'''

def create_level(level):
    for y, row in enumerate(level):
        for x, char in enumerate(row):
            if char == '*':
                Block(x * 32, y * 32, TILE, 50, imgWall)
            if char == "B":
                Block(x * 32, y * 32, TILE, 3, imgBrick)
            elif char == "S":
                Block(x * 32, y * 32, TILE, 1, imgBush)

bonusTimer = 180

def play(level):
    global keys, bonusTimer, PLAYS

    create_level(level)
    mpStart.play()

    while PLAYS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                PLAYS = False

        window.fill((0, 0, 0))

        keys = pygame.key.get_pressed()
        if bonusTimer > 0: bonusTimer -= 1
        else:
            Bonus(randint(50, WIDTH - 50), randint(120, HEIGHT - 50), randint(0, len(imgBonuses) - 1))
            bonusTimer = randint(120, 240)
            
        for bullet in bullets: bullet.update()
        for obj in objects: obj.update()
        ui.update()

        for bullet in bullets: bullet.draw()
        for obj in objects: obj.draw()
        ui.draw()
        
        pygame.display.update()
        clock.tick(FPS)
        
    pygame.quit()

def game_over(color):   
    mpFinish.play() 
    while True:
        window.fill((0, 0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        if color == 'red':
            wins_text = fontUI.render('BLUE WINS', True, 'Blue')
        else:
            wins_text = fontUI.render('RED WINS', True, 'Red')
            
        game_over_text = fontUI.render('GAME OVER', True, (200, 200, 200))
        BACK_BUTTON = Button(image=imgBack, pos=(WIDTH / 2, 490), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")

        window.blit(game_over_text, (WIDTH / 2 - (game_over_text.get_width() / 2), (HEIGHT / 2) - 100))
        window.blit(wins_text, ((WIDTH / 2 - (wins_text.get_width() / 2)), ((HEIGHT / 2 + wins_text.get_height() * 1.5) - 100)))

        BACK_BUTTON.changeColor(MENU_MOUSE_POS)
        BACK_BUTTON.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    objects.clear()
                    bullets.clear()
                    Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
                    Tank('red', 650, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN))
                    ui = UI()
                    main_menu()

        pygame.display.update()
    
    pygame.quit() 

def levels():
    window.fill((0, 0, 0))
    while True:
        PLAYS = True
        window.fill((0, 0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        LVL_TEXT = fontUI.render("LEVELS", True, "#b68f40")
        LVL_RECT = LVL_TEXT.get_rect(center=(WIDTH / 2, 100))

        LVL1_BUTTON = Button(image=imgLvl1, pos=(WIDTH / 2, 150), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")
        LVL2_BUTTON = Button(image=imgLvl2, pos=(WIDTH / 2, 220), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")
        LVL3_BUTTON = Button(image=imgLvl3, pos=(WIDTH / 2, 290), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")
        LVL4_BUTTON = Button(image=imgLvl4, pos=(WIDTH / 2, 360), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")
        LVL5_BUTTON = Button(image=imgLvl5, pos=(WIDTH / 2, 420), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=imgBack, pos=(WIDTH / 2, 490), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")

        window.blit(LVL_TEXT, LVL_RECT)

        for button in [LVL1_BUTTON, LVL2_BUTTON, LVL3_BUTTON, LVL4_BUTTON, LVL5_BUTTON, BACK_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if LVL1_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(level1)
                elif LVL2_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(level2)
                elif LVL3_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(level3)
                elif LVL4_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(level4)
                elif LVL5_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play(level5)
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        window.fill((0, 0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = fontUI.render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(WIDTH / 2, 100))

        PLAY_BUTTON = Button(image=imgStart, pos=(WIDTH / 2, 200), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=imgQuit, pos=(WIDTH / 2, 300), 
                            text_input="", font=fontUI, base_color="#d7fcd4", hovering_color="White")

        window.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    levels()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()