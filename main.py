import os
import pygame
import time
import random
pygame.init()
pygame.font.init()

HEIGHT, WIDTH = 800, 1200
pygame.display.set_caption("Corona Invasion")
WIN = pygame.display.set_mode([WIDTH, HEIGHT])

# images
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
E_RED = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
E_BLUE = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
E_GREEN = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
L_YELLOW = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
L_RED = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
L_BLUE = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
L_GREEN = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
LASER_SHOT = pygame.mixer.Sound(os.path.join("assets", "heat-vision.wav"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# classes
class ship:
	def __init__(self, health=100):
		self.max_health = health
		self.health = health
		self.lasers = []
		self.count = 20
		self.laser_vel = 25

		

	def get_height(self):
		return self.img.get_height()

	def get_width(self):
		return self.img.get_width()
		

	def draw(self, window):
		WIN.blit(self.img, (self.x, self.y))
		for l in self.lasers:
			l.move()
			l.draw(WIN)
		if self.count < 30: #cooldown counter
			self.count += 1
		self.offscreen_laser()
		self.health_bar()
	
	def shoot(self):
		if self.count >= 20:
			LASER_SHOT.play()
			l = laser(self.x, self.y, self.laser_img, self.laser_vel)
			self.lasers.append(l)
			self.count -= 20

	def offscreen_laser(self):
		for l in self.lasers[:]:
			if l.offscreen():
				self.lasers.remove(l)

	def health_bar(self):
		health_bar_width = self.get_width()*(self.health/self.max_health)
		damage_bar_width = self.get_width()*((self.max_health-self.health)/self.max_health)
		health_bar_rect = pygame.Rect((self.x, self.y-12), (health_bar_width, 10))
		damage_bar = pygame.Rect((self.x + health_bar_width, self.y-12), (damage_bar_width, 10))
		pygame.draw.rect(WIN, (0,255,0), health_bar_rect)
		if self.health < self.max_health:
			pygame.draw.rect(WIN, (255,0,0), damage_bar)




class enemy(ship):
	def __init__(self):
		super().__init__()
		self.x = random.randrange(100, (WIDTH-100))
		self.y = random.randrange(-1500, 0)
		self.count = random.randrange(10, 20)
		self.map = {"red": (E_RED, L_RED, 50, 1), 
					"green": (E_GREEN, L_GREEN, 30, 2), 
					"blue": (E_BLUE, L_BLUE, 20, 3)}
		self.color = random.choice(["red", "green", "blue"])
		self.img = self.map[self.color][0]
		self.laser_img = self.map[self.color][1]
		self.max_health = self.map[self.color][2]
		self.health = self.map[self.color][2]
		self.vel = self.map[self.color][3]
		self.mask = pygame.mask.from_surface(self.img)

	def hit(self, p_ship):
		for l in self.lasers:
			if l.collision(p_ship):
				self.lasers.remove(l)
				p_ship.health -= 20

	def enemy_shoot(self):
		prob = random.randrange(500)
		if prob == 37 and self.y > 0:
			self.shoot()


class player(ship):
	def __init__(self, health=100):
		super().__init__(health)
		self.img = PLAYER_SHIP
		self.mask = pygame.mask.from_surface(self.img)
		self.x = WIDTH/2 - self.img.get_height()/2
		self.y = HEIGHT - 200
		self.vel = 10
		self.laser_img = L_YELLOW
		self.laser_vel = -40

	def hit(self, obj):
		for l in self.lasers:
			for e in obj:
				if l.collision(e):
					if l in self.lasers:
						self.lasers.remove(l)
						e.health -= 20


class laser:
	def __init__(self, x, y, img, laser_vel):
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)
		self.x = x
		self.y = y
		self.vel = laser_vel

	def draw(self, window):
		WIN.blit(self.img, (self.x, self.y))

	def move(self):
		self.y += self.vel

	def offscreen(self):
		if self.y > HEIGHT or self.y < 0:
			return True

	def collision(obj, self):
		return collide(obj, self)

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None



# game

def main():
	run = True
	FPS = 60
	clock = pygame.time.Clock()
	main_font = pygame.font.SysFont("sansregular", 50)
	lost_font = pygame.font.SysFont("sansregular", 100)


	level = 0
	lives = 3

	
	p_ship = player()
	enemies = []

	lost = False
	lost_count = 0	
	

	def redraw_window():
			WIN.blit(BG, (0, 0))

			level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
			lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))

			WIN.blit(lives_label, (WIDTH - 10 - lives_label.get_width(), 10))		
			WIN.blit(level_label, (10, 10))

			for e in enemies:
				e.draw(WIN)
			

			p_ship.draw(WIN)

			

			if lost:
				lost_label = lost_font.render("You Lost, sucker!!", 1, (255,255,255))
				WIN.blit(lost_label, (WIDTH/2-lost_label.get_width()/2, HEIGHT/3))


			pygame.display.update()

	while run:
		clock.tick(FPS)

		redraw_window()		
		
		if len(enemies) == 0:
			level += 1
			for i in range(level * 3):
				e = enemy()
				enemies.append(e)

		if lives == 0 or p_ship.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
		
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP] and p_ship.y - p_ship.vel > 0: 
			p_ship.y -= p_ship.vel
		if keys[pygame.K_DOWN] and p_ship.y + p_ship.vel < HEIGHT - p_ship.get_height(): 
			p_ship.y += p_ship.vel
		if keys[pygame.K_LEFT] and p_ship.x - p_ship.vel > 0: 
			p_ship.x -= p_ship.vel
		if keys[pygame.K_RIGHT] and p_ship.x + p_ship.vel < WIDTH -p_ship.get_width(): 
			p_ship.x += p_ship.vel
		if keys[pygame.K_SPACE]:
			p_ship.shoot()


		p_ship.hit(enemies)

		for e in enemies[:]:
			e.y += e.vel
			e.enemy_shoot()
			e.hit(p_ship)
			if e.y + e.get_height() > HEIGHT:
				lives -= 1
				enemies.remove(e)
			if e.health <= 0:
				enemies.remove(e)
		
		

def menu():
	run = True
	main_font = pygame.font.SysFont("sansregular", 120)
	sec_font = pygame.font.SysFont("sansregular", 80)
	count_menu = 0

	WIN.blit(BG, (0, 0))

	title = main_font.render("Corona Invasion", 1, (255,255,255))
	click_label = sec_font.render("Click the mouse to start", 1, (255,255,255))
	WIN.blit(title, (WIDTH/2-title.get_width()/2, HEIGHT/3))
	WIN.blit(click_label, (WIDTH/2-click_label.get_width()/2, HEIGHT/3 + 140))

	pygame.display.update()
	
	while run:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()
	pygame.quit()


menu()

