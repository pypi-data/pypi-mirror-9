#!/Users/HaleyoBourke/Applications/MacPython 2.5
import pygame
import sys
import random
import math
import collections
import AsteroidBelt
import spaceship
import Asteroid
import Menu
from pygame.locals import *
from array import array
pygame.init()
FPS = 30
fpsClock = pygame.time.Clock()
screenInfo = pygame.display.Info()
DISPLAYSURF = pygame.display.set_mode((screenInfo.current_w, screenInfo.current_h))
#DISPLAYSURF = pygame.display.set_mode((1000, 750))
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0,128,0)
menu = Menu.Menu(DISPLAYSURF)
asteroidBelt = AsteroidBelt.AsteroidBelt(DISPLAYSURF)
spaceShip = spaceship.SpaceShip(DISPLAYSURF)

pygame.display.set_caption('Klein Bottle Space Fighter')
while True:
    if(spaceShip.destroyed):
        menu.gameOver(DISPLAYSURF, spaceShip, asteroidBelt)
    else:
        DISPLAYSURF.fill(BLACK)
        spaceShip.updateLocation()
        if(len(spaceShip.bullets) != 0):
            for x in range(0, len(spaceShip.bullets)):
                spaceShip.bullets[x].updateLocation()
                spaceShip.bullets[x].rect = DISPLAYSURF.blit(spaceShip.bullets[x].image, (spaceShip.bullets[x].xCord, spaceShip.bullets[x].yCord))
        keys = pygame.key.get_pressed()
        #if keys[pygame.K_SPACE]:
            #spaceShip.fireBullet()
        if keys[pygame.K_UP]:
            spaceShip.moveUp()
        if keys[pygame.K_RIGHT]:
            spaceShip.moveRight(DISPLAYSURF)
        if keys[pygame.K_LEFT]:
            spaceShip.moveLeft(DISPLAYSURF)
        if(spaceShip.xCord >= (DISPLAYSURF.get_width()) or spaceShip.xCord < 5 or spaceShip.yCord <= 5 or spaceShip.yCord >= (DISPLAYSURF.get_height() - 5)):
            spaceShip.applyKleinPhysics(DISPLAYSURF)
        spaceShip.rect = DISPLAYSURF.blit(spaceShip.image, (spaceShip.xCord, spaceShip.yCord))
        spaceShip.center = spaceShip.rect.center
        asteroidBelt.animateAsteroids(DISPLAYSURF, spaceShip)
    for event in pygame.event.get():
        if(event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            spaceShip.fireBullet()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    if(spaceShip.speed > 0):
        spaceShip.speed -= .00000000001
fpsClock.tick(FPS)



