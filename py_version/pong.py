"""
Pong game in python, using pygame
original code taken from: https://codereview.stackexchange.com/questions/33289/basic-pong-game-in-pygame
adapted for two-player game with pihut gamepads (keyboard handling commented out)

Details:
    - (0,0) in upper left corner, x increases rightwards, y increases downwards
    - items marked as 'not important' are in regards to adapting for CM matrix

PiHut Gamepad keys w/ pygame:
    - Directions cross:
        * pygame.JOYAXISMOTION
        * Pressing button:
            * Up and Down:
                - event.axis = 1
                * Up: event.value = -1.0000305...
                * Down: event.value = 1.0
            * Left and Right:
                - event.axis = 0
                * Left: event.value = -1.0000305...
                * Right: event.value = 1.0
        * Releasing button:
            - event.value = 0
            - event.axis remains as above
    - Buttons:
        * Pressing: pygame.JOYBUTTONDOWN
        * Releasing: pygame.JOYBUTTONUP
        - X: event.button = 0
        - A: event.button = 1
        - B: event.button = 2
        - Y: event.button = 3
        - L: event.button = 4
        - R: event.button = 5
        - Select: event.button = 8
        - Start: event.button = 9
    (nobody knows what happened to 6 and 7...)
"""


import pygame
import serial
import sys
from random import randint

from ClubMateMapper import ClubMateMapper, HORIZONTAL_2x5, CRATE_VERTICAL


class Ball(object):
    def __init__(self, x, y, width, height, x_change, y_change, colour):
        self.x = x
        self.y = y
        self.width = width                      # not important
        self.height = height                    # not important
        self.x_change = x_change
        self.y_change = y_change
        self.speed = 1
        self.colour = colour

    def render(self, screen):                   # not important
        pygame.draw.ellipse(screen, self.colour, self.rect)

    def accelerate(self):
        return
        if self.speed < 3:
            self.speed += 0.2

    def update(self):
        self.x += self.x_change * self.speed
        self.y += self.y_change * self.speed

    @property
    def rect(self):                             # not important
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def next_pos_rect(self):
        x = self.x + self.x_change * self.speed
        y = self.y + self.y_change * self.speed
        return pygame.Rect(x, y, self.width, self.height)


