import pygame
import sys
import random
import math
import collections
from pygame.locals import *
from array import array
pygame.init()
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0,128,0)
gameOverBackground = pygame.image.load('Game Over.png')
gameOverTextImage = pygame.image.load('Game Over Text.png')
gameOverTextImage.set_colorkey(BLACK)
playAgainTextImage = pygame.image.load('play again.png')
playAgainTextActivated = pygame.image.load('Play Again Activated.png')
playAgainTextImage.set_colorkey(BLACK)

class Menu(object):
    def __init__(self, DISPLAYSURF):
        self.screen = pygame.transform.smoothscale(gameOverBackground, (DISPLAYSURF.get_width(), DISPLAYSURF.get_width()))
        self.gameOverText = pygame.transform.smoothscale(gameOverTextImage, (int(DISPLAYSURF.get_width() * 0.875), int(DISPLAYSURF.get_height() * 0.242)))
        self.playAgainText = pygame.transform.smoothscale(playAgainTextImage, (int(DISPLAYSURF.get_width() * 0.375), int(DISPLAYSURF.get_height() * 0.162)))
    
    def gameOver(self, DISPLAYSURF, spaceShip, asteroidBelt):
        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(self.screen, self.screen.get_rect(center = DISPLAYSURF.get_rect().center))
        DISPLAYSURF.blit(self.gameOverText, self.gameOverText.get_rect(center = (DISPLAYSURF.get_rect().center[0], DISPLAYSURF.get_rect().center[1] - DISPLAYSURF.get_rect().center[1]/5)))
        DISPLAYSURF.blit(self.playAgainText, self.playAgainText.get_rect(center = (DISPLAYSURF.get_rect().center[0], DISPLAYSURF.get_rect().center[1] + DISPLAYSURF.get_rect().center[1]/5)))
        if(self.playAgainText.get_rect(center = (DISPLAYSURF.get_rect().center[0], DISPLAYSURF.get_rect().center[1] + DISPLAYSURF.get_rect().center[1]/5)).collidepoint(pygame.mouse.get_pos())):
            self.playAgainText = pygame.transform.smoothscale(playAgainTextActivated, (int(DISPLAYSURF.get_width() * 0.375), int(DISPLAYSURF.get_height() * 0.162)))
        else:
            self.playAgainText = pygame.transform.smoothscale(playAgainTextImage, (int(DISPLAYSURF.get_width() * 0.375), int(DISPLAYSURF.get_height() * 0.162)))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.playAgainText.get_rect(center = (DISPLAYSURF.get_rect().center[0], DISPLAYSURF.get_rect().center[1] + DISPLAYSURF.get_rect().center[1]/5)).collidepoint(pygame.mouse.get_pos()):
                spaceShip.destroyed = False
                spaceShip.speed = 0
                spaceShip.xCord = int(DISPLAYSURF.get_width() * 0.4375)
                spaceShip.yCord = int(DISPLAYSURF.get_height() * 0.5)
                asteroidBelt.initializeAsteroidBelt(DISPLAYSURF)

