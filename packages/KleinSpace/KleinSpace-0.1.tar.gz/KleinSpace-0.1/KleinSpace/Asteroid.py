import pygame
import sys
import random
import math
import collections
from pygame.locals import *
pygame.init()
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0,128,0)
#asteroidImage = pygame.transform.smoothscale(AsteroidImage, (100, 100))
explosionImageRaw = pygame.image.load('explosion.png')

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, imageName, DISPLAYSURF):
        xRange = []
        xRange.append(random.randint(0, int(DISPLAYSURF.get_width() * 0.25)))
        xRange.append(random.randint(int(DISPLAYSURF.get_width() * 0.75), DISPLAYSURF.get_width()))
        self.xCord = xRange[random.randint(0,1)]
        self.yCord = random.randint(0, DISPLAYSURF.get_height())
        self.rise = random.randint(1, 3)
        self.run = random.randint(1, 3)
        self.image = (pygame.transform.smoothscale(pygame.image.load(imageName), (int(DISPLAYSURF.get_width() * 0.12), int(DISPLAYSURF.get_width() * 0.12))))
        self.image.set_colorkey(BLACK)
        self.degrees = 1
        self.rect = self.image.get_rect()
        self.enabled = True
        self.exploding = False

    def move(self, DISPLAYSURF):
        if(self.xCord < (DISPLAYSURF.get_width() + self.run + 1) and self.xCord > (DISPLAYSURF.get_width() - self.run - 1)):
            self.xCord = 0
            self.rise = (-1) * self.rise
        if(self.yCord < 0):
            self.yCord = DISPLAYSURF.get_height()
        elif(self.yCord > DISPLAYSURF.get_height()):
            self.yCord = 0
        self.xCord = self.xCord + self.run
        self.yCord = self.yCord - self.rise

    def explode(self):
        self.image = pygame.transform.smoothscale(explosionImageRaw, (int(self.image.get_height()), int(self.image.get_height())))
        self.enabled = False
        self.exploding = True

    def endExplosionSequence(self, DISPLAYSURF):
        self.image = pygame.transform.smoothscale(explosionImageRaw, (int(self.image.get_height() * 1.5),int(self.image.get_height() * 1.5)))
        self.rect = DISPLAYSURF.blit(self.image, (self.xCord, self.yCord))
        self.exploding = False