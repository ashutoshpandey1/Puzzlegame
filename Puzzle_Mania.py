
from tkinter import *
import math
from PIL import Image
import os
import random, pygame, sys
from pygame.locals import *
import time



def startmemory():
    FPS = 30  # frames per second, the general speed of the program
    WINDOWWIDTH = 640  # size of window's width in pixels
    WINDOWHEIGHT = 480  # size of windows' height in pixels
    REVEALSPEED = 8  # speed boxes' sliding reveals and covers
    BOXSIZE = 40  # size of box height & width in pixels
    GAPSIZE = 10  # size of gap between boxes in pixels
    BOARDWIDTH = 10  # number of columns of icons
    BOARDHEIGHT = 7  # number of rows of icons
    assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
    XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
    YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

    #            R    G    B
    GRAY = (100, 100, 100)
    NAVYBLUE = (60, 60, 100)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 128, 0)
    PURPLE = (255, 0, 255)
    CYAN = (0, 255, 255)

    BGCOLOR = NAVYBLUE
    LIGHTBGCOLOR = GRAY
    BOXCOLOR = WHITE
    HIGHLIGHTCOLOR = BLUE

    DONUT = 'donut'
    SQUARE = 'square'
    DIAMOND = 'diamond'
    LINES = 'lines'
    OVAL = 'oval'

    ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
    ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
    assert len(ALLCOLORS) * len(
        ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."

    def main():
        global FPSCLOCK, DISPLAYSURF
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

        mousex = 0  # used to store x coordinate of mouse event
        mousey = 0  # used to store y coordinate of mouse event
        pygame.display.set_caption('Memory Puzzle Game')


        mainBoard = getRandomizedBoard()
        revealedBoxes = generateRevealedBoxesData(False)

        firstSelection = None  # stores the (x, y) of the first box clicked.

        DISPLAYSURF.fill(BGCOLOR)
        startGameAnimation(mainBoard)
        while True:  # main game loop

            mouseClicked = False

            DISPLAYSURF.fill(BGCOLOR)  # drawing the window
            drawBoard(mainBoard, revealedBoxes)

            for event in pygame.event.get():  # event handling loop

                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    puzzle_mania()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True

            boxx, boxy = getBoxAtPixel(mousex, mousey)
            if boxx != None and boxy != None:
                # The mouse is currently over a box.
                if not revealedBoxes[boxx][boxy]:
                    drawHighlightBox(boxx, boxy)
                if not revealedBoxes[boxx][boxy] and mouseClicked:
                    revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                    revealedBoxes[boxx][boxy] = True  # set the box as "revealed"
                    if firstSelection == None:  # the current box was the first box clicked
                        firstSelection = (boxx, boxy)
                    else:  # the current box was the second box clicked
                        # Check if there is a match between the two icons.
                        icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                        icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                        if icon1shape != icon2shape or icon1color != icon2color:
                            # Icons don't match. Re-cover up both selections.
                            pygame.time.wait(1000)  # 1000 milliseconds = 1 sec
                            coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                            revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                            revealedBoxes[boxx][boxy] = False
                        elif hasWon(revealedBoxes):  # check if all pairs found
                            gameWonAnimation(mainBoard)
                            pygame.time.wait(2000)

                            # Reset the board
                            mainBoard = getRandomizedBoard()
                            revealedBoxes = generateRevealedBoxesData(False)

                            # Show the fully unrevealed board for a second.
                            drawBoard(mainBoard, revealedBoxes)
                            pygame.display.update()
                            pygame.time.wait(1000)

                            # Replay the start game animation.
                            startGameAnimation(mainBoard)
                        firstSelection = None  # reset firstSelection variable

            # Redraw the screen and wait a clock tick.
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def generateRevealedBoxesData(val):
        revealedBoxes = []
        for i in range(BOARDWIDTH):
            revealedBoxes.append([val] * BOARDHEIGHT)
        return revealedBoxes

    def getRandomizedBoard():
        # Get a list of every possible shape in every possible color.
        icons = []
        for color in ALLCOLORS:
            for shape in ALLSHAPES:
                icons.append((shape, color))

        random.shuffle(icons)  # randomize the order of the icons list
        numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)  # calculate how many icons are needed
        icons = icons[:numIconsUsed] * 2  # make two of each
        random.shuffle(icons)

        # Create the board data structure, with randomly placed icons.
        board = []
        for x in range(BOARDWIDTH):
            column = []
            for y in range(BOARDHEIGHT):
                column.append(icons[0])
                del icons[0]  # remove the icons as we assign them
            board.append(column)
        return board

    def splitIntoGroupsOf(groupSize, theList):
        # splits a list into a list of lists, where the inner lists have at
        # most groupSize number of items.
        result = []
        for i in range(0, len(theList), groupSize):
            result.append(theList[i:i + groupSize])
        return result

    def leftTopCoordsOfBox(boxx, boxy):
        # Convert board coordinates to pixel coordinates
        left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
        top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
        return (left, top)

    def getBoxAtPixel(x, y):
        for boxx in range(BOARDWIDTH):
            for boxy in range(BOARDHEIGHT):
                left, top = leftTopCoordsOfBox(boxx, boxy)
                boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
                if boxRect.collidepoint(x, y):
                    return (boxx, boxy)
        return (None, None)

    def drawIcon(shape, color, boxx, boxy):
        quarter = int(BOXSIZE * 0.25)  # syntactic sugar
        half = int(BOXSIZE * 0.5)  # syntactic sugar

        left, top = leftTopCoordsOfBox(boxx, boxy)  # get pixel coords from board coords
        # Draw the shapes
        if shape == DONUT:
            pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
            pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
        elif shape == SQUARE:
            pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
        elif shape == DIAMOND:
            pygame.draw.polygon(DISPLAYSURF, color, (
                (left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1),
                (left, top + half)))
        elif shape == LINES:
            for i in range(0, BOXSIZE, 4):
                pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
                pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + i))
        elif shape == OVAL:
            pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))

    def getShapeAndColor(board, boxx, boxy):
        # shape value for x, y spot is stored in board[x][y][0]
        # color value for x, y spot is stored in board[x][y][1]
        return board[boxx][boxy][0], board[boxx][boxy][1]

    def drawBoxCovers(board, boxes, coverage):
        # Draws boxes being covered/revealed. "boxes" is a list
        # of two-item lists, which have the x & y spot of the box.
        for box in boxes:
            left, top = leftTopCoordsOfBox(box[0], box[1])
            pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
            shape, color = getShapeAndColor(board, box[0], box[1])
            drawIcon(shape, color, box[0], box[1])
            if coverage > 0:  # only draw the cover if there is an coverage
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

    def revealBoxesAnimation(board, boxesToReveal):
        # Do the "box reveal" animation.
        for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
            drawBoxCovers(board, boxesToReveal, coverage)

    def coverBoxesAnimation(board, boxesToCover):
        # Do the "box cover" animation.
        for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
            drawBoxCovers(board, boxesToCover, coverage)

    def drawBoard(board, revealed):
        # Draws all of the boxes in their covered or revealed state.
        for boxx in range(BOARDWIDTH):
            for boxy in range(BOARDHEIGHT):
                left, top = leftTopCoordsOfBox(boxx, boxy)
                if not revealed[boxx][boxy]:
                    # Draw a covered box.
                    pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
                else:
                    # Draw the (revealed) icon.
                    shape, color = getShapeAndColor(board, boxx, boxy)
                    drawIcon(shape, color, boxx, boxy)

    def drawHighlightBox(boxx, boxy):
        left, top = leftTopCoordsOfBox(boxx, boxy)
        pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

    def startGameAnimation(board):
        # Randomly reveal the boxes 8 at a time.
        coveredBoxes = generateRevealedBoxesData(False)
        boxes = []
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                boxes.append((x, y))
        random.shuffle(boxes)
        boxGroups = splitIntoGroupsOf(8, boxes)

        drawBoard(board, coveredBoxes)
        for boxGroup in boxGroups:
            revealBoxesAnimation(board, boxGroup)
            coverBoxesAnimation(board, boxGroup)

    def gameWonAnimation(board):
        # flash the background color when the player has won
        coveredBoxes = generateRevealedBoxesData(True)
        color1 = LIGHTBGCOLOR
        color2 = BGCOLOR

        for i in range(30):
            color1, color2 = color2, color1  # swap colors
            DISPLAYSURF.fill(color1)
            drawBoard(board, coveredBoxes)
            pygame.display.update()
            pygame.time.wait(300)

    def hasWon(revealedBoxes):
        # Returns True if all the boxes have been revealed, otherwise False
        for i in revealedBoxes:
            if False in i:
                return False  # return False if any boxes are covered.
        return True

    main()