class Paddle(object):
    def __init__(self, x, y, width, height, speed, screen_height, colour, game):
        self.x = x
        self.y = y
        self.width = width                      # not important
        self.height = height
        self.y_change = 0
        self.speed = speed
        self.screen_height = screen_height
        self.colour = colour                    # not important
        self.game = game

    def render(self, screen):                   # not important
        pygame.draw.rect(screen, self.colour, self.rect)

    def update(self):
        if self.y < 0:
            self.y = 0
        elif (self.y + self.height) > self.screen_height:
            self.y = self.screen_height - self.height
        else:
            self.y += self.y_change

    def key_handler(self, event):               # to be changed
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:  # RIGHT/LEFT
                pass
            elif event.axis == 1:  # UP/DOWN
                if event.value <= -1 and self.y > 0:                                      # UP
                    self.y_change = -self.speed
                elif event.value >= 1 and (self.y + self.height) < self.screen_height:    # DOWN
                    self.y_change = self.speed
                else:
                    self.y_change = 0
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button < 4:  # color button
                buttons = [(0, 0, 255), (255, 0, 0), (255, 255, 0), (0, 255, 0)]
                self.colour = buttons[event.button]
            elif event.button < 6:  # L & R
                self.colour = (0, 0, 0)
            elif event.button == 8:  # select
                start()
            elif event.button == 9:  # start
                self.game.pause(event.joy)

        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_UP and self.y > 0:
        #         self.y_change = -self.speed
        #     elif event.key == pygame.K_DOWN and (self.y + self.height) < self.screen_height:
        #         self.y_change = self.speed
        # elif event.key in (pygame.K_UP, pygame.K_DOWN):
        #     self.y_change = 0

    @property
    def rect(self):                             # not important
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Pong(object):
    COLOURS = {"BLACK":   (0,   0,   0),
               "WHITE": (255, 255, 255), }

    def __init__(self, external_output=None):
        self.mate_mapper = ClubMateMapper(HORIZONTAL_2x5, CRATE_VERTICAL)

        if external_output is None:
            self.external_output = open("/dev/null", "wb")
        else:
            self.external_output = external_output

        pygame.init()
        for _ in range(pygame.joystick.get_count()):
            pygame.joystick.Joystick(_).init()
        WIDTH, HEIGHT = 20, 10
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # not important
        pygame.display.set_caption("Lewis' Adapted Pong")       # not important
        self.clock = pygame.time.Clock()
        ball_x = randint(9, 10)
        ball_y = randint(4, 5)
        self.ball = Ball(ball_x, ball_y, 1, 1, 1, 1, Pong.COLOURS["BLACK"])
        self.player1 = Paddle(1, HEIGHT/2 - 1,  1, 10, 1, HEIGHT,
                              Pong.COLOURS["BLACK"], self)
        self.player2 = Paddle(WIDTH - 2, HEIGHT/2 - 1,  1, 10, 1, HEIGHT,
                              Pong.COLOURS["BLACK"], self)

    def pause(self, pauser):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 9 and pauser == event.joy:
                            self.play()
                    elif event.joy == 0:
                        self.player1.key_handler(event)
                    elif event.joy == 1:
                        self.player2.key_handler(event)
            self.player1.update()
            self.player1.render(self.screen)
            self.player2.update()
            self.player2.render(self.screen)
            pygame.display.update()
            clock.tick(15)

    def play(self):
        pygame.time.set_timer(1, 5000)
        while True:
            self.clock.tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN):
                    if event.joy == 0:
                        self.player1.key_handler(event)

                        # SOLO MODE
                        # if event.type == pygame.JOYBUTTONDOWN and event.button == 9:
                        #     pass  # avoid triggering double pause if I controll both paddles
                        # else:
                        #     self.player2.key_handler(event)

                    elif event.joy == 1:
                        self.player2.key_handler(event)
                # if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                #    self.player1.key_handler(event)
                #    self.player2.key_handler(event)
                if event.type == 1:
                    self.ball.accelerate()
            self.collision_handler()
            self.draw()

            frame = [
                [
                    self.screen.get_at((x, y)) == (0, 0, 0, 255) and 1 or 0
                    for x in range(20)
                ] for y in range(10)
            ]
            self.external_output.write(
                self.mate_mapper.magic_func(frame)
            )



    def collision_handler(self):
        if self.ball.y + self.ball.height >= self.screen.get_height():
            self.ball.y_change = -abs(self.ball.y_change)
        elif self.ball.y <= 0:
            self.ball.y_change = abs(self.ball.y_change)

        if self.ball.next_pos_rect.colliderect(self.player1.rect):
            self.ball.x_change = -self.ball.x_change
        elif self.ball.next_pos_rect.colliderect(self.player2.rect):
            self.ball.x_change = -self.ball.x_change

        if self.ball.x + self.ball.width >= self.screen.get_width():
            pygame.quit()
            sys.exit()
        elif self.ball.x <= 0:
            pygame.quit()
            sys.exit()

    def draw(self):
        self.screen.fill(Pong.COLOURS["WHITE"])         # not important
        self.ball.update()
        self.ball.render(self.screen)
        self.player1.update()
        self.player1.render(self.screen)
        self.player2.update()
        self.player2.render(self.screen)
        pygame.display.update()


def start():
    arduino = serial.Serial(port='/dev/ttyUSB1', baudrate=115200)
    arduino.write(bytes([0]) * 25)
    Pong(external_output=arduino).play()
    arduino.close()


if __name__ == "__main__":
    start()
