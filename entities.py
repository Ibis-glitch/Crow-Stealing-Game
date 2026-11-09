import math
import pygame
from settings import *
from crow_sprite import CrowSprite

class ThrownRock:
    def __init__(self, x, y, targetX, targetY):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(round(x), round(y), 4, 4)

        self.gravity = 60
        self.alive = True
        self.age = 0

        #Aim toward the crow, allowing for gravity
        dx = targetX - x 
        dy = targetY - y
        distance = math.hypot(dx, dy)

        travelTime = max(0.15, distance / 150)

        self.velocityX = dx / travelTime
        self.velocityY = (dy - 0.5 * self.gravity * travelTime**2) / travelTime

    def update(self, dt, house):
        self.age += dt

        self.velocityY += self.gravity * dt

        self.x += self.velocityX * dt
        self.y += self.velocityY * dt

        self.rect.topleft = (round(self.x), round(self.y))

        #Remove rocks that leave the house
        if (self.age > 3 or self.x < 0 or self.x >= house.worldWidth or self.y < 0 or self.y >= SCREEN_HEIGHT):
            self.alive = False
            return

        #Rocks that hit the furniture, shelves, and walls
        for collider in house.colliders:
            if (self.rect.colliderect(collider)):
                self.alive = False
                return
    
    def draw(self, surface):
        pygame.draw.circle(surface, (190, 185, 170), self.rect.center, 2)

class Crow:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.speed = PLAYER_SPEED
        self.sprite = CrowSprite(width=30)
        self.previousDrawPos = self.rect.topleft
        self.suspicion = 0
        self.inventory = []
        self.hidden = False
        self.hide_spot = None
        self.facing = (1, 0)
        self.x = float(x)
        self.y = float(y)
        self.velocityY = 0
        self.wasJumpPressed = False

    def update(self, dt, keys, solidWalls, platforms):

        #Buttons for jumping
        jumpPressed = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]

        #If hidden
        if (self.hidden):
            self.wasJumpPressed = jumpPressed
            return

        #Horizontal movement
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        
        #If crow isn't on the ground
        if (dx != 0):
            self.facing = (dx, 0)

        #Jump or flap whenever key pressed again
        if (jumpPressed and not self.wasJumpPressed):
            self.velocityY = -JUMP_SPEED

        self.wasJumpPressed = jumpPressed

        #Sprinting or walking
        speed = (SPRINT_SPEED if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else PLAYER_SPEED)

        #Move horixontally
        self.x += dx * speed * dt
        self.rect.x = round(self.x)

        #Horizontal wall collisions (but not for furniture)
        for solidWall in solidWalls: 
            if (self.rect.colliderect(solidWall)):
                if (dx > 0):
                    self.rect.right = solidWall.left
                elif (dx < 0):
                    self.rect.left = solidWall.right

                self.x = float(self.rect.x)

        #Applying gravity
        self.velocityY += GRAVITY * dt

        #Limit the falling speed
        self.velocityY = min(self.velocityY, MAX_FALL_SPEED)

        #Remember crow's previous position
        oldTop = self.rect.top
        oldBottom = self.rect.bottom

        #Moving vertically
        self.y += self.velocityY * dt
        self.rect.y = round(self.y)

        #Finding surface crow may have crossed the frame
        if (self.velocityY > 0):

            #Crow is falling
            #Land on solid walls or platforms (aka on top of furniture)
            landingSurfaces = [
                platform.top for platform in solidWalls + platforms
                if self.rect.right > platform.left
                and self.rect.left < platform.right
                and oldBottom <= platform.top <= self.rect.bottom
            ]

            if (landingSurfaces):
                
                #Land on whatever the highest surface is
                self.rect.bottom = min(landingSurfaces)
                self.velocityY = 0

        elif (self.velocityY < 0):

            #Crow is flying upward
            #But crow won't hit top of furniture
            ceilings = [
                wall.bottom for wall in solidWalls
                if self.rect.right > wall.left
                and self.rect.left < wall.right
                and self.rect.top <= wall.bottom <= oldTop
            ]

            if (ceilings):

                #Stop the crow against the nearest ceiling
                self.rect.top = max(ceilings)
                self.velocityY = 0

        #Synchronize floating point position
        self.y = float(self.rect.y)

    def _move(self, dx, dy, walls):
        self.rect.x += round(dx)
        self.rect.y += round(dy)
        for wall in walls:
            if (self.rect.colliderect(wall)):
                if (dx > 0):
                    self.rect.right = wall.left
                elif (dx < 0):
                    self.rect.left = wall.right
                if (dy > 0):
                    self.rect.bottom = wall.top
                elif (dy < 0):
                    self.rect.top = wall.bottom

    def try_pickup(self, treasures):
        nearby = [item for item in treasures
        if not item.collected and self.rect.inflate(20, 20).colliderect(item.rect)]
        if not nearby:
            return None
        item = min(nearby, key=lambda obj:
                   (self.rect.centerx - obj.rect.centerx) ** 2 + (self.rect.centery - obj.rect.centery) ** 2)
        item.collected = True
        self.inventory.append(item)
        self.suspicion = min(100, self.suspicion + item.noise)
        return item

    def toggle_hide(self, hide_spots):
        if self.hidden:
            self.hidden = False
            self.hide_spot = None
            return
        for spot in hide_spots:
            if self.rect.inflate(10, 10).colliderect(spot):
                self.hidden = True
                self.hide_spot = spot
                self.rect.center = spot.center
                self.x = float(self.rect.x)
                self.y = float(self.rect.y)
                self.velocityY = 0
                return

    def draw(self, surface):
        if (self.hidden):
            pygame.draw.rect(surface, (35, 43, 47), self.rect.inflate(4, 4))
            self.previousDrawPos = self.rect.topleft
            return

        #Detect whether the crow moved
        isIdle = self.rect.topleft == self.previousDrawPos

        visualOffsetY = 3

        visualRect = self.rect.move(0, visualOffsetY)

        #Drawing the sprite
        self.sprite.draw(surface, visualRect, self.facing, idle=isIdle)

        #Remember position for next frame
        self.previousDrawPos = self.rect.topleft
        
