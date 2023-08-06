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
spaceShipImage = pygame.image.load('rocket.png')
spaceShipScaled = None

class SpaceShip(object):
    def __init__(self, DISPLAYSURF):
        self.image = pygame.transform.smoothscale(spaceShipImage, (int(DISPLAYSURF.get_width() * 0.13), int(DISPLAYSURF.get_height() * 0.1)))
        spaceShipScaled = self.image
        self.direction = 'N'
        self.xCord = int(DISPLAYSURF.get_width() * 0.4375)
        self.yCord = int(DISPLAYSURF.get_height() * 0.5)
        self.speed = 0
        self.rotation = 0
        self.center = None
        self.rect = None
        self.bullets = []
        self.destroyed = False

    def moveLeft(self, DISPLAYSURF):
        self.rotation += 2
        self.image = self.rotateSpaceShip(DISPLAYSURF)
        self.updateLocation()
        self.direction = 'L'

    def moveRight(self, DISPLAYSURF):
        self.rotation -= 2
        self.image = self.rotateSpaceShip(DISPLAYSURF)
        self.updateLocation()
        self.direction = 'R'

    def moveUp(self):
        self.speed = 4
        self.xCord += math.cos(math.radians(-self.rotation)) * self.speed
        self.yCord += math.sin(math.radians(-self.rotation)) * self.speed
        self.direction = 'U'

    def applyKleinPhysics(self, DISPLAYSURF):
        if(self.rotation > 359):
            self.rotation = self.rotation % 360
        elif(self.rotation < 0):
            self.rotation = (360 + self.rotation) % 360
            
        spaceShipScaled = pygame.transform.smoothscale(spaceShipImage, (int(DISPLAYSURF.get_width() * .13), int(DISPLAYSURF.get_height() * 0.1)))
        if(self.xCord >= DISPLAYSURF.get_width() or self.xCord < 5):
            if(self.xCord >= DISPLAYSURF.get_width()):
                if(self.rotation > 0 and self.rotation < 90):
                    self.rotation = (360 - self.rotation) % 360
                elif(self.rotation > 270 and self.rotation < 360):
                    self.rotation = (360 - self.rotation) % 360
                self.xCord = 5
                self.image = pygame.transform.rotate(spaceShipScaled, self.rotation % 360)
            elif(self.xCord < 5):
                if(self.rotation < 180 and self.rotation > 90):
                    self.rotation = (180 + (180 - self.rotation)) % 360
                elif(self.rotation > 180 and self.rotation < 270):
                    self.rotation = (180 - (270 - self.rotation)) % 360
                self.xCord = DISPLAYSURF.get_width() - 1
                self.image = pygame.transform.rotate(spaceShipScaled, self.rotation % 360)
            if(self.yCord > int(DISPLAYSURF.get_height() * 0.417)):
                    self.yCord = int(DISPLAYSURF.get_height() * 0.417) - (self.yCord - int(DISPLAYSURF.get_height() * 0.417))
            elif(self.yCord < int(DISPLAYSURF.get_height() * 0.417)):
                self.yCord = int(DISPLAYSURF.get_height() * 0.417)+ (int(DISPLAYSURF.get_height() * 0.417) - self.yCord)
        elif(self.yCord <= 3):
            self.yCord = DISPLAYSURF.get_height() - 5
        elif(self.yCord > DISPLAYSURF.get_height()):
            self.yCord = 4

    def rotateSpaceShip(self, DISPLAYSURF):
        spaceShipScaled = pygame.transform.smoothscale(spaceShipImage, (int(DISPLAYSURF.get_width() * .13), int(DISPLAYSURF.get_height() * 0.1)))
        rotatedImage = pygame.transform.rotate(spaceShipScaled, self.rotation % 360)
        rotatedRect = rotatedImage.get_rect()
        rotatedRect.center = self.center
        #self.rect = rotatedRect
        self.xCord = rotatedRect.x
        self.yCord = rotatedRect.y
        return rotatedImage

    def updateLocation(self):
        self.xCord += math.cos(math.radians(-self.rotation)) * self.speed
        self.yCord += math.sin(math.radians(-self.rotation)) * self.speed

    def fireBullet(self):
        bullet = Bullet.Bullet(self.rect.center)
        bullet.fire(self.rotation)
        self.bullets.append(bullet)

    def explode(self):
        self.destroyed = True
        #self.image = pygame.image.load('explosion.png')


