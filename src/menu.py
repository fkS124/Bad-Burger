import math
from itertools import cycle
import pygame
import os
import src.animation as animation
import src.ratatouille as ratatouille
import random
from .utils import *
import time


class Menu:
    def __init__(self, screen: pygame.surface.Surface, clock: pygame.time.Clock):
        self.settings = get_json("src/settings")

        # ----------------------- SCREEN -------------------------------- #
        self.screen: pygame.surface.Surface = screen
        self.W: int = self.settings["WIDTH"]
        self.H: int = self.settings["HEIGHT"]

        # ---------------------- VARIABLES ------------------------------ #
        self.logo: pygame.surface.Surface = load_alpha("data/assets/logo.png")
        self.music_on: pygame.surface.Surface = load_alpha("data/assets/music_on.png")
        self.music_off: pygame.surface.Surface = load_alpha("data/assets/music_off.png")
        self.table: pygame.surface.Surface = load_alpha("data/assets/table.png")
        self.sfx_on: pygame.surface.Surface = load_alpha("data/assets/sfx_on.png")
        self.sfx_off: pygame.surface.Surface = load_alpha("data/assets/sfx_off.png")
        self.button_image: pygame.surface.Surface = load_alpha("data/assets/button.png")
        self.button_hover_image: pygame.surface.Surface = load_alpha("data/assets/button_hover.png")
        self.credits_back_image: pygame.surface.Surface = resize_ratio(load_alpha("data/assets/credits-background.png"), (self.W, self.H))
        self.help_small_window: pygame.surface.Surface = resizex(load_alpha("data/assets/credits-background-no-burger.png"), 4)
        self.running: bool = True
        self.font_60: pygame.font.Font = pygame.font.Font("data/fonts/Minecraft.ttf", 60)
        self.font_50: pygame.font.Font = pygame.font.Font("data/fonts/Minecraft.ttf", 50)
        self.font_40: pygame.font.Font = pygame.font.Font("data/fonts/Minecraft.ttf", 40)
        self.font_30: pygame.font.Font = pygame.font.Font("data/fonts/Minecraft.ttf", 30)
        self.font_20: pygame.font.Font = pygame.font.Font("data/fonts/Minecraft.ttf", 20)
        self.font_10: pygame.font.Font = pygame.font.Font("data/fonts/Minecraft.ttf", 10)
        self.clock: pygame.time.Clock = clock
        self.credits: bool = False
        self.run_help: bool = False
        self.clicked_first_button: bool = False
        self.last_time: float = time.time()
        self.fps: int = self.settings["FPS"]
        self.dt: float = 1.0
        self.fake_players: list = [_FakePlayer(0 + -100*i, random.randint(270, 370), 10, self.settings) for i in range(7)]

        # -------------------------- BUTTONS ---------------------------- #

        self.buttons: ratatouille.FrameWork = ratatouille.init(self.screen)
        self.buttons.new_special_button((self.W // 2 - 100 // 2, self.H // 2 - 50 // 2 + 80), self.button_image, self.button_hover_image, (100, 40), self.stop_running)  # play
        self.buttons.new_special_button((self.W // 2 - 110 // 2, self.H // 2 - 50 // 2 + 125), self.button_image, self.button_hover_image, (110, 40), self.toggle_help)  # help
        self.buttons.new_special_button((self.W // 2 - 140 // 2, self.H // 2 - 50 // 2 + 170), self.button_image, self.button_hover_image, (140, 40), self.switch_credits)  # credits
        self.buttons.new_special_button((self.W // 2 - 100 // 2, self.H // 2 - 50 // 2 + 215), self.button_image, self.button_hover_image, (100, 40),  self.__quit__)  # quit

        self.credits_back: ratatouille.SpecialButton = ratatouille.SpecialButton((self.W//2 - 100//2, 350), self.button_image, self.button_hover_image, (100, 40), self.switch_credits)
        self.start_menu: ratatouille.SpecialButton = ratatouille.SpecialButton((self.W // 2 - 170 // 2, self.H // 2 - 50 // 2 + 80), self.button_image, self.button_hover_image, (170, 40), self.toggle_clicked_first_button)

        self.sound_buttons: ratatouille.FrameWork = ratatouille.init(self.screen)
        self.sound_buttons.new_special_button((self.W - 35, 5), self.music_on if self.settings["play_music"] else self.music_off, self.music_on if self.settings["play_music"] else self.music_off, (32, 32), self.toggle_sounds)
        self.sound_buttons.new_special_button((self.W - 67, 4), self.sfx_on if self.settings["play_sfx"] else self.sfx_off, self.sfx_on if self.settings["play_sfx"] else self.sfx_off, (32, 32), self.toggle_sfx)

    def toggle_clicked_first_button(self):
        self.clicked_first_button = not self.clicked_first_button

    def toggle_help(self):
        self.run_help = not self.run_help

    def help(self):
        index = 0
        
        buttons: ratatouille.FrameWork = ratatouille.init(self.screen)
        buttons.new_special_button((self.W//2 - 100//2, self.H - 130), self.button_image, self.button_hover_image, (100, 40), self.toggle_help)
        buttons.new_special_button((self.W//2 - 100//2 - 50, self.H - 130), self.button_image, self.button_hover_image, (40, 40))
        buttons.new_special_button((self.W//2 + 100//2 + 10, self.H - 130), self.button_image, self.button_hover_image, (40, 40))

        arrow_images = resizex(load_alpha(f"data/assets/arrows/arrow.png"), 2)
        walk_down = [load_alpha(f"data/assets/walk_down/walk_down{i+1}.png") for i in range(8)]
        walk_up = [load_alpha(f"data/assets/walk_up/walk_up{i+1}.png") for i in range(8)]
        walk_left = [load_alpha(f"data/assets/walk_left/walk_left{i+1}.png") for i in range(8)]
        walk_right = [pygame.transform.flip(image, True, False) for image in walk_left]
        images = [*walk_down, *walk_left, *walk_up, *walk_right]
        animation_walk_showcase: animation.Animation = animation.Animation(self.W//2 - 16, 200, images, 3)
        while self.run_help:
            self.clock.tick(self.fps)

            self.dt = time.time() - self.last_time
            self.dt *= self.fps
            self.last_time = time.time()

            self.screen.fill((255, 100, 50))
            for x in range(26):
                for y in range(25):
                    self.screen.blit(self.table, (x*32, y*28))

            for fake_player in self.fake_players:
                fake_player.move(self.dt)
                fake_player.animate()
                fake_player.update(self.screen)

            self.screen.blit(self.credits_back_image, (0, 0))
            self.screen.blit(self.help_small_window, (self.W//2 - self.help_small_window.get_width()//2,self.H//2 - self.help_small_window.get_height()//2 - 30))

            if   animation_walk_showcase.current_image in walk_down:
                self.screen.blit(arrow_images, (325, 190))
            elif animation_walk_showcase.current_image in walk_right:
                self.screen.blit(pygame.transform.rotate(arrow_images, 90), (325, 190))
            elif animation_walk_showcase.current_image in walk_up:
                self.screen.blit(pygame.transform.rotate(arrow_images, 180), (325, 190))
            elif animation_walk_showcase.current_image in walk_left:
                self.screen.blit(pygame.transform.rotate(arrow_images, 270), (325, 190))

            animation_walk_showcase.animate()
            animation_walk_showcase.update(self.screen)
            buttons.update()
            label = self.font_30.render("back", True, (0, 0, 0))
            self.screen.blit(label, (self.W//2 - label.get_width()//2, self.H - 130 + 40//2 - label.get_height()//2))

            label = self.font_40.render("moving", True, (0, 0, 0))
            self.screen.blit(label, (self.W//2 - label.get_width()//2, 160))

            blit_multiple_lines(217, 250, wrap_multi_lines("move the player with the arrow buttons", self.font_20, 230, True),
                                self.screen, self.font_20, centered_x=True, centered_x_pos=self.W//2)

            pygame.display.update()

            for event in pygame.event.get():
                buttons.handle_events(event)
                if event.type == pygame.QUIT:
                    self.__quit__()

    def __quit__(self):
        write_json("src/settings", self.settings)
        pygame.quit()
        quit(-1)

    def toggle_sounds(self):
        self.settings["play_music"]: bool = not self.settings["play_music"]
        if self.settings["play_music"]:
            self.sound_buttons.buttons[0].image = pg.transform.smoothscale(self.music_on, (32, 32))
            self.sound_buttons.buttons[0].image_hover = pg.transform.smoothscale(self.music_on, (32, 32))
        else:
            self.sound_buttons.buttons[0].image = pg.transform.smoothscale(self.music_off, (32, 32))
            self.sound_buttons.buttons[0].image_hover = pg.transform.smoothscale(self.music_off, (32, 32))

    def toggle_sfx(self):
        self.settings["play_sfx"]: bool = not self.settings["play_sfx"]
        if self.settings["play_sfx"]:
            self.sound_buttons.buttons[1].image = pg.transform.smoothscale(self.sfx_on, (32, 32))
            self.sound_buttons.buttons[1].image_hover = pg.transform.smoothscale(self.sfx_on, (32, 32))
        else:
            self.sound_buttons.buttons[1].image = pg.transform.smoothscale(self.sfx_off, (32, 32))
            self.sound_buttons.buttons[1].image_hover = pg.transform.smoothscale(self.sfx_off, (32, 32))

    def stop_running(self):
        self.running = False

    def switch_credits(self):
        self.credits = not self.credits

    def draw(self):
        self.screen.fill((255, 100, 50))
        for x in range(26):
            for y in range(25):
                self.screen.blit(self.table, (x*32, y*28))

        for fake_player in self.fake_players:
            fake_player.move(self.dt)
            fake_player.animate()
            fake_player.update(self.screen)

        self.screen.blit(self.logo, (self.W//2 - self.logo.get_width()//2, (20 + math.sin(time.time() * 5) * 5 - 25)*self.dt))
        self.sound_buttons.update()

        if self.clicked_first_button:

            if self.credits:
                self.screen.blit(self.credits_back_image, (0, 0))

                self.credits_back.update(self.screen)
                label = self.font_30.render("back", True, (0, 0, 0))
                self.screen.blit(label, (self.W//2 - label.get_width()//2, self.credits_back.rect[1] + self.credits_back.rect[3]//2 - label.get_height()//2))

                height = self.font_30.get_height()
                for i, text in enumerate(self.settings["credits"]):
                    rendered_text_surface = self.font_30.render(text, True, (0, 0, 0))
                    self.screen.blit(rendered_text_surface, (self.W / 2 - rendered_text_surface.get_width() / 2, 50 + (380 - height * len(self.settings["credits"])) / 2 + (i * height)))

            else:
                self.buttons.update()

                label = self.font_30.render("play", True, (0, 0, 0)); _rect = label.get_rect(center=self.buttons.buttons[0].rect.center)
                self.screen.blit(label, _rect)

                label = self.font_30.render("help", True, (0, 0, 0)); _rect = label.get_rect(center=self.buttons.buttons[1].rect.center)
                self.screen.blit(label, _rect)

                label = self.font_30.render("credits", True, (0, 0, 0)); _rect = label.get_rect(center=self.buttons.buttons[2].rect.center)
                self.screen.blit(label, _rect)

                label = self.font_30.render("quit", True, (0, 0, 0)); _rect = label.get_rect(center=self.buttons.buttons[3].rect.center)
                self.screen.blit(label, _rect)

        else:
            self.start_menu.update(self.screen)
            label = self.font_30.render("click to eat", True, (0, 0, 0))
            self.screen.blit(label, (self.W // 2 - label.get_width() // 2, self.H // 2 - label.get_height() // 2 + 75))

        pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():

            if self.clicked_first_button:
                if self.credits:  # check if the credits are drawn

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.credits_back.handle_click(event.pos)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.switch_credits()
                else:
                    self.buttons.handle_events(event)

            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.start_menu.handle_click(event.pos)

            self.sound_buttons.handle_events(event)
            if event.type == pygame.QUIT:
                self.__quit__()
 
    def run(self, fps):
        self.fps = fps
        self.running = True
        self.last_time = time.time()
        while self.running:
            self.clock.tick(self.fps)

            self.dt = time.time() - self.last_time
            self.dt *= self.fps
            self.last_time = time.time()

            if self.run_help:
                self.help()

            self.draw()
            self.event_handler()
        write_json("src/settings", self.settings)


class _FakePlayer:
    def __init__(self, x: int, y: int, vel: int, settings: dict):
        self.x = x
        self.y = y
        self.walking_right_animation = cycle(
            [
                pg.transform.scale2x(
                        load_alpha(
                            f"data/assets/walk_right/{file}"
                                    )
                ) for file in os.listdir("data/assets/walk_right")
            ]
        )
        self.vel = vel
        self.jump_count = 10
        self.is_jumping = False
        self.frames_per_image = 2
        self.time = 0
        self.settings = settings
        for _ in range(random.randint(1, 15)):
            self.current_image = next(self.walking_right_animation)

    def move(self, dt):
        if self.x >= 0:
            if self.is_jumping:
                if self.jump_count >= -10:
                    self.y -= ((self.jump_count * abs(self.jump_count)) / 2)*dt
                    self.jump_count -= 1
                else:
                    self.jump_count = 10
                    self.is_jumping = False

        if random.randint(0, 1000) > 900 and not self.is_jumping:
            self.is_jumping = True

        self.x += self.vel*dt
        if self.x >= self.settings["WIDTH"] + 50:
            self.x = 0

    def animate(self):
        if self.time >= self.frames_per_image:
            self.time = 0
            self.current_image = next(self.walking_right_animation)
        self.time += 1

    def update(self, screen: pygame.surface.Surface):
        if self.x >= -50:
            screen.blit(self.current_image, (self.x, self.y))