class Grandma:
    def __init__(self, start, speed, visionRadius, canThrow=False):
        self.rect = pygame.Rect(start[0], start[1], 9, 11)

        #Original guarding position
        self.homeX = float(self.rect.x)
        self.homeCenterX = self.rect.centerx
        self.x = float(self.rect.x)

        #All mechanics used for chasing the crow
        self.speed = speed
        self.chaseSpeed = max(35, speed * 2)
        self.visionRadius = visionRadius

        #Guarding, chasing, returning states
        self.state = "guarding"

        #Direction: looking left or right
        self.direction = -1

        #Looking left or right every 2.5 seconds
        self.lookTimer = 0
        self.lookInterval = 2.5

        #Alerted, showing the exclamation mark
        self.alertTimer = 0

        #Chasing limits, when grandma gives up
        self.maxChaseDistance = 180
        self.maxDistanceFromHome = 200
        self.maxUnreachableHeight = 60

        #Delay for chasing
        self.highEscapeTimer = 0
        self.highEscapeDelay = 1.0

        #Ranged attack abilities for when crow too high
        #Exclusive to level three (will get updated later)
        self.canThrow = canThrow
        self.rocks = []
        self.throwTimer = 0
        self.throwDelay = 1.4
        self.throwRange = 115

    def crowTooHigh(self, crow):

        #Tracks how far the crow is above resident's head
        height = self.rect.top - crow.rect.bottom

        return height > self.maxUnreachableHeight

    #Checks whether or not the resident can see the crow
    def canSee(self, crow):

        #No crow, no detection
        if (crow.hidden):
            return False

        #Coordinates for the crow
        dx = crow.rect.centerx - self.rect.centerx
        dy = crow.rect.centery - self.rect.centery

        #Calculates distance between resident and crow
        distance = math.hypot(dx, dy)

        #Resident can't see the crow
        if (distance > self.visionRadius):
            return False
        
        #Resident can see the crow
        if (distance == 0):
            return True

        #90 degree field of vision
        angleLimit = math.cos(math.radians(45))

        return(dx * self.direction / distance >= angleLimit)
    
    #Function for resident actually giving chase to crow
    def moveTowards(self, targetX, speed, dt, house):
        #Direction to the target
        difference = targetX - self.rect.centerx

        #If you get caught, womp womp
        if (abs(difference) < 0.1):
            return

        #Basically what direction the resident is facing
        if (difference > 0):
            self.direction = 1

        else:
            self.direction = -1

        #The resident's movement to the crow
        movement = self.direction * min(speed * dt, abs(difference))

        #The x position getting adjusted by the movement
        #So just the resident moving
        self.x += movement
        self.rect.x = round(self.x)
    
    def update(self, dt, house, crow):
        self.throwTimer = max(0, self.throwTimer - dt)
        self.alertTimer = max(0, self.alertTimer - dt)

        #Updating the exisitng rocks
        for rock in self.rocks[:]:
            rock.update(dt, house)

            if (not rock.alive):
                self.rocks.remove(rock)

        #Spot the crow while guarding or returning
        if (self.state != "chasing"):
            if (self.canSee(crow)):
                if (self.canThrow or not self.crowTooHigh(crow)):
                    self.state = "chasing"
                    self.alertTimer = 1.0
                    self.throwTimer = 0.35

        #Guarding state
        if (self.state == "guarding"):
            self.lookTimer += dt

            if (self.lookTimer >= self.lookInterval):
                self.direction *= -1
                self.lookTimer = 0

            return

        #Chasing state
        if (self.state == "chasing"):
            distance = abs(crow.rect.centerx - self.rect.centerx)

            distanceFromHome = abs(self.rect.centerx - self.homeCenterX)

            tooHigh = self.crowTooHigh(crow)

            #Count how long the crow stays too high
            if (tooHigh):
                self.highEscapeTimer += dt

            else:
                self.highEscapeTimer = 0

            #Conditions that end a chase
            if (crow.hidden or distance > self.maxChaseDistance or distanceFromHome > self.maxDistanceFromHome):
                self.state = "returning"
                self.highEscapeTimer = 0

            #Crow is too high for the resident to reach
            elif (tooHigh and self.canThrow and distance <= self.throwRange):

                #Stop chasing the crow and attempt to throw rock at crow
                #Changing directions
                self.direction = (1 if crow.rect.centerx > self.rect.centerx else -1)

                #Throw when cooldown expires
                if (self.throwTimer <= 0):

                    rock = ThrownRock(
                        self.rect.centerx + self.direction * 7, 
                        self.rect.top - 5,
                        crow.rect.centerx,
                        crow.rect.centery
                    )

                    self.rocks.append(rock)
                    self.throwTimer = self.throwDelay

                return

            #Regular residents give up
            elif (tooHigh and self.highEscapeTimer >= self.highEscapeDelay):
                self.state = "returning"
                self.highEscapeTimer = 0

            else: 
                self.moveTowards(crow.rect.centerx, self.chaseSpeed, dt, house)
                return

        #Returning home state
        if (self.state == "returning"):
            distanceHome = abs(self.rect.centerx - self.homeCenterX)

            if (distanceHome <= self.speed * dt + 1):
                self.rect.x = round(self.homeX)
                self.x = self.homeX
                self.state = "guarding"
                self.lookTimer = 0

            else:
                self.moveTowards(self.homeCenterX, self.speed, dt, house)

    def draw(self, surface):

        #Resident's position
        cx, cy = self.rect.center

        #Drawing the vision cone
        radius = int(self.visionRadius)
        size = radius * 2 + 4

        #Create a transparent yellow vision cone
        visionSurface = pygame.Surface((size, size), pygame.SRCALPHA)

        origin = radius + 2
        angle = 0 if self.direction == 1 else math.pi
        halfAngle = math.radians(45)

        points = [(origin, origin)]

        for i in range(21):
            a = angle - halfAngle + i * (2 * halfAngle / 20)

            px = origin + radius * math.cos(a)
            py = origin + radius * math.sin(a)

            points.append((int(px), int(py)))

        #Red when chasing, yellow otherwise
        if (self.state == "chasing"):
            coneColor = (255, 80, 65, 65)
        else:
            coneColor = (255, 230, 80, 50)

        pygame.draw.polygon(visionSurface, coneColor, points)

        surface.blit(visionSurface, (cx - origin, cy - origin))

        #Draw resident
        pygame.draw.rect(surface, (174, 111, 91), self.rect)

        #Eye faces movement direction
        eyeX = (self.rect.right - 3 if self.direction == 1 else self.rect.left + 1)

        pygame.draw.rect(surface, (234, 205, 174), (eyeX, self.rect.y + 2, 2, 2))

        #Alert exclamation mark
        if (self.state == "chasing" or self.alertTimer > 0):
            bubble = pygame.Rect(cx - 4, self.rect.top -15, 9, 12)

            pygame.draw.rect(surface, (255, 80, 65), bubble, border_radius = 2)

            #Exclamation line
            pygame.draw.rect(surface, (30, 25, 20), (cx, bubble.y + 2, 1, 6))

            #Exclamation dot
            pygame.draw.rect(surface, (30, 25, 20), (cx, bubble.y + 9, 1, 2))
         
class Treasure:
    def __init__(self, pos, name, value, noise):
        self.rect = pygame.Rect(pos[0], pos[1], 6, 6)
        self.name = name
        self.value = value
        self.noise = noise
        self.collected = False
        self.color = GOLD if value >= 5 else (160, 190, 190)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 1, self.rect.y + 1, 2, 1))
