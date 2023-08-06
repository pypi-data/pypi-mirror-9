#!/Users/HaleyoBourke/Applications/MacPython 2.5
import pygame
import sys
import random
import collections
import AsteroidBelt
import Bullet
import math
import Asteroid
from pygame.locals import *
from array import array
pygame.init()
bulletImage = pygame.transform.smoothscale(pygame.image.load('bullet.png'), (9, 10))
WHITE = (255, 255, 255)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position):
        self.image = bulletImage
        self.xCord = position[0]
        self.yCord = position[1]
        self.direction = 0
        self.rect = self.image.get_rect()
        self.enabled = True
        
    def fire(self, direction):
        self.direction = direction

    def updateLocation(self):
        self.xCord += math.cos(math.radians(-self.direction)) * 7
        self.yCord += math.sin(math.radians(-self.direction)) * 7

    #def applyKleinPhysics(self):
        #if(self.xCord >= 800 or self.xCord < 5):
            #if(self.xCord >= 800):
                #if(self.direction > 0 and self.direction < 90):
                    #self.direction = 360 - self.direction
                #elif(self.direction > 270 and self.direction < 360):
                    #self.direction = (360 - self.direction)
                #self.xCord = 5
                #self.image = pygame.transform.rotate(bulletImage, self.direction % 360)
            #elif(self.xCord < 5):
                #if(self.direction < 180 and self.direction > 90):
                    #self.direction = 180 + (180 - self.direction)
                #elif(self.direction > 180 and self.direction < 270):
                    #self.direction = 180 - (270 - self.direction)
                #self.xCord = 799
                #self.image = pygame.transform.rotate(bulletImage, self.direction % 360)
            #if(self.yCord > 250):
                #self.yCord = 250 - (self.yCord - 250)
            #elif(self.yCord < 250):
                #self.yCord = 250 + (250 - self.yCord)
        #elif(self.yCord <= 3):
            #self.yCord = 500
        #elif(self.yCord > 500):
            #self.yCord = 4


