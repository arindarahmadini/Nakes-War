import pygame, random

#initialize
pygame.init()

# set the screen 
WIDTH, HEIGHT = 288,512
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nakes' War")

# set the icon
icon = pygame.image.load('Assets/logo.png')
pygame.display.set_icon(icon)

# load images
NURSE_SALLY = pygame.image.load('Assets/nurse.png')

# ...viruses
RED_VIRUS = pygame.image.load('Assets/red_kroni.png')
GREEN_VIRUS = pygame.image.load('Assets/green_kroni.png')
BLUE_VIRUS = pygame.image.load('Assets/blue_kroni.png')

# ... lasers
RED_LASER = pygame.image.load("Assets/pixel_laser_red.png")
GREEN_LASER = pygame.image.load("Assets/pixel_laser_green.png")
BLUE_LASER = pygame.image.load("Assets/pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("Assets/pixel_laser_yellow.png")

# ... background
BG = pygame.image.load("Assets/bg_game.png")
BG_SCALED = pygame.transform.scale(BG, (WIDTH, HEIGHT))
MAIN_BG = pygame.transform.scale(pygame.image.load("Assets/bg_main.png"),(WIDTH, HEIGHT))

# ... backsound
BG_SOUND = pygame.mixer.music.load("Sounds/sound_game.mp3")
pygame.mixer.music.play(-1)

# ... sound
SHOOT_SFX = pygame.mixer.Sound("Sounds/shoot.wav")
COUGH_SFX = pygame.mixer.Sound("Sounds/cough.wav")

# defining the lasers class
class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not(self.y <= height-120 and self.y >=0) 
        # if lasers are off the screen the result will be False, as the value inside brackets is True. 
        # so we add 'not' to know that the result is False

    def collision(self,obj):
        return collide(self,obj)

# defining the general class
class Object:
    COOLDOWN = 30 # Half of FPS
    def __init__(self,x,y,health=100,counter=0):
        self.x = x
        self.y = y
        self.health = health
        self.counter = counter
        self.object_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,window):
        window.blit(self.object_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10 
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.object_img.get_width()

    def get_height(self):
        return self.object_img.get_height()

# defining the player class
class Player(Object):
    def __init__(self,x,y,health=100,counter=0):
        super().__init__(x,y,health,counter)
        self.object_img = NURSE_SALLY
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.object_img)
        self.max_health = health
        self.counter = counter

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.counter += 1 #count virus hit by laser
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.object_img.get_height() + 10, self.object_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.object_img.get_height() + 10, self.object_img.get_width() * (self.health/self.max_health), 10))

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-35,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#defining the enemy class
class Enemy(Object):
    COLOR_MAP ={
                "red": (RED_VIRUS,RED_LASER),
                "green": (GREEN_VIRUS,GREEN_LASER),
                "blue": (BLUE_VIRUS,BLUE_LASER)
              }

    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.object_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.object_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-25,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

# defining the collision -- if the lasers and the objects are overlaping
def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x #if the object 1 hit object 2
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None # if there is no overlapping, it means (None) -> no overlapping = (x,y) -< the value is plus

# defining main loop
def main():
    run = True
    FPS = 60

    level = 0
    lives = 5
 
    main_font = pygame.font.SysFont('comicsans',23)
    lost_font = pygame.font.SysFont('comicsans',35)

    enemies = []
    wave_length = 5
    enemy_vel = 1 #double increased

    player_vel = 5
    laser_vel = 6
    player = Player(120,355)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    #color
    white = (255, 255, 255)
    black = (0, 0, 0)

    # display img code & render update
    def redraw_window():
        WIN.blit(BG_SCALED,(0,0))
        player.draw(WIN)

        pygame.draw.rect(BG_SCALED, white, [10, HEIGHT-60, 85, 50])
        pygame.draw.rect(BG_SCALED, white, [100, HEIGHT-60, 85, 50])
        pygame.draw.rect(BG_SCALED, white, [190, HEIGHT-60, 85, 50])

        level_label = main_font.render(f'Level:{level}',1,black)
        lives_label = main_font.render(f'Lives:{lives}',1,black)
        virus_label = main_font.render(f'Virus:{player.counter}',1,black)

        WIN.blit(lives_label,(24,HEIGHT-43))
        WIN.blit(virus_label,(113, HEIGHT-43))
        WIN.blit(level_label,(205, HEIGHT-43))

        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_font.render('You got infected!!!',1, black)
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 235))

        # render update
        pygame.display.update()

    # set the main loop

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <=0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(10, WIDTH -60), 
                        random.randrange(-700, -100), #make the enemies' position closer to the screen
                        random.choice(['red','green','blue'])) #the enemies' position before show in the screen
                enemies.append(enemy)

    # set the main loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #LEFT
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #RIGHT
            player.x += player_vel 
        if keys[pygame.K_w] and player.y - player_vel > 0: #UP
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 85 < HEIGHT: #DOWN
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()
            SHOOT_SFX.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 120) == 1:
                enemy.shoot()                
            if collide(enemy,player):
                player.health -= 15
                COUGH_SFX.play()
                lives -= 1
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() + 65 > HEIGHT:
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)



# main menu
def main_menu():
	title_font = pygame.font.SysFont('comicsans',18)
	run = True
	while run:
		WIN.blit(MAIN_BG,(0,0))
		title_label = title_font.render('PRESS THE MOUSE TO BEGIN',1,(255,255,255))
		WIN.blit(title_label,(5,225))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()
				
	pygame.quit() 

main_menu()
