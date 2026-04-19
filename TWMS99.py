import pygame
from sys import exit
import sys
import random
import os
import json
import asyncio 
import math 


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

GAME_WIDTH = 1020
GAME_HEIGHT = 650

class DataStorage:
    def __init__(self):
        self.default_save = {"high_score": 0, "total_games_played": 0, "high_phil_score": 0}
        self.save_data = self.default_save.copy()
        self.load_data()

    def load_data(self):
        if os.path.exists("savegame.json"):
            with open("savegame.json", "r") as file:
                try:
                    self.save_data = json.load(file)
                    if "high_phil_score" not in self.save_data:
                        self.save_data["high_phil_score"] = 0
                except:
                    self.save_data = self.default_save.copy()

    def save_data_to_file(self):
        with open("savegame.json", "w") as file:
            json.dump(self.save_data, file, indent=4)

    def update_stats(self, new_score, new_phil_score):
        self.save_data["total_games_played"] += 1
        if new_score > self.save_data["high_score"]:
            self.save_data["high_score"] = new_score
            
        if new_phil_score > self.save_data["high_phil_score"]:
            self.save_data["high_phil_score"] = new_phil_score
            
        self.save_data_to_file()

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, GAME_WIDTH / 8, GAME_HEIGHT / 2, 44, 44)
        self.img = img

class Pipe(pygame.Rect):
    def __init__(self, img, y_pos):
        pygame.Rect.__init__(self, GAME_WIDTH, y_pos, 100, 100)
        self.img = img
        self.passed = False
        self.angle = random.randint(0, 360) 
        self.spin_speed = random.randint(2, 6) * random.choice([-1, 1])

class Gabagool(pygame.Rect):
    def __init__(self, img, y_pos):
        pygame.Rect.__init__(self, GAME_WIDTH, y_pos, 50, 50)
        self.img = img

class Duck(pygame.Rect):
    def __init__(self, img, y_pos):
        pygame.Rect.__init__(self, GAME_WIDTH, y_pos, 150, 120)
        self.img = img

class Phil(pygame.Rect):
    def __init__(self, img, y_pos):
        pygame.Rect.__init__(self, GAME_WIDTH, y_pos, 44, 44)
        self.img = img

class Livia(pygame.Rect):
    def __init__(self, img, y_pos):
        pygame.Rect.__init__(self, GAME_WIDTH, y_pos, 54, 54)
        self.img = img

