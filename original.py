#!/usr/bin/env python
import pygame
import random
import sys
from pygame.locals import *

# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
TITLE = "Zombie Apocalypse"
# Window size definition
WINDOWWIDTH = 600
WINDOWHEIGHT = 600
SCOREZONE = 100
SCOREBOARD = pygame.Rect(0, 601, 100, 600)
BACKGROUNDCOLOR = (0, 0, 0)
FPS = 35
# Player Definition
PLAYERCOLOR = (255, 0, 0)
PLAYERSIZE = 15
PLAYERMOVERATE = 3
playerSafeZone = pygame.Rect(0, 0, 60, 60)
# Attack Definitions
ATTACKCOLOR = (255, 255, 0)
ZATTACKSIZE = 5
XATTACKSIZE = 5
ZATTACKSPEED = 5
XATTACKSPEED = 8
ZLIFE = 2
XLIFE = 15
ZNOISESIZE = 300
ZNOISEDIM = (ZNOISESIZE, ZNOISESIZE)
XNOISESIZE = 200
XNOISEDIM = (XNOISESIZE, XNOISESIZE)
ZNOISE = pygame.Rect((0, 0), (ZNOISEDIM))
XNOISE = pygame.Rect((0, 0), (XNOISEDIM))
# Zombie Definitions
ZOMCOLOR = (0, 255, 0)
ZOMSIZE = 17
zomSpeed = 1
zomSight = pygame.Rect(0, 0, 150, 150)
zomScore = 10
# Skeleton Definition
SKELCOLOR = (255, 255, 255)
SKELSIZE = 13
skelSpeed = 4
skelSight = pygame.Rect(0, 0, 100, 100)
skelScore = 15
SPAWNRATE = 1001
SPAWNINTERVAL = 50


def terminate():
    pygame.quit()
    sys.exit()


def newAttack(newdir, newtype, spawnlocation):
    if newtype == 'z':
        newAttackSpeed = ZATTACKSPEED
        newAttackSize = ZATTACKSIZE
        newAttackLife = ZLIFE
    elif newtype == 'x':
        newAttackSpeed = XATTACKSPEED
        newAttackSize = XATTACKSIZE
        newAttackLife = XLIFE
    newAttack = {
        'rect': pygame.Rect((spawnlocation),
                            (newAttackSize, newAttackSize)),
        'direction': newdir, 'life': newAttackLife, 'speed': newAttackSpeed,
    }
    attacks.append(newAttack)


def newEnemy(style):
    spawn = random.randint(1, SPAWNRATE)
    coin = random.randint(0, 10)
    if style == "z" and spawn >= zomSpawn:
        newSize = ZOMSIZE
        newColor = ZOMCOLOR
        newSpeed = zomSpeed
        newSight = zomSight
        newScore = zomScore
    elif style == "s" and spawn >= skelSpawn:
        newSize = SKELSIZE
        newColor = SKELCOLOR
        newSpeed = skelSpeed
        newSight = skelSight
        newScore = skelScore
    else:
        return
    if coin <= awareness:
        awake = True
    else:
        awake = False
    newMobile = {
        'rect': pygame.Rect(random.randint(1, WINDOWWIDTH - newSize),
                            random.randint(1, WINDOWHEIGHT - newSize), newSize,
                            newSize),
        'color': newColor,
        'speed': newSpeed,
        'sight': newSight,
        'awake': awake,
        'score': newScore
    }
    playerSafeZone.center = playerRect.center
    if newMobile['rect'].colliderect(playerSafeZone) == False:
        enemies.append(newMobile)


def textDraw(text, font, surface, x, y, color):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # pressing escape quits
                    terminate()
                if event.key == K_RETURN:
                    return


windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT + SCOREZONE))
pygame.display.set_caption(TITLE)
pygame.mouse.set_visible(False)
topScore = 0
TEXTCOLOR = (255, 255, 255)
font = pygame.font.SysFont(None, 24)
titlefont = pygame.font.SysFont(None, 48)
TITLECOLOR = (0, 128, 0)