# Number Puzzle
def startnumber():
    # Create the constants (go ahead and experiment with different values)
    BOARDWIDTH = 4  # number of columns in the board
    BOARDHEIGHT = 4  # number of rows in the board
    TILESIZE = 80
    WINDOWWIDTH = 640
    WINDOWHEIGHT = 480
    FPS = 30
    BLANK = None

    #                 R    G    B
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BRIGHTBLUE = (0, 50, 255)
    DARKTURQUOISE = (3, 54, 73)
    GREEN = (0, 204, 0)

    BGCOLOR = DARKTURQUOISE
    TILECOLOR = GREEN
    TEXTCOLOR = WHITE
    BORDERCOLOR = BRIGHTBLUE
    BASICFONTSIZE = 20

    BUTTONCOLOR = WHITE
    BUTTONTEXTCOLOR = BLACK
    MESSAGECOLOR = WHITE

    XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
    YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

    def main():
        global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT, QUIT_SURF, QUIT_RECT

        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Number Slide Puzzle')
        BASICFONT = pygame.font.Font('Hello Avocado.ttf', BASICFONTSIZE)

        # Store the option buttons and their rectangles in OPTIONS.
        RESET_SURF, RESET_RECT = makeText('Reset', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
        NEW_SURF, NEW_RECT = makeText('New Game', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
        SOLVE_SURF, SOLVE_RECT = makeText('Solve', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

        mainBoard, solutionSeq = generateNewPuzzle(80)
        SOLVEDBOARD = getStartingBoard()  # a solved board is the same as the board in a start state.
        allMoves = []  # list of moves made from the solved configuration

        while True:  # main game loop
            slideTo = None  # the direction, if any, a tile should slide
            msg = 'Click tile or press arrow keys to slide.'  # contains the message to show in the upper left corner.
            if mainBoard == SOLVEDBOARD:
                msg = 'Solved!'

            drawBoard(mainBoard, msg)

            for event in pygame.event.get():  # event handling loop
                if event.type == QUIT:
                    pygame.quit()
                    puzzle_mania()
                if event.type == MOUSEBUTTONUP:
                    spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                    if (spotx, spoty) == (None, None):
                        # check if the user clicked on an option button
                        if RESET_RECT.collidepoint(event.pos):
                            resetAnimation(mainBoard, allMoves)  # clicked on Reset button
                            allMoves = []
                        elif NEW_RECT.collidepoint(event.pos):
                            mainBoard, solutionSeq = generateNewPuzzle(80)  # clicked on New Game button
                            allMoves = []
                        elif SOLVE_RECT.collidepoint(event.pos):
                            resetAnimation(mainBoard, solutionSeq + allMoves)  # clicked on Solve button
                            allMoves = []

                    else:
                        # check if the clicked tile was next to the blank spot

                        blankx, blanky = getBlankPosition(mainBoard)
                        if spotx == blankx + 1 and spoty == blanky:
                            slideTo = LEFT
                        elif spotx == blankx - 1 and spoty == blanky:
                            slideTo = RIGHT
                        elif spotx == blankx and spoty == blanky + 1:
                            slideTo = UP
                        elif spotx == blankx and spoty == blanky - 1:
                            slideTo = DOWN

                elif event.type == KEYUP:
                    # check if the user pressed a key to slide a tile
                    if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                        slideTo = LEFT
                    elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                        slideTo = RIGHT
                    elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                        slideTo = UP
                    elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                        slideTo = DOWN

            if slideTo:
                slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.',
                               8)  # show slide on screen
                makeMove(mainBoard, slideTo)
                allMoves.append(slideTo)  # record the slide
            pygame.display.update()
            FPSCLOCK.tick(FPS)


    def getStartingBoard():
        # Return a board data structure with tiles in the solved state.
        # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
        # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
        counter = 1
        board = []
        for x in range(BOARDWIDTH):
            column = []
            for y in range(BOARDHEIGHT):
                column.append(counter)
                counter += BOARDWIDTH
            board.append(column)
            counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

        board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = BLANK
        return board

    def getBlankPosition(board):
        # Return the x and y of board coordinates of the blank space.
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == BLANK:
                    return (x, y)

    def makeMove(board, move):
        # This function does not check if the move is valid.
        blankx, blanky = getBlankPosition(board)

        if move == UP:
            board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
        elif move == DOWN:
            board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
        elif move == LEFT:
            board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
        elif move == RIGHT:
            board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

    def isValidMove(board, move):
        blankx, blanky = getBlankPosition(board)
        return (move == UP and blanky != len(board[0]) - 1) or \
               (move == DOWN and blanky != 0) or \
               (move == LEFT and blankx != len(board) - 1) or \
               (move == RIGHT and blankx != 0)

    def getRandomMove(board, lastMove=None):
        # start with a full list of all four moves
        validMoves = [UP, DOWN, LEFT, RIGHT]

        # remove moves from the list as they are disqualified
        if lastMove == UP or not isValidMove(board, DOWN):
            validMoves.remove(DOWN)
        if lastMove == DOWN or not isValidMove(board, UP):
            validMoves.remove(UP)
        if lastMove == LEFT or not isValidMove(board, RIGHT):
            validMoves.remove(RIGHT)
        if lastMove == RIGHT or not isValidMove(board, LEFT):
            validMoves.remove(LEFT)

        # return a random move from the list of remaining moves
        return random.choice(validMoves)

    def getLeftTopOfTile(tileX, tileY):
        left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
        top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
        return (left, top)

    def getSpotClicked(board, x, y):
        # from the x & y pixel coordinates, get the x & y board coordinates
        for tileX in range(len(board)):
            for tileY in range(len(board[0])):
                left, top = getLeftTopOfTile(tileX, tileY)
                tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
                if tileRect.collidepoint(x, y):
                    return (tileX, tileY)
        return (None, None)

    def drawTile(tilex, tiley, number, adjx=0, adjy=0):
        # draw a tile at board coordinates tilex and tiley, optionally a few
        # pixels over (determined by adjx and adjy)
        left, top = getLeftTopOfTile(tilex, tiley)
        pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
        textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)

    def makeText(text, color, bgcolor, top, left):
        # create the Surface and Rect objects for some text.
        textSurf = BASICFONT.render(text, True, color, bgcolor)
        textRect = textSurf.get_rect()
        textRect.topleft = (top, left)
        return (textSurf, textRect)

    def drawBoard(board, message):
        DISPLAYSURF.fill(BGCOLOR)
        if message:
            textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
            DISPLAYSURF.blit(textSurf, textRect)

        for tilex in range(len(board)):
            for tiley in range(len(board[0])):
                if board[tilex][tiley]:
                    drawTile(tilex, tiley, board[tilex][tiley])

        left, top = getLeftTopOfTile(0, 0)
        width = BOARDWIDTH * TILESIZE
        height = BOARDHEIGHT * TILESIZE
        pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

        DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

    def slideAnimation(board, direction, message, animationSpeed):
        # Note: This function does not check if the move is valid.

        blankx, blanky = getBlankPosition(board)
        if direction == UP:
            movex = blankx
            movey = blanky + 1
        elif direction == DOWN:
            movex = blankx
            movey = blanky - 1
        elif direction == LEFT:
            movex = blankx + 1
            movey = blanky
        elif direction == RIGHT:
            movex = blankx - 1
            movey = blanky

        # prepare the base surface
        drawBoard(board, message)
        baseSurf = DISPLAYSURF.copy()
        # draw a blank space over the moving tile on the baseSurf Surface.
        moveLeft, moveTop = getLeftTopOfTile(movex, movey)
        pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

        for i in range(0, TILESIZE, animationSpeed):
            # animate the tile sliding over

            DISPLAYSURF.blit(baseSurf, (0, 0))
            if direction == UP:
                drawTile(movex, movey, board[movex][movey], 0, -i)
            if direction == DOWN:
                drawTile(movex, movey, board[movex][movey], 0, i)
            if direction == LEFT:
                drawTile(movex, movey, board[movex][movey], -i, 0)
            if direction == RIGHT:
                drawTile(movex, movey, board[movex][movey], i, 0)

            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def generateNewPuzzle(numSlides):
        # From a starting configuration, make numSlides number of moves (and
        # animate these moves).
        sequence = []
        board = getStartingBoard()
        drawBoard(board, '')
        pygame.display.update()
        pygame.time.wait(500)  # pause 500 milliseconds for effect
        lastMove = None
        for i in range(numSlides):
            move = getRandomMove(board, lastMove)
            slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=int(TILESIZE / 3))
            makeMove(board, move)
            sequence.append(move)
            lastMove = move
        return (board, sequence)

    def resetAnimation(board, allMoves):
        # make all of the moves in allMoves in reverse.
        revAllMoves = allMoves[:]  # gets a copy of the list
        revAllMoves.reverse()

        for move in revAllMoves:
            if move == UP:
                oppositeMove = DOWN
            elif move == DOWN:
                oppositeMove = UP
            elif move == RIGHT:
                oppositeMove = LEFT
            elif move == LEFT:
                oppositeMove = RIGHT
            slideAnimation(board, oppositeMove, '', animationSpeed=int(TILESIZE / 2))
            makeMove(board, oppositeMove)

    main()

