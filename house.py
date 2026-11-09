import pygame
from settings import *

class House:
    def __init__(self, number):
        self.number = number

        #Set the house to three screens wide
        self.worldWidth = SCREEN_WIDTH * 3

        #House overall height fits in screen
        self.groundY = SCREEN_HEIGHT - 8

        #Creating the outerboundaries
        self.walls = [
            pygame.Rect(0, 0, self.worldWidth, 8),
            pygame.Rect(0, self.groundY, self.worldWidth, 8),
            pygame.Rect(0, 0, 8, SCREEN_HEIGHT),
            pygame.Rect(self.worldWidth - 8, 0, 8, SCREEN_HEIGHT),
        ] 

        self.roomDivisions = [   
            pygame.Rect(SCREEN_WIDTH, 8, 4, self.groundY - 53),
            pygame.Rect(SCREEN_WIDTH * 2, 8, 4, self.groundY - 53)
        ]

        #Furniture will be spread throughout the house
        self.furniture = [
            pygame.Rect(110, self.groundY - 18, 56, 18),                    #Low table
            pygame.Rect(250, self.groundY - 30, 34, 30),                    #Cabinet
            
            pygame.Rect(SCREEN_WIDTH + 70, self.groundY - 22, 58, 22),      #Table
            pygame.Rect(SCREEN_WIDTH + 200, self.groundY - 36, 40, 36),      #Dresser

            pygame.Rect(SCREEN_WIDTH * 2 + 65, self.groundY - 20, 52, 20),
            pygame.Rect(SCREEN_WIDTH * 2 + 200, self.groundY - 32, 38, 32)
        ]

        #Shelves are made separately to be put on the wall
        self.shelves = [
            pygame.Rect(65, 95, 42, 6),
            pygame.Rect(SCREEN_WIDTH + 140, 82, 46, 6),
            pygame.Rect(SCREEN_WIDTH * 2 + 150, 70, 52, 6)
        ]

        #Solid objects (basically block movement in every direction)
        self.solidWalls = self.walls + self.roomDivisions

        #One way platforms (blocks crow when falling, used for the furniture)
        self.platforms = self.furniture + self.shelves

        #All colliders, used by residents and rocks
        self.colliders = self.solidWalls + self.platforms

        #Creating the hiding spots
        self.hidingSpots = [
            pygame.Rect(118, self.groundY - 14, 18, 10),
            pygame.Rect(SCREEN_WIDTH + 92, self.groundY - 17, 20, 12)
        ]

        #Exiting near the far-right end
        self.exitPlace = pygame.Rect(self.worldWidth - 34, self.groundY - 22, 22, 22)
        
        #Placing the crow on the left side
        self.crowStart = (25, self.groundY - 16)

        #Setting residents positions 
        residentPositions = [
            (240, self.groundY - 11), 
            (SCREEN_WIDTH + 200, self.groundY - 11),
            (SCREEN_WIDTH * 2 + 170, self.groundY -11)
        ]

        #Helper function for putting treasures on top of the furniture and shelves
        def onTop(platform, offsetX, name, value, noise):
            treasureWidth = 6
            treasureHeight = 6

            #Keep treasures within platform width
            x = platform.left + offsetX
            x = max(platform.left, min(x, platform.right - treasureWidth))

            #One pixel gap above the furniture
            y = platform.top - treasureHeight - 1

            return ((x, y), name, value, noise)
        

        #All the treasures positions throughout house
        allTreasures = [
            #Room 1
            onTop(self.furniture[0], 20, "Bottle cap", 2, 3),
            onTop(self.shelves[0], 16, "Shiny button", 3, 4),
            onTop(self.furniture[1], 12, "Golden ring", 8, 9),

            #Room 2
            onTop(self.furniture[2], 24, "Teaspoon", 4, 7),
            onTop(self.shelves[1], 18, "Key", 5, 7),
            onTop(self.furniture[3], 10, "Dog tag", 6, 8),

            onTop(self.furniture[4], 18, "Spoon", 4, 6),
            onTop(self.shelves[2], 22, "Pocket watch", 10, 10),
            onTop(self.furniture[5], 8, "Golden ring", 8, 9)
        ]

        #For house number 1 (subject to change)
        if number == 1:
            self.residentStarts = residentPositions[:1]
            self.residentSpeed = 17
            self.visionRadius = 60
            self.treasureData = allTreasures[:4]

        #For house number 2
        elif number == 2:
            self.residentStarts = residentPositions[:2]
            self.residentSpeed = 23
            self.visionRadius = 70
            self.treasureData = allTreasures[:6]
        
        #For the last house...
        else:
            self.residentStarts = residentPositions
            self.residentSpeed = 29
            self.visionRadius = 80
            self.treasureData = allTreasures

    def draw(self, surface):
        #Background wall
        pygame.draw.rect(surface, (49, 57, 65), (0, 0, self.worldWidth, self.groundY))

        #Windows in the house
        for x in range(70, self.worldWidth - 30, 180):
            pygame.draw.rect(surface, (100, 145, 165), (x, 30, 35, 28))
            pygame.draw.rect(surface, WALL_COLOR, (x, 30, 35, 28), 2)

        #Floor, ceiling, and outside walls
        for wall in self.walls[:4]:
            pygame.draw.rect(surface, WALL_COLOR, wall)

        for divider in self.roomDivisions:
            pygame.draw.rect(surface, WALL_COLOR, divider)
        
        #Furniture
        for rect in self.furniture:
            pygame.draw.rect(surface, FURNITURE_DARK, rect.inflate(2, 2))
            pygame.draw.rect(surface, FURNITURE_COLOR, rect)

        #Shelves
        for shelf in self.shelves:
            pygame.draw.rect(surface, (95, 70, 45), shelf)
            pygame.draw.rect(surface, (145, 110, 70), shelf, 1)

        #Hiding places
        for spot in self.hidingSpots:
            pygame.draw.rect(surface, (65, 76, 66), spot)
            pygame.draw.rect(surface, (95, 112, 85), spot, 1)

        #Exit 
        pygame.draw.rect(surface, (60, 115, 83), self.exitPlace)
        pygame.draw.rect(surface, (145, 205, 145), self.exitPlace, 1)
