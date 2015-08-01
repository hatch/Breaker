__author__ = 'ryanmcintire'

import sys
import os
import math

import pygame
from pygame import locals

##########
#
#Globals

SCREEN_SIZE_X = 600
SCREEN_SIZE_Y = 650
STATUS_FIELD_X = 600
STATUS_FIELD_Y = 50
GAME_FIELD_X = 600
GAME_FIELD_Y = 600
CELL_SIZE_X = int(GAME_FIELD_X / 100)
CELL_SIZE_Y = int(GAME_FIELD_Y / 100)
BASE_SPEED = 2


class Game():

    def __init__(self):

        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        sounds = {}
        self.newGameSession()
        pass

    def newGameSession(self):
        self.gameSession = GameSession()

class MenuSystem():
    pass


class Menu():
    pass



class MainMenu(Menu):
    pass



class HighScoreMenu(Menu):
    pass



class Options(Menu):
    pass



class GameSession():

    def __init__(self):
        self.initializeGame()
        self.gameLoop()


    def initializeGame(self):
        self.screen = pygame.display.set_mode((SCREEN_SIZE_X, SCREEN_SIZE_Y))
        pygame.display.set_caption("Block Breaker 5000!")
        pygame.mouse.set_visible(False)
        self.player = Player()
        self.player.setPlayerNewGame()
        self.statusField = StatusField(self)
        self.collisionSpace = CollisionSpace()
        self.paddle = Paddle()
        self.ball = Ball(self.collisionSpace, self.paddle, self.player)
        self.blockField = BlockField(self.collisionSpace)
        self.ballLost = False

    def resetAfterLostBall(self):
        self.ball.ballLockedToPaddle()

    def gameLoop(self):
        flagKeyPressed = False
        playerLiving = True
        while playerLiving:
            for event in pygame.event.get():
                if event.type == locals.QUIT:
                    sys.exit()
                elif event.type == locals.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    move_x, move_y = event.rel
                elif event.type == locals.KEYDOWN:
                    flagKeyPressed = True
                elif event.type == locals.KEYUP:
                    flagKeyPressed = False

                if flagKeyPressed:
                    keysPressed = pygame.key.get_pressed()
                    if keysPressed[locals.K_SPACE] and self.ball.ballLockedToPaddle:
                        self.ball.ballUnlockFromPaddle()

            self.screen.fill((0,0,0))
            self.paddle.move(mouse_x)
            ballHit = self.ball.move()
            self.blockField.draw(self.screen)
            self.ball.draw(self.screen)
            self.paddle.draw(self.screen)
            self.statusField.draw()
            if ballHit:
                print(ballHit)
            if ballHit == "block_hit":
                self.player.addPointsToScore(10)
            elif ballHit == "bottom_out":
                print("Here...")
                self.playerLiving = self.playerLostBall()
            pygame.display.update()

    def playerLostBall(self):
        self.player.removeBall()

        return True

class StatusField:
    ##TODO CREATE BORDER
    pygame.font.init()
    font = pygame.font.Font(None, 24)


    def __init__(self, gameSession):
        self.gameSession = gameSession

    def draw(self):
        self.statusPrint(self.font, 10, 5, "Balls Remaining: ", str(self.gameSession.player.ballsRemaining))
        self.statusPrint(self.font, 250, 5, "Score:", str(self.gameSession.player.score))


    def statusPrint(self, font, x, y, text, varText, color=(255, 255, 255)):
        textToPrint = font.render(text, True, color)
        textWidth = self.font.size(text)[0] + 5
        varTextToPrint = font.render(varText, True, color)
        self.gameSession.screen.blit(textToPrint, (x, y))
        self.gameSession.screen.blit(varTextToPrint, (x+textWidth, y))

class Player:

    def setPlayerNewGame(self):
        self.ballsRemaining = 3
        self.score = 0

    def addPointsToScore(self, morePoints):
        self.score += morePoints

    def removeBall(self):
        self.ballsRemaining -= 1

    def testForHighScore(self):
        pass


