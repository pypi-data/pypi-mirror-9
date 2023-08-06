import sys
sys.path.append('/usr/lib/python2.7/dist-packages')
import pygame
import pygame.locals

clock = pygame.time.Clock()

WIDTH = 300
HEIGHT = 100

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Alien Tower')

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((240, 240, 240))

base = background.copy()

class Player(object):
    MAX_JUMP = 80
    def __init__(self, pos_x, pos_y, base):
        self.viz = pygame.Surface((20, 20))
        self.viz = self.viz.convert()
        self.viz.fill((0,0,0))
        self.pos = self.viz.get_rect()
        self.pos.x = pos_x
        self.pos.y = pos_y
        self.blank = base
        self.moving = 0

    def draw_on(self, surface):
        surface.blit(self.blank, self.blank.get_rect())
        surface.blit(self.viz, self.pos)

    def move_left_on(self, surface):
        self.pos.x -= 1
        self.draw_on(surface)

    def move_right_on(self, surface):
        self.pos.x += 1
        self.draw_on(surface)

    def move_up_on(self, surface):
        self.pos.y -= 1
        self.draw_on(surface)

    def move_down_on(self, surface):
        self.pos.y += 1
        self.draw_on(surface)

player = Player(140, 80, base)

player.draw_on(background)
screen.blit(background, (0,0))
pygame.display.flip()


NOWHERE = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4

import diesel

def game_main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                raise SystemExit(0)
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_LEFT:
                    player.moving = LEFT
                elif event.key == pygame.locals.K_RIGHT:
                    player.moving = RIGHT
                elif event.key == pygame.locals.K_UP:
                    player.moving = UP
                elif event.key == pygame.locals.K_DOWN:
                    player.moving = DOWN
            elif event.type == pygame.locals.KEYUP:
                player.moving = NOWHERE

        if player.moving == LEFT:
            player.move_left_on(background)
            diesel.fire('direction', ('left (%d)' % player.pos.x))
        elif player.moving == RIGHT:
            player.move_right_on(background)
            diesel.fire('direction', ('right (%d)' % player.pos.x))
        elif player.moving == UP:
            player.move_up_on(background)
            diesel.fire('direction', ('up (%d)' % player.pos.y))
        elif player.moving == DOWN:
            player.move_down_on(background)
            diesel.fire('direction', ('down (%d)' % player.pos.y))

        if player.moving:
            screen.blit(background, (0,0))
            pygame.display.flip()
        diesel.sleep(0.015)

def server(addr):
    while True:
        direction = diesel.wait('direction')
        diesel.send(direction + '\r\n')
diesel.quickstart(game_main, diesel.Service(server, 4433))