def dragpuzzle():
    ####################################
    ####################################
    # init
    ####################################
    def init(data, canvas):
        data.mode = "intro"
        data.prevmode = "intro"
        ############################################################################
        # Intro Screen
        loadBackground(data, canvas)
        ############################################################################
        # Animation
        loadAnim1(data, canvas)
        loadAnim2(data, canvas)
        loadAnim3(data, canvas)
        loadAnim4(data, canvas)

        # Animation location
        data.Anim1X1, data.Anim1Y1 = 100, 110
        data.Anim2X1, data.Anim2Y1 = 110, data.height - 100
        data.Anim3X1, data.Anim3Y1 = data.width - 110, 110
        data.Anim4X1, data.Anim4Y1 = data.width - 100, data.height - 100

        # animation sliding speed
        data.Anim1dx, data.Anim4dx, data.Anim3dy, data.Anim2dy = 4, 4, 4, 4
        ############################################################################
        # Help
        data.helpRadius = 25
        data.margin = 50
        data.helpCx = data.width - data.margin
        data.helpCy = data.height - data.margin

        data.introBuildX1 = data.width / 2 - 100
        data.introBuildX2 = data.width / 2 + 150
        data.introBuildY1 = data.height / 2 + 50
        data.introBuildY2 = data.height / 2 + 100

        ############################################################################
        # Constructor
        loadConBackground(data, canvas)
        data.step = 150
        data.easyX1 = data.width / 3 - 50
        data.easyX2 = data.width / 3 + 50
        data.easyY1 = data.height / 2 - 25 + 100
        data.easyY2 = data.height / 2 + 25 + 100

        data.hardX1 = data.width * 2 / 3 - 50
        data.hardX2 = data.width * 2 / 3 + 50
        data.hardY1 = data.height / 2 - 25 + 100
        data.hardY2 = data.height / 2 + 25 + 100

        data.medX1 = data.width / 2 - 50
        data.medX2 = data.width / 2 + 50
        data.medY1 = data.height / 2 - 25 + 100
        data.medY2 = data.height / 2 + 25 + 100

        data.nextX1, data.nextY1 = data.width / 2 - 50, data.height - 90
        data.nextX2, data.nextY2 = data.width / 2 + 50, data.height - 50
        data.level = 0
        data.photo = 0
        # The resized image on the left of the screen
        data.finalImg = None
        # The puzzle cut into pieces
        data.finalPuzzle = None
        loadImg1(data, canvas)
        loadImg2(data, canvas)
        loadImg3(data, canvas)
        data.img1X1, data.img1X2 = 70, 170 + 70
        data.img1Y1, data.img1Y2 = 70, 70 + 106

        data.img2X1, data.img2X2 = 270, 270 + 170
        data.img2Y1, data.img2Y2 = 70, 70 + 119

        data.img3X1, data.img3X2 = 470, 470 + 170
        data.img3Y1, data.img3Y2 = 70, 70 + 127

        data.countPressed = 0

        data.buttonX1, data.buttonY1 = data.width / 2 + 90, 240
        data.buttonX2, data.buttonY2 = data.width / 2 + 180, 280

        ###########################################################################
        # Puzzle
        loadPuzzle1(data, canvas)
        loadPuzzle2(data, canvas)
        loadPuzzle3(data, canvas)
        data.piecesMade = False
        data.definedPiece = []
        data.dashboardX0 = 250
        data.dashboardY0 = 50
        data.selectBool = False
        data.pieceSelected = None

        data.timer = 0

        # After the game is won
        data.solvedX1 = data.width / 2 - 60
        data.solvedY1 = data.height / 2 + 150
        data.solvedX2 = data.width / 2 + 60
        data.solvedY2 = data.height / 2 + 185

        # Hint Box
        data.hintX1 = 30
        data.hintY1 = 190
        data.hintX2 = 100
        data.hintY2 = 220
        data.hintPiece = None
        data.hintColor = "red"

        ############################################################################
        # Solver
        data.solved = False
        data.solverFinal = None
        data.solverShuffled = None

    ####################################
    # mode dispatcher
    ####################################

    def mousePressed(event, data, canvas):
        if (data.mode == "intro"):
            introMousePressed(event, data)
        elif (data.mode == "constructor"):
            constructorMousePressed(event, data, canvas)
        elif (data.mode == "puzzle"):
            puzzleMousePressed(event, data, canvas)

    def keyPressed(event, data):
        if (data.mode == "intro"):
            introKeyPressed(event, data)
        elif (data.mode == "constructor"):
            constructorKeyPressed(event, data)
        elif (data.mode == "puzzle"):
            puzzleKeyPressed(event, data)

    def mouseMotion(canvas, event, data):
        if (data.mode == "puzzle"): puzzleMouseMotion(canvas, event, data)

    def mouseRelease(canvas, event, data):
        if (data.mode == "puzzle"): puzzleMouseRelease(canvas, event, data)

    def timerFired(data):
        if (data.mode == "intro"):
            introTimerFired(data)
        elif (data.mode == "constructor"):
            constructorTimerFired(data)
        elif (data.mode == "puzzle"):
            puzzleTimerFired(data)

    def redrawAll(canvas, data):
        if (data.mode == "intro"):
            introRedrawAll(canvas, data)
        elif (data.mode == "constructor"):
            constructorRedrawAll(canvas, data)
        elif (data.mode == "puzzle"):
            puzzleRedrawAll(canvas, data)

    ####################################
    # intro mode
    ####################################

    # Loading the Animations
    def loadBackground(data, canvas):
        filename = "background1.jpg"
        data.background = PhotoImage(file=filename, master=canvas)

    def loadAnim1(data, canvas):
        filename = "introAnim1.gif"
        data.Anim1 = PhotoImage(file=filename, master=canvas)

    def loadAnim2(data, canvas):
        filename = "introAnim1.gif"
        data.Anim2 = PhotoImage(file=filename, master=canvas)

    def loadAnim3(data, canvas):
        filename = "introAnim1.gif"
        data.Anim3 = PhotoImage(file=filename, master=canvas)

    def loadAnim4(data, canvas):
        filename = "introAnim1.gif"
        data.Anim4 = PhotoImage(file=filename, master=canvas)

    def getDistance(x1, x2, y1, y2):
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    def introMousePressed(event, data):
        # If the mouse was pressed on buttons
        if (data.introBuildX1 < event.x < data.introBuildX2 and
                data.introBuildY1 < event.y < data.introBuildY2):
            data.mode = "constructor"

    def introKeyPressed(event, data):
        pass

    def introTimerFired(data):
        # Dictates the direction of the animations
        sign = sign2 = sign3 = sign4 = -1
        if data.Anim1X1 + 100 >= data.width or data.Anim1X1 - 90 <= 0:
            data.Anim1dx *= sign
        data.Anim1X1 += data.Anim1dx
        if data.Anim2Y1 + 70 >= data.height or data.Anim2Y1 - 100 <= 0:
            data.Anim2dy *= sign2
        data.Anim2Y1 += data.Anim2dy
        if data.Anim3Y1 + 70 >= data.height or data.Anim3Y1 - 100 <= 0:
            data.Anim3dy *= sign3
        data.Anim3Y1 += data.Anim3dy
        if data.Anim4X1 + 100 >= data.width or data.Anim4X1 - 90 <= 0:
            data.Anim4dx *= sign4
        data.Anim4X1 += data.Anim4dx

    # Draws the Constructor (Helper Function)
    def drawConstructor(canvas, data):
        canvas.create_rectangle(data.introBuildX1, data.introBuildY1,
                                data.introBuildX2, data.introBuildY2, fill="orange",
                                outline="brown", width=3)

        canvas.create_text(data.width / 2 - 70, data.height / 2 + 60, anchor=NW,
                           text="Drag & Drop", font="courier 20 bold")
    #
    def drawAnimations(canvas, data):
        canvas.create_image(data.Anim1X1, data.Anim1Y1, image=data.Anim1)
        canvas.create_image(data.Anim2X1, data.Anim2Y1, image=data.Anim2)
        canvas.create_image(data.Anim3X1, data.Anim3Y1, image=data.Anim3)
        canvas.create_image(data.Anim4X1, data.Anim4Y1, image=data.Anim4)

    def introRedrawAll(canvas, data):
        canvas.create_image(data.width / 2, data.height / 2, image=data.background)
        drawAnimations(canvas, data)
        canvas.create_text(data.width / 2, data.height / 2 - 20,
                           text="Puzzle Mania", fill="brown", font="courier 35 bold")
        #### Buttons #####
        # Constructor
        drawConstructor(canvas, data)

    ####################################
    # constructor mode
    ####################################
    # from tkinter import filedialog

    def loadConBackground(data, canvas):
        filename = "background1.jpg"
        data.conBack = PhotoImage(file=filename, master=canvas)

    # Draws an outline for a selection (Helper Function)
    def drawOutline(x1, y1, x2, y2, canvas):
        canvas.create_rectangle(x1, y1, x2, y2, fill=None, outline="red",
                                width=3)

    # Draws an outline around the level selected (Helper Function)
    def drawLevelOutline(data, canvas):
        if data.level == 1:
            drawOutline(data.easyX1, data.easyY1, data.easyX2, data.easyY2, canvas)
        elif data.level == 2:
            drawOutline(data.medX1, data.medY1, data.medX2, data.medY2, canvas)
        elif data.level == 3:
            drawOutline(data.hardX1, data.hardY1, data.hardX2, data.hardY2, canvas)

    # Draws an outline around the picture from the picture library selected
    def drawPhotoOutline(data, canvas):
        if data.photo == 1:
            drawOutline(data.img1X1, data.img1Y1, data.img1X2, data.img1Y2, canvas)

        elif data.photo == 2:
            drawOutline(data.img2X1, data.img2Y1, data.img2X2, data.img2Y2, canvas)

        elif data.photo == 3:
            drawOutline(data.img3X1, data.img3Y1, data.img3X2, data.img3Y2, canvas)

    # Draws the back button
    def drawBack(canvas, data):
        canvas.create_oval(data.helpCx - data.helpRadius, data.helpCy - data.helpRadius,
                           data.helpCx + data.helpRadius, data.helpCy + data.helpRadius, fill="red",
                           outline="Black", width=2)

        canvas.create_text(data.helpCx, data.helpCy, text="Back",
                           font="Arial 15")

    # Checks the level selected
    def checkLevelSelect(event, data, canvas):
        if (data.easyX1 < event.x < data.easyX2 and
                data.easyY1 < event.y < data.easyY2):
            # step value for piece size
            data.step = 150
            data.level = 1

        elif (data.medX1 < event.x < data.medX2 and
              data.medY1 < event.y < data.medY2):
            # step value for piece size
            data.step = 100
            data.level = 2

        elif (data.hardX1 < event.x < data.hardX2 and
              data.hardY1 < event.y < data.hardY2):
            # step value for piece size
            data.step = 80
            data.level = 3

    # Checks the photo selected
    def checkPhotoSelect(event, data, canvas):
        if (data.img1X1 < event.x < data.img1X2 and
                data.img1Y1 < event.y < data.img1Y2):
            data.photo = 1
            data.finalImg = data.img1

        elif (data.img2X1 < event.x < data.img2X2 and
              data.img2Y1 < event.y < data.img2Y2):
            data.photo = 2
            data.finalImg = data.img2

        elif (data.img3X1 < event.x < data.img3X2 and
              data.img3Y1 < event.y < data.img3Y2):
            data.photo = 3
            data.finalImg = data.img3


    def checkButtonPressed(event, data, canvas):
        if (data.buttonX1 < event.x < data.buttonX2 and
                data.buttonY1 < event.y < data.buttonY2):
            data.countPressed += 1

    def constructorMousePressed(event, data, canvas):
        checkLevelSelect(event, data, canvas)
        checkPhotoSelect(event, data, canvas)
        if data.countPressed == 0:
            checkButtonPressed(event, data, canvas)
        if (data.nextX1 - 60 < event.x < data.nextX2 - 60 and
                data.nextY1 < event.y < data.nextY2):
            data.mode = "puzzle"
        elif (getDistance(event.x, data.helpCx, event.y, data.helpCy)
              <= data.helpRadius):
            init(data, canvas)
            data.mode = "intro"

    # Loading the images in the picture library
    def loadImg1(data, canvas):
        filename = "puzzle1_170.gif"
        data.img1 = PhotoImage(file=filename, master=canvas)

    def loadImg2(data, canvas):
        filename = "puzzle2_170.gif"
        data.img2 = PhotoImage(file=filename, master=canvas)

    def loadImg3(data, canvas):
        filename = "puzzle3_170.gif"
        data.img3 = PhotoImage(file=filename, master=canvas)



    # Draws the picture library
    def drawImages(canvas, data):
        canvas.create_image(data.width / 2, data.height / 2, image=data.conBack)
        canvas.create_image(70, 70, anchor=NW, image=data.img1)
        canvas.create_image(270, 70, anchor=NW, image=data.img2)
        canvas.create_image(470, 70, anchor=NW, image=data.img3)

    def constructorKeyPressed(event, data):
        pass

    def constructorTimerFired(data):
        pass

    # Draws levels
    def drawLevels(canvas, data):
        canvas.create_rectangle(data.easyX1, data.easyY1,
                                data.easyX2, data.easyY2, fill="orange",
                                outline="brown", width=3)
        canvas.create_rectangle(data.medX1, data.medY1,
                                data.medX2, data.medY2, fill="orange",
                                outline="brown", width=3)
        canvas.create_rectangle(data.hardX1, data.hardY1,
                                data.hardX2, data.hardY2, fill="orange",
                                outline="brown", width=3)
        canvas.create_text(data.width / 2, data.height / 2 + 40,
                           text="Pick a level.", font="Arial 17 bold")
        canvas.create_text(data.easyX1 + 20, data.easyY1 + 15, anchor=NW,
                           text="Easy", font="courier 18 bold")
        canvas.create_text(data.medX1 + 7, data.medY1 + 15, anchor=NW,
                           text="Medium", font="courier 18 bold")
        canvas.create_text(data.hardX1 + 20, data.hardY1 + 15, anchor=NW,
                           text="Hard", font="courier 18 bold")

    def drawNext(canvas, data):
        data.gridX1 = data.nextX1 + 60
        data.gridY1 = data.nextY1
        data.gridX2 = data.nextX2 + 60
        data.gridY2 = data.nextY2

        canvas.create_rectangle(data.nextX1 - 60, data.nextY1,
                                data.nextX2 - 60, data.nextY2, fill="green", outline="black",
                                width=3)
        canvas.create_text(data.width / 2 - 100, data.height - 85, anchor=NW,
                           text="Puzzle", font="courier 18 bold")

    def constructorRedrawAll(canvas, data):
        canvas.create_image(data.width / 2, data.height / 2, image=data.conBack)
        # Images
        drawImages(canvas, data)
        drawPhotoOutline(data, canvas)
        # Levels
        drawLevels(canvas, data)
        drawLevelOutline(data, canvas)
        # Go back option
        drawBack(canvas, data)
        # Next
        drawNext(canvas, data)


    ####################################
    # Puzzle mode
    ####################################

    # Piece Class
    class piece(object):
        # Initializing the piece object with its dimensions, current
        # position and final position
        def __init__(self, image, dimensions, finalPos, currPos):
            self.image = image
            self.dimension = dimensions  # (x1, y1, x2, y2)
            self.width = self.dimension[2] - self.dimension[0]
            self.height = self.dimension[3] - self.dimension[1]
            self.finalPos = finalPos
            self.fx1 = finalPos[0]
            self.fy1 = finalPos[1]
            self.fx2 = finalPos[2]
            self.fy2 = finalPos[3]

            self.currPos = currPos
            self.cx1 = currPos[0]
            self.cy1 = currPos[1]
            self.cx2 = self.cx1 + (self.width)
            self.cy2 = self.cy1 + (self.height)

        # Checks whether a point is contained in the dimensions of a piece
        def containsPoint(self, x, y):
            return (self.cx1 < x < self.cx2 and self.cy1 < y < self.cy2)

        def changePos(self, dx, dy):
            self.cx1 = dx
            self.cy1 = dy
            self.cx2 = dx
            self.cy2 = dy

        # Draws the piece at the current position
        def draw(self, canvas):
            canvas.create_image(self.cx1, self.cy1, anchor=NW, image=self.image)

    # Checking the final image and setting final puzzle to be cut to the x2.5 image
    def checkPuzzleImage(data, canvas):
        if data.finalImg == data.img1:
            data.puzzleName = "puzzle1_170.gif"
            data.puzzle = data.puzzle1

        elif data.finalImg == data.img2:
            data.puzzleName = "puzzle2_170.gif"
            data.puzzle = data.puzzle2

        elif data.finalImg == data.img3:
            data.puzzleName = "puzzle3_170.gif"
            data.puzzle = data.puzzle3
        else:
            data.puzzle = data.finalImg

    # Loading the Puzzle Images
    def loadPuzzle1(data, canvas):
        filename = "puzzle1_170.gif"
        data.puzzle1 = PhotoImage(file=filename, master=canvas)

    def loadPuzzle2(data, canvas):
        filename = "puzzle2_170.gif"
        data.puzzle2 = PhotoImage(file=filename, master=canvas)

    def loadPuzzle3(data, canvas):
        filename = "puzzle3_170.gif"
        data.puzzle3 = PhotoImage(file=filename, master=canvas)

    # Helper Functions for Redrawall
    def displayDashboard(canvas, data):
        canvas.create_text(250, 20, anchor=NW, text="Dashboard",
                           fill="white", font="Arial 15 bold")
        imgWidth = data.finalImg.width()
        imgHeight = data.finalImg.height()
        data.dashboardX0 = 250
        data.dashboardY0 = 50
        canvas.create_rectangle(data.dashboardX0, data.dashboardY0,
                                data.dashboardX0 + imgWidth * 2.5, data.dashboardY0 + imgHeight * 2.5,
                                fill=None, outline="white", width=4)

    def displayFinalPuzzle(canvas, data):
        canvas.create_text(30, 20, anchor=NW, text="Final Image",
                           font="Arial 15 bold")
        canvas.create_image(30, 50, anchor=NW, image=data.finalImg)

    def giveHint(data, canvas):
        for piece in data.definedPiece:
            if piece.cx1 != piece.fx1 or piece.cy1 != piece.fy1:
                # print("Hi")
                data.hintPiece = piece
                return

    def drawHintPiece(data, canvas):
        if (data.hintPiece != None and (data.hintPiece.cx1 != data.hintPiece.fx1 or
                                        data.hintPiece.cy1 != data.hintPiece.cy2)):
            Piece = data.hintPiece
            canvas.create_rectangle(Piece.cx1, Piece.cy1, Piece.cx2,
                                    Piece.cy2, fill=None, outline="green", width=3)
            canvas.create_rectangle(Piece.fx1, Piece.fy1, Piece.fx2,
                                    Piece.fy2, fill=None, outline="green", width=3)

    def puzzleMouseRelease(canvas, event, data):
        if data.selectBool == True:
            currPiece = data.pieceSelected
            if (currPiece.fx1 < event.x < currPiece.fx2 and
                    currPiece.fy1 < event.y < currPiece.fy2):
                if currPiece == data.hintPiece:
                    data.hintPiece = None
                # print("Hi")
                currPiece.cx1 = currPiece.fx1
                currPiece.cy1 = currPiece.fy1
                currPiece.cx2 = currPiece.cx1 + currPiece.width
                currPiece.cy2 = currPiece.cy1 + currPiece.height
            else:
                currPiece.cx1 = event.x - 20
                currPiece.cy1 = event.y - 20
                currPiece.cx2 = currPiece.cx1 + currPiece.width
                currPiece.cy2 = currPiece.cy1 + currPiece.height
            data.selectBool = False

    def puzzleMouseMotion(canvas, event, data):
        if data.selectBool == True:
            currPiece = data.pieceSelected
            currPiece.cx1 = event.x - 20
            currPiece.cy1 = event.y - 20
            currPiece.cx2 = currPiece.cx1 + currPiece.width
            currPiece.cy2 = currPiece.cy1 + currPiece.height

    def puzzleMousePressed(event, data, canvas):
        if (getDistance(event.x, data.helpCx, event.y, data.helpCy)
                <= data.helpRadius):
            init(data, canvas)
            data.mode = "constructor"

            # Check for mouse press on hint button
        if (data.hintX1 < event.x < data.hintX2 and data.hintY1 < event.y < data.hintY2):
            giveHint(data, canvas)

        # After the puzzle is solved
        if data.solved == True:
            if (data.solvedX1 < event.x < data.solvedX2 and data.solvedY1 <
                    event.y < data.solvedY2):
                init(data, canvas)
                data.mode = "constructor"

        # Moving the pieces

        if data.selectBool == True:
            currPiece = data.pieceSelected
            if (currPiece.fx1 < event.x < currPiece.fx2 and
                    currPiece.fy1 < event.y < currPiece.fy2):
                if currPiece == data.hintPiece:
                    data.hintPiece = None
                currPiece.cx1 = currPiece.fx1
                currPiece.cy1 = currPiece.fy1
                currPiece.cx2 = currPiece.cx1 + currPiece.width
                currPiece.cy2 = currPiece.cy1 + currPiece.height

            else:
                currPiece.cx1 = event.x - 20
                currPiece.cy1 = event.y - 20
                currPiece.cx2 = currPiece.cx1 + currPiece.width
                currPiece.cy2 = currPiece.cy1 + currPiece.height
            data.selectBool = False

        # else:
        for piece in data.definedPiece:
            # Drag
            if piece.containsPoint(event.x, event.y):
                if piece.cx1 != piece.fx1 or piece.cy1 != piece.fy1:
                    # print(piece.dimension)
                    data.selectBool = True
                    data.pieceSelected = piece

    def makePieces(data, canvas):
        data.piecesMade = True
        data.puzzleWidth = data.puzzle.width()
        data.puzzleHeight = data.puzzle.height()
        stepHor, stepVer = data.step, data.step
        # A 2D list containing tuples with the coordinate points of the pieces
        data.allPieces = []
        # Creates a new folder to store the images
        newpath = "C:\\Users\\nites\\PycharmProjects\\pythonProject\\final_year_project\\termproject\\Project Source Files and Support Files\\puzzlePieces"
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        height = data.puzzleHeight
        width = data.puzzleWidth
        for y in range(0, height, stepVer):
            heights = []
            for x in range(0, width, stepHor):
                if (y + stepVer > height and x + stepHor > width):
                    heights.append((x, y, width, height))
                elif (y + stepVer > height):
                    heights.append((x, y, x + stepHor, height))
                elif (x + stepHor > width):
                    heights.append((x, y, width, y + stepVer))
                else:
                    heights.append((x, y, x + stepHor, y + stepVer))
            data.allPieces.append(heights)
        rows, cols = len(data.allPieces), len(data.allPieces[0])
        picNum = 1
        for row in range(rows):
            for col in range(cols):
                x1, y1, x2, y2 = data.allPieces[row][col]
                finalPosition = (x1 + 250, y1 + 50, x2 + 250, y2 + 50)
                x = random.randint(20, data.width - 150)
                y = random.randint(380, data.height - 150)
                currPosition = (x, y)
                # dashboardPos[picNum] = (x1, y1, x2, y2)
                img = Image.open(data.puzzleName)
                pieceImg = img.crop(data.allPieces[row][col])
                picName = "C:\\Users\\nites\\PycharmProjects\\pythonProject\\final_year_project\\termproject\\Project Source Files and Support Files\\puzzlePieces\\img%d.gif" % picNum
                pieceImg.save(picName)
                pieceImport = PhotoImage(file=picName, master=canvas)
                picNum += 1
                data.definedPiece.append(piece(pieceImport, data.allPieces[row][col], finalPosition, currPosition))

    def drawPieces(data, canvas):
        for piece in data.definedPiece:
            piece.draw(canvas)

    # Checks whether each piece's current position is the same as the final position
    def checkForWin(canvas, data):
        for piece in data.definedPiece:
            if piece.cx1 != piece.fx1 or piece.cy1 != piece.fy1:
                return
        textmsg = random.choice(["Good job!"])
        data.solved = True
        canvas.create_text(data.width / 2, data.height / 2 + 85, text=textmsg,
                           font="courier 45 bold", fill="brown")
        gameTime = "Time: " + str(str(time.strftime("%M:%S", time.gmtime(data.timer // 1000))))
        canvas.create_text(data.width / 2, data.height / 2 + 130, text=gameTime,
                           font="courier 15 bold")
        canvas.create_rectangle(data.solvedX1, data.solvedY1,
                                data.solvedX2, data.solvedY2, fill="green",
                                width=2)
        canvas.create_text(data.width / 2 - 53, data.height / 2 + 155,
                           text="Solve more!", anchor=NW,
                           font="courier 13 bold", fill="black")

    def drawOutlineCurrPiece(canvas, data):
        if data.pieceSelected == None:
            return
        elif data.selectBool == True:
            curr = data.pieceSelected
            canvas.create_rectangle(curr.cx1, curr.cy1, curr.cx2, curr.cy2,
                                    fill=None, outline="red", width=2)

    def drawHint(canvas, data):
        canvas.create_rectangle(data.hintX1, data.hintY1, data.hintX2,
                                data.hintY2, fill="green", outline="black", width=2)
        canvas.create_text(data.hintX1 + 10, data.hintY1 + 5, text="Hint", anchor=NW,
                           font="courier 15 ", fill="black")

    def drawTimer(data, canvas):
        gameTime = "Time: " + str(str(time.strftime("%M:%S", time.gmtime(data.timer // 1000))))
        canvas.create_text(data.width - 30, 20, anchor=NE, text=gameTime, font="Arial 13 bold",
                           fill="white")

    def puzzleRedrawAll(canvas, data):
        canvas.create_image(data.width / 2, data.height / 2 + 100, image=data.background)
        # Puzzle
        checkPuzzleImage(data, canvas)
        if data.piecesMade == False:
            makePieces(data, canvas)
        drawPieces(data, canvas)
        # Display
        displayFinalPuzzle(canvas, data)
        drawBack(canvas, data)
        displayDashboard(canvas, data)
        drawOutlineCurrPiece(canvas, data)
        drawHint(canvas, data)
        drawHintPiece(data, canvas)
        drawTimer(data, canvas)
        checkForWin(canvas, data)

    def puzzleKeyPressed(event, data):
        pass

    def puzzleTimerFired(data):
        if data.solved == False:
            data.timer += 100

    ####################################
    # use the run function as-is
    ####################################

    def run(width=300, height=300):
        def redrawAllWrapper(canvas, data):
            canvas.delete(ALL)
            canvas.create_rectangle(0, 0, data.width, data.height,
                                    fill='white', width=0)
            redrawAll(canvas, data)
            canvas.update()

        def mousePressedWrapper(event, canvas, data):
            mousePressed(event, data, canvas)
            redrawAllWrapper(canvas, data)

        ################################################################################
        # Drag and Drop
        ################################################################################
        # Mouse Motion
        def mouseMotionWrapper(event, canvas, data):
            mouseMotion(canvas, event, data)
            redrawAllWrapper(canvas, data)

        # Mouse Release
        def mouseReleaseWrapper(event, canvas, data):
            mouseRelease(canvas, event, data)
            redrawAllWrapper(canvas, data)

        # Mouse Double Click
        # def mouseDoubleClickWrapper(event, canvas, data):
        #    mouseDoubleClick(canvas, event, data)
        #    redrawAllWrapper(canvas, data)
        ################################################################################
        def keyPressedWrapper(event, canvas, data):
            keyPressed(event, data)
            redrawAllWrapper(canvas, data)

        def timerFiredWrapper(canvas, data):
            timerFired(data)
            redrawAllWrapper(canvas, data)
            # pause, then call timerFired again
            canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

        # Set up data and call init
        class Struct(object): pass

        data = Struct()
        data.width = width
        data.height = height
        data.timerDelay = 100  # milliseconds
        # create the root and the canvas
        root = Tk()
        root.title("Drag & Drop")
        canvas = Canvas(root, width=data.width, height=data.height)
        canvas.pack()
        init(data, canvas)
        # set up events
        root.bind("<Button-1>", lambda event:
        mousePressedWrapper(event, canvas, data))
        root.bind("<Key>", lambda event:
        keyPressedWrapper(event, canvas, data))
        root.bind("<B1-Motion>", lambda event:
        mouseMotionWrapper(event, canvas, data))
        root.bind("<ButtonRelease-1>", lambda event:
        mouseReleaseWrapper(event, canvas, data))

        timerFiredWrapper(canvas, data)
        # and launch the app
        # root.mainloop()  # blocks until window is closed
        print("bye!")

    run(700, 600)



def puzzle_mania():


    bg = PhotoImage(file="background1.jpg")
    label1 = Label(rootf, image=bg)
    label1.place(x=0, y=0)

    label2=Label(rootf,text="Choose Your Favorite Game",font=("comicsansms",32),bg="gray")
    label2.place(x=150,y=100)



    drag_puzzle = Button(rootf, text="Drag Puzzle", bg="gray", padx=30, pady=30, borderwidth=4, font=26 ,command=dragpuzzle)
    memory_Puzzle = Button(rootf, text="Memory Puzzle", bg="gray", padx=30, pady=30, borderwidth=4, font=26,
                           command=startmemory)
    number_Puzzle = Button(rootf, text="Number Puzzle", bg="gray", padx=30, pady=30, borderwidth=4, font=26,
                           command=startnumber)

    drag_puzzle.place(x=170,y=250)
    memory_Puzzle.place(x=450,y=250)
    number_Puzzle.place(x=300,y=450)
    rootf.mainloop()

if __name__ == '__main__':
    rootf = Tk()
    rootf.title("Puzzle Mania")
    rootf.geometry("830x800")

    puzzle_mania()