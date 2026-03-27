import pygame
import sys
import random
pygame.font.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

WIDTH = 800
HEIGHT = 500
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Campsite Cat')
clock = pygame.time.Clock()
Font = pygame.font.SysFont('Arial', 24,True)
EndGameFont = pygame.font.SysFont('TimesNewRoman', 48,True)


try:
    background = pygame.image.load('Graphics/Background.png').convert_alpha()
    BG = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    BG = pygame.Surface((WIDTH, HEIGHT))
    BG.fill((50, 50, 50))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprites = {
            'idle': [pygame.image.load('Graphics/Stand.png').convert_alpha()],
            'Walk': [pygame.image.load(f'Graphics/Walk{i}.png').convert_alpha() for i in range(1, 7)],
            'Run': [pygame.image.load(f'Graphics/Run{i}.png').convert_alpha() for i in range(1, 5)],
            'Jump': [pygame.image.load(f'Graphics/Jump{i}.png').convert_alpha() for i in range(1, 3)],
            'Fall': [pygame.image.load('Graphics/Fall1.png').convert_alpha()],
            'Land': [pygame.image.load(f'Graphics/Land{i}.png').convert_alpha() for i in range(1, 3)],
            'Meow': [pygame.image.load(f'Graphics/Meow{i}.png').convert_alpha() for i in range(1, 3)],
            "Sleep": [pygame.image.load(f'Graphics/Sleep{i}.png').convert_alpha() for i in range(1, 3)],
            'FallingAsleep': [pygame.image.load(f'Graphics/FallingAsleep{i}.png').convert_alpha() for i in range(1, 3)]
        }
        
        # Define specific speeds for each status
        self.speeds = {
            'idle': 0.2,
            'Walk': 0.2,
            'Run': 0.2,
            'Jump': 0.2,
            'Fall': 0.2,
            'Land': 0.2,
            'Meow': 0.05, # Much slower
            'Sleep':0.05,
            "FallingAsleep":0.04
        }

        self.status = 'idle'
        self.current_sprite = 0
        self.facing_right = True
        self.image = self.sprites[self.status][self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH // 2, HEIGHT)
        self.gravity = 0
        self.has_food = False
        self.score =0
        self.meow_played = False

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.facing_right = True
            self.status = 'Run' if keys[pygame.K_LSHIFT] else 'Walk'
            self.rect.x += 7 if keys[pygame.K_LSHIFT] else 5
        elif keys[pygame.K_LEFT]:
            self.facing_right = False
            self.status = 'Run' if keys[pygame.K_LSHIFT] else 'Walk'
            self.rect.x -= 7 if keys[pygame.K_LSHIFT] else 5
        else:
            self.status = 'idle'

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

    def apply_gravity(self):
        self.gravity += 1.0
        self.rect.y += self.gravity
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.gravity = 0
            if self.status == 'Fall':
                if self.has_food:
                    self.status = 'Meow'
                    self.current_sprite = 0
                    self.has_food = False
                else:
                    self.status = 'Land'
                    self.current_sprite = 0

    def animate(self):
        animation = self.sprites[self.status]
        
        # Use the speed specific to the current status
        speed = self.speeds.get(self.status, 0.2)
        self.current_sprite += speed
        
        if self.current_sprite >= len(animation):
            if self.status in ['Land', 'Meow']:
                self.status = 'idle'
                self.meow_played = False
            elif self.status == 'FallingAsleep':
                self.status = 'Sleep'
            self.current_sprite = 0
        
        image = animation[int(self.current_sprite)]
        self.image = image if self.facing_right else pygame.transform.flip(image, True, False)

    def update(self):
        if self.status in ['Land', 'Meow','Sleep','FallingAsleep']:
            self.apply_gravity()
            self.animate()
            return

        self.get_input()
        self.apply_gravity()

        if self.rect.bottom < HEIGHT:
            self.status = 'Jump' if self.gravity < 0 else 'Fall'
        
        if self.rect.bottom >= HEIGHT and self.has_food:
            self.status = 'Meow'
            self.current_sprite = 0
            self.has_food = False

        self.animate()

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('Graphics/Catfood.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > 1000:
            self.kill()
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.Font = pygame.font.SysFont('Arial', 24,True)
        self.image = self.Font.render('Z', True, (0,0,0))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.direction = pygame.math.Vector2(random.uniform(-0.5, 0.5), -1)
        self.alpha = 255
    def update(self):
        self.pos += self.direction
        self.rect.center = self.pos
        self.alpha -= 3 # Fade speed
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)          

def main():
    moving_sprites = pygame.sprite.Group()
    cat = Player()
    moving_sprites.add(cat)
    food_group = pygame.sprite.Group()
    particle_group = pygame.sprite.Group()
    Bg_music = pygame.mixer.Sound('Graphics/Music.mp3')
    Bg_music.set_volume(0.5)
    Bg_music.play(-1)  # Loop the music
    cat_purr = pygame.mixer.Sound('Graphics/CatPurr.wav')
    cat_purr.set_volume(0.5)
    cat_purr.play(-1)  # Loop the purring sound
    cat_meow = pygame.mixer.Sound('Graphics/CatMeow.wav')
    cat_meow.set_volume(0.2)
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    fade_alpha = 255
    spawn_interval = 4000
    last_spawn_time = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and cat.status not in ['Meow', 'Sleep', 'FallingAsleep']:
                        if cat.rect.bottom >= HEIGHT:
                            cat.gravity = -20
                    
        if cat.status not in ['Meow', 'Sleep', 'FallingAsleep']:
            if current_time - last_spawn_time > spawn_interval:
                food_group.add(Food(random.randint(50, WIDTH - 50), random.randint(250, 400)))
                last_spawn_time = current_time

        if pygame.sprite.spritecollide(cat, food_group, True):
            cat.has_food = True
            cat.score += 1 
        if cat.score >= 20 and cat.status not in ["Sleep", "FallingAsleep"]:
            cat.status = "FallingAsleep"
            cat.current_sprite = 0 
        if cat.status in ["Sleep", "FallingAsleep"]:
            if fade_alpha < 255:
                fade_alpha += 0.5
                fade_surface.set_alpha(fade_alpha)
            elif fade_alpha == 255:
                pygame.time.delay(1000) 
                running = False
                

        else:
            if fade_alpha>0:
                fade_alpha -= 1.0
                fade_surface.set_alpha(fade_alpha)        
                
                
        if cat.status == 'Sleep' and  random.randint(0,20)==0:
            new_z = Particle(cat.rect.centerx + 10, cat.rect.top + 10)
            particle_group.add(new_z)   
        if cat.status == 'Meow':
            if not cat.meow_played:
                cat_meow.play()
                cat.meow_played = True     
        
       
            
        screen.blit(BG, (0, 0))
        moving_sprites.update()
        food_group.update()
        moving_sprites.draw(screen)
        food_group.draw(screen)
        score_text = Font.render(f'Score: {cat.score}', True, (255, 255, 255))
        shadow_text = Font.render(f'Score: {cat.score}', True, (0, 0, 0))
        particle_group.update()
        particle_group.draw(screen)
        Sleeptext = EndGameFont.render('The Cat is Sleeping...', True,  "#5CFFFFFF")
        screen.blit(shadow_text, (10 + 2, 10 + 2))
        screen.blit(score_text, (10, 10))
        if fade_alpha > 0:
            screen.blit(fade_surface, (0, 0))
        if cat.status == 'Sleep':
            screen.blit(Sleeptext, (WIDTH // 2 - Sleeptext.get_width() // 2, (HEIGHT // 2 - Sleeptext.get_height() // 2) - 15))


        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()