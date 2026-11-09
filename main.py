import pygame
from settings import *
from entities import Crow, Grandma, Treasure
from house import House

pygame.init()
pygame.display.set_caption("The Crow Job")
window = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))                              #Part of the house user can see
worldSurface = pygame.Surface((SCREEN_WIDTH * 3, SCREEN_HEIGHT))                    #The whole house (even offscreen parts)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 12)
bigFont = pygame.font.Font(None, 22)
messageFont = pygame.font.Font("SebladeBlackRegular.ttf", 10)

#Function for drawing text 
def draw_text(surface, text, x, y, color=WHITE, font_obj=font):
    font_obj = pygame.font.Font("SebladeBlackRegular.ttf", 10)
    image = font_obj.render(text, False, color)
    surface.blit(image, (x, y))

def draw_bar(surface, x, y, width, height, value, color):
    pygame.draw.rect(surface, DARK, (x, y, width, height))
    pygame.draw.rect(surface, color, (x + 1, y + 1, int((width - 2) * max(0, min(1, value))), height - 2))

def reset_game(houseNumber):
    house = House(houseNumber)
    crow = Crow(*house.crowStart)
    residents = [Grandma(pos, house.residentSpeed, house.visionRadius, canThrow = houseNumber == 3 and i == len(house.residentStarts) - 1)
                 for i, pos in enumerate(house.residentStarts)]
    treasures = [Treasure(pos, name, value, noise)
                 for pos, name, value, noise in house.treasureData]
    return house, crow, residents, treasures

houseNumber = 1
house, crow, residents, treasures = reset_game(houseNumber)
totalScore = 0
message = "Find something shiny. Get out before you're spotted!"
messageTimer = 50
gameState = "playing"  # playing, caught, won

running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if gameState == "playing":

                #Picking up treaures 
                if event.key == pygame.K_e:
                    picked = crow.try_pickup(treasures)
                    if picked:
                        message = f"Stolen: {picked.name}!"
                        messageTimer = 30
                    else:
                        message = "Nothing close enough to steal."
                        messageTimer = 20

                #Hiding in the house
                if event.key == pygame.K_h:
                    crow.toggle_hide(house.hidingSpots)
                    message = "You are hiding." if crow.hidden else "Back to business."
                    messageTimer = 50

                if event.key == pygame.K_RETURN and crow.rect.colliderect(house.exitPlace):
                    if crow.inventory:
                        totalScore += sum(item.value for item in crow.inventory)
                        if houseNumber >= MAX_HOUSES:
                            gameState = "won"
                        else:
                            houseNumber += 1
                            house, crow, residents, treasures = reset_game(houseNumber)
                            message = f"House {houseNumber}. The stakes are getting higher..."
                            messageTimer = 50
                    else:
                        message = "You can't go home empty-beaked. Steal something first!"
                        messageTimer = 30

            elif gameState in ("caught", "won") and event.key == pygame.K_r:
                houseNumber = 1
                totalScore = 0
                house, crow, residents, treasures = reset_game(houseNumber)
                gameState = "playing"
                message = "A fresh start. A fresh nest."
                messageTimer = 50

    if gameState == "playing":
        keys = pygame.key.get_pressed()
        crow.update(dt, keys, house.solidWalls, house.platforms)

        #Ensure that the message timer will be descresed
        if (messageTimer > 0):
            messageTimer -= 1

        #Updates residents and checks for contact
        for resident in residents:
            resident.update(dt, house, crow)

            #Resident physically catches crow
            if (resident.rect.colliderect(crow.rect)):
                gameState = "caught"
                message = "You were caught!"
                messageTimer = 120
                break

            #Checking whether thrown rock hit the crow 
            for rock in resident.rocks:
                if (rock.rect.colliderect(crow.rect)):
                    gameState = "caught"
                    message = "You were hit by a rock"
                    break

            if (gameState == "caught"):
                break

        #Suspicion bar as alert indicator
        crow.suspicion = (100 if any(r.state == "chasing" for r in residents) else 0)

    #Draw the entire house first
    worldSurface.fill(FLOOR_COLOR)
    house.draw(worldSurface)

    for treasure in treasures:
        if not treasure.collected:
            treasure.draw(worldSurface)

    for resident in residents:
        resident.draw(worldSurface)

        for rock in resident.rocks:
            rock.draw(worldSurface)

    crow.draw(worldSurface)

    #Camera that follow the crow horizontally
    cameraX = crow.rect.centerx - SCREEN_WIDTH // 2

    #Prevent the camera from scrolling beyond the house
    cameraX = max(0, min(cameraX, house.worldWidth - SCREEN_WIDTH))

    #Drawing visible parts of the world 
    canvas.fill(FLOOR_COLOR)
    canvas.blit(worldSurface, (-cameraX, 0))

    # HUD
    pygame.draw.rect(canvas, HUD_BG, (3, 3, 112, 25))
    draw_text(canvas, f"HOUSE {houseNumber}/{MAX_HOUSES}", 7, 6)
    draw_text(canvas, f"BAG:", 7, 16)
    for i, item in enumerate(crow.inventory):
            pygame.draw.rect(canvas, item.color, (35 + i * 12, 18, 7, 7))
    pygame.draw.rect(canvas, HUD_BG, (SCREEN_WIDTH - 94, 3, 91, 25))
    draw_text(canvas, "SUSPICION", SCREEN_WIDTH - 90, 6)
    draw_bar(canvas, SCREEN_WIDTH - 90, 16, 82, 7, crow.suspicion / 100, ALERT_COLOR)

    if (messageTimer > 0 and gameState == "playing"):

        #Convert message into image
        textSurface = messageFont.render(message, False, WHITE)

        #Centering the text in the middle of the screen at the bottom
        textRect = textSurface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 22))

        #Text background that's slightly bigger than the text
        backgroundRect = textRect.inflate(12, 6)

        #Drawing the background
        pygame.draw.rect(canvas, HUD_BG, backgroundRect)

        #Drawing text over the background
        canvas.blit(textSurface, textRect)

    # End-state overlays
    if gameState in ("caught", "won"):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 18, 210))
        canvas.blit(overlay, (0, 0))
        title = "CAUGHT!" if gameState == "caught" else "THE NEST IS FULL!"
        subtitle = "The residents noticed you." if gameState == "caught" else "You've conquered the neighborhood."
        draw_text(canvas, title, 105, 62, ALERT_COLOR if gameState == "caught" else GOLD, bigFont)
        draw_text(canvas, subtitle, 75, 88)
        draw_text(canvas, f"Total loot value: {totalScore}", 93, 105)
        draw_text(canvas, "Press R to play again  |  ESC to quit", 66, 128)

    # Scale using nearest-neighbor for crisp pixel edges.
    scaled = pygame.transform.scale(canvas, window.get_size())
    window.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()