class BoxPiece:
    pos_x = 0
    pos_y = 0
    width = 0
    height = 0

    def getMinMax(self):
        min_x = self.pos_x
        max_x = self.pos_x + self.width
        min_y = self.pos_y
        max_y = self.pos_y + self.height
        return((min_x, min_y), (max_x, max_y))


class Paddle(BoxPiece):

    heightFactor = 3
    widthFactor = 10
    color = 255, 255, 255

    def __init__(self):
        self.height = CELL_SIZE_Y * self.heightFactor
        self.width = CELL_SIZE_X * self.widthFactor
        self.pos_x = (GAME_FIELD_X / 2) - (self.width / 2)
        self.pos_y = GAME_FIELD_Y - self.height * 2 + STATUS_FIELD_Y

    def move(self, mouse_x):
        if mouse_x + self.width > GAME_FIELD_X:
            self.pos_x = GAME_FIELD_X - self.width
        else:
            self.pos_x = mouse_x

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos_x, self.pos_y, self.width, self.height), 0)


class Ball:
    radius = int(CELL_SIZE_X)
    color = 255, 0, 0
    pygame.mixer.init(44100, -16, 2, 4096)
    sounds = {}
    sounds['paddle_hit'] = pygame.mixer.Sound(os.path.join('data', 'paddle_hit.wav'))
    sounds['block_hit'] = pygame.mixer.Sound(os.path.join('data', 'block_hit.wav'))
    sounds['ball_loss'] = pygame.mixer.Sound(os.path.join('data', 'ball_loss.wav'))

    def __init__(self, collisionSpace, paddle, player):
        self.paddle = paddle
        self.ballLockedToPaddle = True
        self.positionOnPaddle()
        self.velocity_x = -2 * BASE_SPEED
        self.velocity_y = -2 * BASE_SPEED
        self.collisionSpace = collisionSpace
        self.player = player
        self.ballLost = True
        ##TODO - Paddle moves around while ball lost.
        ##TODO - Create timedown until reset position on paddle.



    def pointsCross(self):
        bot_y = self.pos_y + self.radius
        top_y = self.pos_y - self.radius
        right_x = self.pos_x + self.radius
        left_x = self.pos_x - self.radius
        return (bot_y, top_y, right_x, left_x)

    def collisionCross(self):
        new_x, new_y = self.calcNewPosition()
        bot_y, top_y, right_x, left_x = self.pointsCross()
        return (new_x, new_y, bot_y, top_y, right_x, left_x)

    def testScreenCollision(self):
        bot_y, top_y, right_x, left_x = self.pointsCross()
        if right_x > GAME_FIELD_X or left_x < 0:
            self.velocity_x = -self.velocity_x
        if top_y < 0:
            self.velocity_y = -self.velocity_y

    def testBlockCollision(self):
        bot_y, top_y, right_x, left_x = self.pointsCross()
        points = {}
        points['top'] = (self.pos_x, top_y)
        points['bottom'] = (self.pos_x, bot_y)
        points['left'] = (left_x, self.pos_y)
        points['right'] = (right_x, self.pos_y)
        for point in points:
            if self.collisionSpace.testForCollision(points[point]):
                if point == 'left' or point == 'right':
                    self.velocity_x = -self.velocity_x
                if point == 'top' or point == 'bottom':
                    self.velocity_y = -self.velocity_y
                self.sounds['block_hit'].play()
                self.player.addPointsToScore(20)
                break

    def testPaddleCollision(self):
        paddle = self.paddle
        bot_y, top_y, right_x, left_x = self.pointsCross()
        if bot_y >= paddle.pos_y and bot_y <= paddle.pos_y + paddle.height:
            if right_x > paddle.pos_x and left_x < paddle.pos_x + paddle.width:
                self.velocity_y = -self.velocity_y
                self.pos_y = paddle.pos_y - self.radius
                self.sounds['paddle_hit'].play()
            elif right_x == paddle.pos_x or left_x == paddle.pos_x + paddle.width:
                self.velocity_x = -self.velocity_x
                self.sounds['paddle_hit'].play()


    def testBottomCollision(self):
        bot_y, top_y, right_x, left_x = self.pointsCross()
        if top_y > GAME_FIELD_Y + STATUS_FIELD_Y and top_y < GAME_FIELD_Y + STATUS_FIELD_Y + 30:
            channel = self.sounds['ball_loss'].play()
            self.ballLost = True
            self.player.removeBall()

    def ballUnlockFromPaddle(self):
        self.ballLockedToPaddle = False

    def ballLockToPaddle(self):
        self.ballLockedToPaddle = True

    def positionOnPaddle(self):
        self.pos_x = self.paddle.pos_x + int(self.paddle.width/2)
        self.pos_y = self.paddle.pos_y - self.radius - 4

    def move(self):

        if self.ballLockedToPaddle:
            self.positionOnPaddle()
            return


        if self.testScreenCollision():
           pass
        elif self.testBlockCollision():
            self.player.addPointsToScore(20)
        elif self.testPaddleCollision():
            pass
        elif self.testBottomCollision():
            self.player.removeBall()

        self.pos_x += self.velocity_x
        self.pos_y += self.velocity_y

        return None


    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.pos_x, self.pos_y), self.radius, 0)