# Outer loop
while True:

    pygame.draw.rect(windowSurface, BACKGROUNDCOLOR,
                     pygame.Rect(100, 50, 400, 500))
    textDraw(' %s ' % (TITLE), titlefont, windowSurface, 135, 60, TITLECOLOR)
    textDraw('Press Enter to start', font, windowSurface, 220, 500, TEXTCOLOR)
    textDraw('Top Score: %s' % (topScore), font, windowSurface, 250, 470,
             TEXTCOLOR)
    pygame.display.update()
    waitForPlayerToPressKey()
    # Set up game
    playerRect = pygame.Rect(0, 0, PLAYERSIZE, PLAYERSIZE)
    playerRect.center = ((WINDOWWIDTH / 2), (WINDOWHEIGHT / 2))
    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False
    lastMove = 0
    # Set up libraries
    attacks = []
    enemies = []
    # Variables
    awareness = 0
    score = 0
    playerLife = 10
    spawnSpeed = 0
    zomSpawn = 975
    skelSpawn = 995
    # main loop
    while True:
        for event in pygame.event.get():
            # End game if quit via window control
            if event.type == QUIT:
                terminate()

            # Activate player movement
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT:
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP:
                    moveDown = False
                    moveUp = True
                if event.key == K_DOWN:
                    moveUp = False
                    moveDown = True

                # Z attack creation
                if event.key == ord('z'):
                    ZNOISE.center = playerRect.center
                    for e in enemies:
                        if e['awake'] == False:
                            if ZNOISE.colliderect(e['rect']):
                                e['awake'] = True
                    if moveUp == True:
                        if moveLeft == True:
                            newAttack(4, 'z', playerRect.topleft)
                            newAttack(7, 'z', playerRect.topleft)
                            newAttack(8, 'z', playerRect.topleft)
                        elif moveRight == True:
                            newAttack(8, 'z', playerRect.topright)
                            newAttack(9, 'z', playerRect.topright)
                            newAttack(6, 'z', playerRect.topright)
                        else:
                            newAttack(7, 'z', playerRect.midtop)
                            newAttack(8, 'z', playerRect.midtop)
                            newAttack(9, 'z', playerRect.midtop)
                    elif moveDown == True:
                        if moveLeft == True:
                            newAttack(4, 'z', playerRect.bottomleft)
                            newAttack(1, 'z', playerRect.bottomleft)
                            newAttack(2, 'z', playerRect.bottomleft)
                        elif moveRight == True:
                            newAttack(6, 'z', playerRect.bottomright)
                            newAttack(3, 'z', playerRect.bottomright)
                            newAttack(2, 'z', playerRect.bottomright)
                        else:
                            newAttack(3, 'z', playerRect.midbottom)
                            newAttack(2, 'z', playerRect.midbottom)
                            newAttack(1, 'z', playerRect.midbottom)
                    elif moveLeft == True:
                        newAttack(7, 'z', playerRect.midleft)
                        newAttack(4, 'z', playerRect.midleft)
                        newAttack(1, 'z', playerRect.midleft)
                    elif moveRight == True:
                        newAttack(9, 'z', playerRect.midright)
                        newAttack(6, 'z', playerRect.midright)
                        newAttack(3, 'z', playerRect.midright)
                    else:
                        if lastMove == 2:
                            newAttack(3, 'z', playerRect.midbottom)
                            newAttack(2, 'z', playerRect.midbottom)
                            newAttack(1, 'z', playerRect.midbottom)
                        elif lastMove == 4:
                            newAttack(7, 'z', playerRect.midleft)
                            newAttack(4, 'z', playerRect.midleft)
                            newAttack(1, 'z', playerRect.midleft)
                        elif lastMove == 6:
                            newAttack(9, 'z', playerRect.midright)
                            newAttack(6, 'z', playerRect.midright)
                            newAttack(3, 'z', playerRect.midright)
                        elif lastMove == 8:
                            newAttack(7, 'z', playerRect.midtop)
                            newAttack(8, 'z', playerRect.midtop)
                            newAttack(9, 'z', playerRect.midtop)

                # X Attack Creation
                if event.key == ord('x'):
                    XNOISE.center = playerRect.center
                    for e in enemies:
                        if e['awake'] == False:
                            if XNOISE.colliderect(e['rect']):
                                e['awake'] = True
                    if moveUp == True:
                        if moveLeft == True:
                            newAttack(7, 'x', playerRect.topleft)
                        elif moveRight == True:
                            newAttack(9, 'x', playerRect.topright)
                        else:
                            newAttack(8, 'x', playerRect.midtop)
                    elif moveDown == True:
                        if moveLeft:
                            newAttack(1, 'x', playerRect.bottomleft)
                        elif moveRight == True:
                            newAttack(3, 'x', playerRect.bottomright)
                        else:
                            newAttack(2, 'x', playerRect.midbottom)
                    elif moveLeft == True:
                        newAttack(4, 'x', playerRect.midleft)
                    elif moveRight == True:
                        newAttack(6, 'x', playerRect.midright)
                    else:
                        if lastMove == 2:
                            newAttack(2, 'x', playerRect.midbottom)
                        elif lastMove == 4:
                            newAttack(4, 'x', playerRect.midleft)
                        elif lastMove == 6:
                            newAttack(6, 'x', playerRect.midright)
                        elif lastMove == 8:
                            newAttack(8, 'x', playerRect.midtop)

            # Deactivate player movement and save last direction
            if event.type == KEYUP:
                if event.key == K_LEFT or event.key == ord('a'):
                    moveLeft = False
                    lastMove = 4
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveRight = False
                    lastMove = 6
                if event.key == K_UP or event.key == ord('w'):
                    moveUp = False
                    lastMove = 8
                if event.key == K_DOWN or event.key == ord('s'):
                    moveDown = False
                    lastMove = 2
                # Close game if escape key is pressed
                if event.key == K_ESCAPE:
                    terminate()

        # Move the player around.
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

        # Move Attacks
        for a in attacks:
            if a['direction'] == 9:
                a['rect'].move_ip(a['speed'], - a['speed'])
            elif a['direction'] == 8:
                a['rect'].move_ip(0, - a['speed'])
            elif a['direction'] == 7:
                a['rect'].move_ip(- a['speed'], - a['speed'])
            elif a['direction'] == 6:
                a['rect'].move_ip(a['speed'], 0)
            elif a['direction'] == 4:
                a['rect'].move_ip(- a['speed'], 0)
            elif a['direction'] == 3:
                a['rect'].move_ip(a['speed'], a['speed'])
            elif a['direction'] == 2:
                a['rect'].move_ip(0, a['speed'])
            elif a['direction'] == 1:
                a['rect'].move_ip(- a['speed'], a['speed'])

        # Move enemies
        for e in enemies:
            if e['awake'] == False:
                shuffle = random.randint(1, 10)
                if shuffle == 1 and e['rect'].left > 0 and e[
                    'rect'].bottom < WINDOWHEIGHT:
                    e['rect'].move_ip(-1, 1)
                elif shuffle == 2 and e['rect'].bottom < WINDOWHEIGHT:
                    e['rect'].move_ip(0, 1)
                elif shuffle == 3 and e['rect'].right < WINDOWWIDTH and e[
                    'rect'].bottom < WINDOWHEIGHT:
                    e['rect'].move_ip(1, 1)
                elif shuffle == 4 and e['rect'].left > 0:
                    e['rect'].move_ip(-1, 0)
                elif shuffle == 6 and e['rect'].right < WINDOWWIDTH:
                    e['rect'].move_ip(1, 0)
                elif shuffle == 7 and e['rect'].left > 0 and e['rect'].top > 0:
                    e['rect'].move_ip(-1, -1)
                elif shuffle == 8 and e['rect'].top > 0:
                    e['rect'].move_ip(0, -1)
                elif shuffle == 9 and e['rect'].right < WINDOWWIDTH and e[
                    'rect'].top > 0:
                    e['rect'].move_ip(1, 1)
            elif e['awake'] == True:
                if playerRect.centerx > e['rect'].centerx:
                    if playerRect.centery > e['rect'].centery:
                        e['rect'].move_ip(e['speed'], e['speed'])
                    elif playerRect.centery < e['rect'].centery:
                        e['rect'].move_ip(e['speed'], - e['speed'])
                    else:
                        e['rect'].move_ip(e['speed'], 0)
                elif playerRect.centerx < e['rect'].centerx:
                    if playerRect.centery > e['rect'].centery:
                        e['rect'].move_ip(- e['speed'], e['speed'])
                    elif playerRect.centery < e['rect'].centery:
                        e['rect'].move_ip(- e['speed'], - e['speed'])
                    else:
                        e['rect'].move_ip(- e['speed'], 0)
                elif playerRect.centery > e['rect'].centery:
                    e['rect'].move_ip(0, e['speed'])
                elif playerRect.centery < e['rect'].centery:
                    e['rect'].move_ip(0, - e['speed'])

        # Collision checks
        # Attacks against Enemies
        for a in attacks[:]:
            for e in enemies[:]:
                if a['rect'].colliderect(e['rect']) == True:
                    score += e['score']
                    enemies.remove(e)
                    attacks.remove(a)
                    break
        # Player Against Enemies
        for e in enemies[:]:
            if playerRect.colliderect(e['rect']) == True:
                playerLife -= 1
                enemies.remove(e)
        # Wake zones
        for e in enemies:
            if e['awake'] == False:
                e['sight'].center = e['rect'].center
            if e['sight'].colliderect(playerRect) == True:
                e['awake'] = True
            for e2 in enemies:
                if e2['awake'] == True:
                    e['sight'].center = e['rect'].center
                    if e['sight'].colliderect(e2['rect']):
                        e['awake'] = True

        # Spawn
        # Enemies
        newEnemy("s")
        newEnemy("z")

        # Draw frame
        windowSurface.fill(BACKGROUNDCOLOR)
        for a in attacks:
            pygame.draw.rect(windowSurface, ATTACKCOLOR, a['rect'])
        pygame.draw.rect(windowSurface, PLAYERCOLOR, playerRect)
        for e in enemies:
            pygame.draw.rect(windowSurface, e['color'], e['rect'])
        # Score area
        pygame.draw.rect(windowSurface, BACKGROUNDCOLOR, SCOREBOARD)
        # Draw the score and top score.
        textDraw('Score: %s' % (score), font, windowSurface, 20, 620, TEXTCOLOR)
        textDraw('Top Score: %s' % (topScore), font, windowSurface, 20, 660,
                 TEXTCOLOR)
        if playerLife >= 1:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(550, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(550, 620, 30, 30), 2)
        if playerLife >= 2:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(510, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(510, 620, 30, 30), 2)
        if playerLife >= 3:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(470, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(470, 620, 30, 30), 2)
        if playerLife >= 4:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(430, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(430, 620, 30, 30), 2)
        if playerLife >= 5:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(390, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(390, 620, 30, 30), 2)
        if playerLife >= 6:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(350, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(350, 620, 30, 30), 2)
        if playerLife >= 7:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(310, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(310, 620, 30, 30), 2)
        if playerLife >= 8:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(270, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(270, 620, 30, 30), 2)
        if playerLife >= 9:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(230, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(230, 620, 30, 30), 2)
        if playerLife >= 10:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(190, 620, 30, 30))
        else:
            pygame.draw.rect(windowSurface, PLAYERCOLOR,
                             pygame.Rect(190, 620, 30, 30), 2)

        # Age and remove attacks
        for a in attacks[:]:
            if (a['life'] < 0
                    or a['rect'].bottom < 0
                    or a['rect'].top > WINDOWHEIGHT
                    or a['rect'].left > WINDOWWIDTH
                    or a['rect'].right < 0):
                attacks.remove(a)
            a['life'] -= 1

        # Break loop if player is dead.
        if playerLife <= 0:
            break

        spawnSpeed += 1
        if spawnSpeed == SPAWNINTERVAL:
            zomSpawn -= 1
            skelSpawn -= 1

        # Update screen
        pygame.display.update()
        mainClock.tick(FPS)

    # Draw Game over screen
    pygame.draw.rect(windowSurface, BACKGROUNDCOLOR,
                     pygame.Rect(100, 50, 400, 500))
    textDraw('GAME OVER', titlefont, windowSurface, 195, 60, TITLECOLOR)
    textDraw('Press Enter to continue', font, windowSurface, 220, 500,
             TEXTCOLOR)
    if score > topScore:
        topScore = score
        textDraw('New High Score!: %s' % (topScore), font, windowSurface, 245,
                 470, TEXTCOLOR)
    else:
        textDraw('Top Score: %s' % (topScore), font, windowSurface, 250, 470,
                 TEXTCOLOR)
    pygame.display.update()
    waitForPlayerToPressKey()