class GameEngine:
    def __init__(self):
        pygame.init() 
        self.window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("The waste management simulator '99")
        self.clock = pygame.time.Clock()

       
        try:
            bg_image_raw = pygame.image.load(resource_path("assets/sopbg.png"))
            self.bg_img_normal = pygame.transform.scale(bg_image_raw, (GAME_WIDTH + 40, GAME_HEIGHT + 40)).convert_alpha()
        except:
            self.bg_img_normal = pygame.Surface((GAME_WIDTH + 40, GAME_HEIGHT + 40))
            self.bg_img_normal.fill((50, 150, 200)) 

        try:
            pine_bg_raw = pygame.image.load(resource_path("assets/pinebarrens.png"))
            self.bg_img_pine = pygame.transform.scale(pine_bg_raw, (GAME_WIDTH + 40, GAME_HEIGHT + 40)).convert_alpha()
        except:
            self.bg_img_pine = pygame.Surface((GAME_WIDTH + 40, GAME_HEIGHT + 40))
            self.bg_img_pine.fill((200, 200, 220))

       
        try:
            logo_raw = pygame.image.load(resource_path("assets/logo.png"))
            self.logo_img = pygame.transform.scale(logo_raw, (500, 160)) 
        except:
            self.logo_img = None

        self.active_bg = self.bg_img_normal

        
        try:
            bird_img = pygame.image.load(resource_path("assets/soprano.png"))
            self.bird_img = pygame.transform.scale(bird_img, (44, 44))
            
            obstacle = pygame.image.load(resource_path("assets/prozac.png"))
            self.obstacle_img = pygame.transform.scale(obstacle, (100, 100))
            
            gaba_img = pygame.image.load(resource_path("assets/gabagool.png"))
            self.gabagool_img = pygame.transform.scale(gaba_img, (50, 50))

            duck_image = pygame.image.load(resource_path("assets/ducks.png"))
            self.duck_img = pygame.transform.scale(duck_image, (150, 120)) 
            
            phil_img = pygame.image.load(resource_path("assets/phil.png"))
            self.phil_boss_img = pygame.transform.scale(phil_img, (44, 44))
            
            livia_img = pygame.image.load(resource_path("assets/livia.png"))
            self.livia_boss_img = pygame.transform.scale(livia_img, (54, 54))
        except Exception as e:
            print(f"Missing a sprite image! Make sure they are in the 'assets' folder. Error: {e}")
            self.bird_img = pygame.Surface((44, 44)); self.bird_img.fill((255, 215, 0))
            self.obstacle_img = pygame.Surface((100, 100)); self.obstacle_img.fill((0, 255, 0))
            self.gabagool_img = pygame.Surface((50, 50)); self.gabagool_img.fill((255, 0, 0))
            self.duck_img = pygame.Surface((150, 120)); self.duck_img.fill((255, 165, 0))
            self.phil_boss_img = pygame.Surface((44, 44)); self.phil_boss_img.fill((255, 0, 255))
            self.livia_boss_img = pygame.Surface((54, 54)); self.livia_boss_img.fill((0, 255, 255))

        # load audio from assets/
        try:
            pygame.mixer.music.load(resource_path("assets/Do.mp3"))
            pygame.mixer.music.set_volume(0.7) 
            pygame.mixer.music.play(-1)
        except:
            pass

        try:
            self.game_over_sound = pygame.mixer.Sound(resource_path("assets/culo.mp3"))
            self.game_over_sound.set_volume(0.8) 
        except:
            self.game_over_sound = None

        try:
            self.hehe_sound = pygame.mixer.Sound(resource_path("assets/hehe.mp3"))
            self.hehe_sound.set_volume(1.0) 
        except:
            self.hehe_sound = None

        try:
            self.gaba_sound = pygame.mixer.Sound(resource_path("assets/eatingsound.mp3"))
            self.gaba_sound.set_volume(1.0) 
        except:
            self.gaba_sound = None

        try:
            self.panic_sound = pygame.mixer.Sound(resource_path("assets/breathing.mp3"))
            self.panic_sound.set_volume(1.0)
        except:
            self.panic_sound = None
            
        try:
            self.curse_sound = pygame.mixer.Sound(resource_path("assets/curse.mp3"))
            self.curse_sound.set_volume(1.0)
        except:
            self.curse_sound = None
            
        try:
            self.pooryou_sound = pygame.mixer.Sound(resource_path("assets/pooryou.mp3"))
            self.pooryou_sound.set_volume(1.0)
        except:
            self.pooryou_sound = None

        self.storage = DataStorage()
        self.bird = Bird(self.bird_img)
        self.pipes = []
        self.gabagools = [] 
        self.ducks = [] 
        self.phils = [] 
        self.livias = []
        
        # physics and game state
        self.velocity_x = -2 
        self.velocity_y = 0 
        self.gravity = 0.4
        self.score = 0
        self.phil_score = 0 
        self.game_over = False
        self.game_state = "menu"
        self.shake_timer = 0 
        
        self.target_bg_type = 0 
        self.is_bg_fading = False
        self.bg_fade_progress = 0
        self.next_bg = None

        self.is_panicking = False
        self.panic_end_time = 0

        self.current_spawn_rate = 2000 
        self.current_phil_rate = 15000 
        
        self.create_pipes_timer = pygame.USEREVENT + 0
        pygame.time.set_timer(self.create_pipes_timer, self.current_spawn_rate)
        
        self.create_gaba_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.create_gaba_timer, 3500)

        self.create_duck_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.create_duck_timer, 10000)
        
        self.create_phil_timer = pygame.USEREVENT + 3
        pygame.time.set_timer(self.create_phil_timer, self.current_phil_rate)
        
        self.create_livia_timer = pygame.USEREVENT + 4
        pygame.time.set_timer(self.create_livia_timer, 22000) 

    def add_score(self, amount):
        old_score = self.score
        self.score += amount
        self.update_difficulty()
        
        if (old_score // 10) < (self.score // 10) and self.score >= 10:
            if self.hehe_sound:
                self.hehe_sound.play()

    def update_difficulty(self):
        old_rate = self.current_spawn_rate
        old_phil_rate = self.current_phil_rate
        
        new_target = (self.score // 40) % 2
        if new_target != self.target_bg_type:
            self.target_bg_type = new_target
            self.next_bg = self.bg_img_pine if new_target == 1 else self.bg_img_normal
            self.next_bg.set_alpha(0)
            self.is_bg_fading = True
            self.bg_fade_progress = 0
        
        if self.score < 5: 
            self.velocity_x = -2
            self.current_spawn_rate = 2000 
            self.current_phil_rate = 15000
        elif self.score < 10: 
            self.velocity_x = -3
            self.current_spawn_rate = 1500 
            self.current_phil_rate = 10000 
        elif self.score < 15: 
            self.velocity_x = -4
            self.current_spawn_rate = 1100 
            self.current_phil_rate = 7000 
        elif self.score < 20: 
            self.velocity_x = -5
            self.current_spawn_rate = 800  
            self.current_phil_rate = 5000 
        else: 
            self.velocity_x = -6
            self.current_spawn_rate = 600  
            self.current_phil_rate = 4000 

        if old_rate != self.current_spawn_rate:
            pygame.time.set_timer(self.create_pipes_timer, self.current_spawn_rate)
            
        if old_phil_rate != self.current_phil_rate:
            pygame.time.set_timer(self.create_phil_timer, self.current_phil_rate)

    def draw_text_with_outline(self, text, font, text_color, center_x, y_pos, align_left=False):
        main_text = font.render(text, True, text_color)
        shadow = font.render(text, True, (0, 0, 0)) 
        
        if align_left:
            x = center_x
        else:
            x = center_x - main_text.get_width() / 2
            
        y = y_pos

        offsets = [
            (-2, 0), (2, 0), (0, -2), (0, 2), 
            (-2, -2), (2, -2), (-2, 2), (2, 2), 
            (3, 3), (4, 4) 
        ]
        
        for ox, oy in offsets:
            self.window.blit(shadow, (x + ox, y + oy))
            
        self.window.blit(main_text, (x, y))

    def create_pipes(self):
        pipe_height = 100
        random_y = random.randint(0, GAME_HEIGHT - pipe_height) 
        random_pipe = Pipe(self.obstacle_img, random_y)
        self.pipes.append(random_pipe)

    def create_gabagool(self):
        random_y = random.randint(50, GAME_HEIGHT - 100)
        gaba = Gabagool(self.gabagool_img, random_y)
        self.gabagools.append(gaba)

    def create_duck(self):
        random_y = random.randint(50, GAME_HEIGHT - 100)
        duck = Duck(self.duck_img, random_y)
        self.ducks.append(duck)
        
    def create_phil(self):
        random_y = random.randint(50, GAME_HEIGHT - 150)
        phil = Phil(self.phil_boss_img, random_y)
        self.phils.append(phil)
        
    def create_livia(self):
        random_y = random.randint(50, GAME_HEIGHT - 150)
        livia = Livia(self.livia_boss_img, random_y)
        self.livias.append(livia)

    def reset_game(self):
        self.bird.x = GAME_WIDTH / 8 
        self.bird.y = GAME_HEIGHT / 2
        self.pipes.clear()
        self.gabagools.clear() 
        self.ducks.clear() 
        self.phils.clear()
        self.livias.clear()
        self.score = 0
        self.phil_score = 0 
        self.velocity_y = -6
        self.game_over = False
        self.shake_timer = 0 
        
        self.target_bg_type = 0
        self.active_bg = self.bg_img_normal
        self.active_bg.set_alpha(255) 
        self.is_bg_fading = False
        self.bg_fade_progress = 0
        
        self.is_panicking = False
        if self.panic_sound:
            self.panic_sound.stop()
            
        self.update_difficulty() 

    def trigger_game_over(self):
        if not self.game_over: 
            self.game_over = True
            self.shake_timer = 25 
            self.storage.update_stats(self.score, self.phil_score)
            
            if self.game_over_sound:
                self.game_over_sound.play() 
            if self.panic_sound:
                self.panic_sound.stop() 

    def move(self):
        if self.is_panicking and pygame.time.get_ticks() > self.panic_end_time:
            self.is_panicking = False
            if self.panic_sound:
                self.panic_sound.stop()

        keys = pygame.key.get_pressed()
        self.gravity = 0.4 
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.bird.x -= 5 
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.bird.x += 5 

        self.velocity_y += self.gravity
        self.bird.y += self.velocity_y

        if self.bird.x < 0:
            self.bird.x = 0
        if self.bird.x > GAME_WIDTH - self.bird.width:
            self.bird.x = GAME_WIDTH - self.bird.width

        if self.bird.y > GAME_HEIGHT or self.bird.y < 0:
            self.trigger_game_over() 
            return

        for pipe in self.pipes:
            pipe.x += self.velocity_x
            
            if not pipe.passed and self.bird.x > pipe.x + pipe.width:
                self.add_score(1) 
                pipe.passed = True
            
            bird_hitbox = self.bird.inflate(-12, -12) 
            pipe_hitbox = pipe.inflate(-30, -30) 
            
            if bird_hitbox.colliderect(pipe_hitbox):
                self.trigger_game_over() 
                return
                
        while len(self.pipes) > 0 and self.pipes[0].x < -100:
            self.pipes.pop(0)

        for gaba in self.gabagools[:]: 
            gaba.x += self.velocity_x 
            if self.bird.inflate(-10, -10).colliderect(gaba.inflate(-10, -10)):
                self.add_score(2) 
                if self.gaba_sound:
                    self.gaba_sound.play()
                self.gabagools.remove(gaba) 
            elif gaba.x < -100:
                self.gabagools.remove(gaba) 
                
        for duck in self.ducks[:]:
            duck.x += (self.velocity_x - 1) 
            
            if self.bird.inflate(-10, -10).colliderect(duck.inflate(-10, -10)):
                if not self.is_panicking:
                    self.is_panicking = True
                    self.panic_end_time = pygame.time.get_ticks() + 4000 
                    if self.panic_sound:
                        self.panic_sound.play(-1) 
                        
                self.ducks.remove(duck) 
            elif duck.x < -100:
                self.ducks.remove(duck)
                
        for phil in self.phils[:]:
            phil.x += (self.velocity_x - 1) 
            
            if self.bird.inflate(-15, -15).colliderect(phil.inflate(-15, -15)):
                if self.curse_sound:
                    self.curse_sound.play()
                self.phil_score += 1
                self.phils.remove(phil)
            elif phil.x < -100:
                self.phils.remove(phil)
                
        for livia in self.livias[:]:
            livia.x += (self.velocity_x - 1)
            
            if self.bird.inflate(-15, -15).colliderect(livia.inflate(-15, -15)):
                if self.pooryou_sound:
                    self.pooryou_sound.play()
                self.livias.remove(livia)
            elif livia.x < -100:
                self.livias.remove(livia)

    def draw_menu(self):
        self.window.blit(self.active_bg, (-20, -20)) 
        
        if self.logo_img:
            self.window.blit(self.logo_img, (GAME_WIDTH/2 - self.logo_img.get_width()/2, 100))
        else:
            font_title = pygame.font.SysFont("Comic Sans MS", 35, bold=True) 
            self.draw_text_with_outline("The waste management simulator '99", font_title, (255, 215, 0), GAME_WIDTH/2, 130)
            
        font_options = pygame.font.SysFont("Arial", 35, bold=True)
        self.draw_text_with_outline("[1]: Start Game", font_options, (255, 255, 255), GAME_WIDTH/2, 300)
        self.draw_text_with_outline("[2]: High Score", font_options, (255, 255, 255), GAME_WIDTH/2, 370)
        self.draw_text_with_outline("[3]: Quit", font_options, (255, 255, 255), GAME_WIDTH/2, 440)

    def draw_high_scores(self):
        self.window.blit(self.active_bg, (-20, -20)) 
        font_title = pygame.font.SysFont("Segoe UI", 65, bold=True) 
        font_options = pygame.font.SysFont("Segoe UI", 45, bold=True) 

        self.draw_text_with_outline("Records", font_title, (255, 215, 0), GAME_WIDTH/2, 100)
        
        self.draw_text_with_outline(f"Best Score: {int(self.storage.save_data['high_score'])}", font_options, (255, 255, 255), GAME_WIDTH/2, 220)
        self.draw_text_with_outline(f"Where's my fkn money Record: {int(self.storage.save_data['high_phil_score'])}", font_options, (255, 80, 80), GAME_WIDTH/2, 290)
        self.draw_text_with_outline(f"Played: {self.storage.save_data['total_games_played']}", font_options, (200, 200, 200), GAME_WIDTH/2, 360)
        
        self.draw_text_with_outline("Press ESC to Back", font_options, (255, 215, 0), GAME_WIDTH/2, 480)

    def draw_game(self):
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.randint(-15, 15)
            shake_y = random.randint(-15, 15)
            self.shake_timer -= 1
            
        self.window.blit(self.active_bg, (-20 + shake_x, -20 + shake_y)) 

        if self.is_bg_fading:
            self.bg_fade_progress += 3 
            if self.bg_fade_progress >= 255:
                self.bg_fade_progress = 255
                
            self.next_bg.set_alpha(self.bg_fade_progress)
            self.window.blit(self.next_bg, (-20 + shake_x, -20 + shake_y))
            
            if self.bg_fade_progress == 255:
                self.active_bg = self.next_bg
                self.is_bg_fading = False
                self.bg_fade_progress = 0
            
        self.window.blit(self.bird.img, (self.bird.x + shake_x, self.bird.y + shake_y))

        for gaba in self.gabagools:
            self.window.blit(gaba.img, (gaba.x + shake_x, gaba.y + shake_y))
            
        for duck in self.ducks:
            self.window.blit(duck.img, (duck.x + shake_x, duck.y + shake_y))
            
        for phil in self.phils:
            self.window.blit(phil.img, (phil.x + shake_x, phil.y + shake_y))
            
        for livia in self.livias:
            self.window.blit(livia.img, (livia.x + shake_x, livia.y + shake_y))

        for pipe in self.pipes:
            if not self.game_over:
                pipe.angle = (pipe.angle + pipe.spin_speed) % 360 
            
            rotated_prozac = pygame.transform.rotate(pipe.img, pipe.angle)
            prozac_rect = rotated_prozac.get_rect(center=pipe.center)
            self.window.blit(rotated_prozac, (prozac_rect.x + shake_x, prozac_rect.y + shake_y))
            
        if self.is_panicking and not self.game_over:
            pulse = abs(math.sin(pygame.time.get_ticks() / 200)) 
            alpha_value = int(80 + (pulse * 100)) 
            
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha_value)) 
            self.window.blit(overlay, (0, 0))
        
        text_font = pygame.font.SysFont("Segoe UI", 50, bold=True)

        if self.game_over:
            if self.shake_timer <= 0:
                self.draw_text_with_outline(f"Game over: {int(self.score)}", text_font, (255, 80, 80), GAME_WIDTH/2, GAME_HEIGHT/2 - 50)
                menu_font = pygame.font.SysFont("Segoe UI", 30, bold=True)
                self.draw_text_with_outline("Press 'R' or ENTER to Restart", menu_font, (255, 255, 255), GAME_WIDTH/2, GAME_HEIGHT/2 + 15)
                self.draw_text_with_outline("Press ESC for Menu", menu_font, (200, 200, 200), GAME_WIDTH/2, GAME_HEIGHT/2 + 55)
        else:
            hud_text = f"score: {int(self.score)}  |  Where's my fkn money counter: {self.phil_score}"
            hud_font = pygame.font.SysFont("Segoe UI", 30, bold=True)
            self.draw_text_with_outline(hud_text, hud_font, (255, 255, 255), 15, 5, align_left=True)

    async def run(self):
        while True: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if event.type == self.create_pipes_timer and not self.game_over and self.game_state == "playing":
                    self.create_pipes()
                if event.type == self.create_gaba_timer and not self.game_over and self.game_state == "playing":
                    self.create_gabagool()
                if event.type == self.create_duck_timer and not self.game_over and self.game_state == "playing":
                    self.create_duck()
                if event.type == self.create_phil_timer and not self.game_over and self.game_state == "playing":
                    self.create_phil()
                if event.type == self.create_livia_timer and not self.game_over and self.game_state == "playing":
                    self.create_livia()
                
                if event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_1:
                            self.game_state = "playing"
                            self.reset_game()
                        elif event.key == pygame.K_2:
                            self.game_state = "high_scores"
                        elif event.key == pygame.K_3:
                            pygame.quit()
                            exit()
                    
                    elif self.game_state == "high_scores":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                    
                    elif self.game_state == "playing":
                        if not self.game_over:
                            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP, pygame.K_w):
                                self.velocity_y = -6 
                        
                        else:
                            if self.shake_timer <= 0:
                                if event.key in (pygame.K_r, pygame.K_RETURN): 
                                    self.reset_game()
                                    if self.game_over_sound:
                                        self.game_over_sound.stop()
                                        
                                elif event.key == pygame.K_ESCAPE:
                                    self.game_state = "menu"
                                    if self.game_over_sound:
                                        self.game_over_sound.stop()

            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "high_scores":
                self.draw_high_scores()
            elif self.game_state == "playing":
                if not self.game_over:
                    self.move()
                self.draw_game()
                
            pygame.display.update()
            self.clock.tick(60)
            
            await asyncio.sleep(0) 

async def main():
    game = GameEngine()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