class Block(BoxPiece):

    heightFactor = 4
    widthFactor = 5
    leftGap = CELL_SIZE_X * 4
    topGap = CELL_SIZE_Y * 4
    twixtGap = CELL_SIZE_X * 2
    color = 0, 200, 200

    def __init__(self, row, column, blockField):
        self.height = CELL_SIZE_Y * self.heightFactor
        self.width = CELL_SIZE_X * self.widthFactor
        self.blockField = blockField
        self.row = row
        self.column = column

        self.pos_x = self.leftGap + column * (self.width + self.twixtGap)
        self.pos_y = self.topGap + row * (self.height + self.twixtGap) + STATUS_FIELD_Y

        self.unbroken = True

    def draw(self, screen):
        if self.unbroken:
            pygame.draw.rect(screen, self.color, (self.pos_x, self.pos_y, self.width, self.height), 0)

    def setBroken(self):
        self.unbroken = False

class BlockField:

    def __init__(self, collisionSpace):
        self.rows = 6
        self.columns = 12
        self.collisionSpace = collisionSpace
        self.createBlockField()

    def createBlockField(self):
        ##TODO
        self.blockField = [[Block(row, column, self) for row in range(self.rows)] for column in range(self.columns)]
        [[self.collisionSpace.insertIntoCollisionSpace(block) for block in column] for column in self.blockField]
        pass

    def draw(self, screen):
        [[block.draw(screen) for block in column] for column in self.blockField]

    def destroy(self, block):
        self.blockField[block.column][block.row] = None

class CollisionSpace:

    def __init__(self):
        self.cell_size = CELL_SIZE_X
        self.grid = {}

    def hashFunction(self, point):
        hashed_x = int(point[0]/CELL_SIZE_X)
        hashed_y = int(point[1]/CELL_SIZE_Y)
        hashed_x = int(hashed_x)
        hashed_y = int(hashed_y)
        return hashed_x, hashed_y

    def insertIntoCollisionSpace(self, insertableObject):
        min, max = insertableObject.getMinMax()
        min, max = self.hashFunction(min), self.hashFunction(max)
        for x_slot in range(min[0], max[0]+1):
            for y_slot in range(min[1], max[1]+1):
                self.grid[(x_slot, y_slot)] = insertableObject

    def testForCollision(self, point):
        point = self.hashFunction(point)
        if point in self.grid:
            collisionObject = self.grid[point]
            print(collisionObject)

            if isinstance(collisionObject, Block):
                if collisionObject.unbroken:
                    collisionObject.setBroken()
                    self.removeObjectFromGrid(point)
                    return True
                else:
                    return False

    def removeObjectFromGrid(self, point):
        if point in self.grid:
            removableObject = self.grid[point]
            min, max = removableObject.getMinMax()
            min, max = self.hashFunction(min), self.hashFunction(max)
            for x_slot in range(min[0], max[0]+1):
                for y_slot in range(min[1], max[1]+1):
                    del self.grid[(x_slot, y_slot)]



game = Game()

