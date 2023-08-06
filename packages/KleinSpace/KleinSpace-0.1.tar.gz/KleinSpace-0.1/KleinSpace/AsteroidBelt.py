import pygame
import sys
import random
import math
import spaceship
import Asteroid
import collections
from pygame.locals import *
pygame.init()

class AsteroidBelt(object):
    def __init__(self, DISPLAYSURF):
        self.arrayOfAsteroids = []
        self.initializeAsteroidBelt(DISPLAYSURF)

    def initializeAsteroidBelt(self, DISPLAYSURF):
        self.arrayOfAsteroids = []
        self.arrayOfAsteroids.append(Asteroid.Asteroid('asteroid1.png', DISPLAYSURF))
        self.arrayOfAsteroids.append(Asteroid.Asteroid('asteroid2.png', DISPLAYSURF))
        self.arrayOfAsteroids.append(Asteroid.Asteroid('asteroid3.png', DISPLAYSURF))
        self.arrayOfAsteroids.append(Asteroid.Asteroid('asteroid4.png', DISPLAYSURF))
        self.arrayOfAsteroids.append(Asteroid.Asteroid('asteroid5.png', DISPLAYSURF))
        self.arrayOfAsteroids.append(Asteroid.Asteroid('asteroid6.png', DISPLAYSURF))

    def animateAsteroids(self, DISPLAYSURF, spaceShip):
        for x in range (0, len(self.arrayOfAsteroids)):
            if(self.arrayOfAsteroids[x].enabled or self.arrayOfAsteroids[x].exploding == True):
                if(len(spaceShip.bullets) > 0):
                    for bulletIndex in range(0, len(spaceShip.bullets)):
                        if(spaceShip.bullets[bulletIndex].enabled):
                            if(pygame.sprite.collide_rect(spaceShip.bullets[bulletIndex], self.arrayOfAsteroids[x])):
                                self.arrayOfAsteroids[x].explode()
                                spaceShip.bullets[bulletIndex].enabled = False
                self.arrayOfAsteroids[x].move(DISPLAYSURF)
                self.arrayOfAsteroids[x].rect = DISPLAYSURF.blit(self.arrayOfAsteroids[x].image, (self.arrayOfAsteroids[x].xCord,self.arrayOfAsteroids[x].yCord))
                if(spaceShip.rect):
                    if(pygame.sprite.collide_rect(self.arrayOfAsteroids[x], spaceShip)):
                        self.arrayOfAsteroids[x].explode()
                        spaceShip.explode()
                if(self.arrayOfAsteroids[x].exploding == True):
                    self.arrayOfAsteroids[x].endExplosionSequence(DISPLAYSURF)

