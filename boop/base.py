from PIL import Image, ImageDraw
import math
import copy


"""
This is Base class for the Boop player. It defines variables that will be used by all players, and some usefull methods.

DO NOT MODIFY THIS FILE. It will not be upload to Brute anyway, so your changes of this file will not work on Brute.

If you need to define your own variables and methods, do it in the constructor of Player class in player.py
"""

class Base:
    def __init__(self, player):
        self.board = [ [0]*6 for _ in range(6) ]

        self.kittens = 0            #the total number of kittens available to this player (a part can be on the board)
        self.cats = 0               #the total number of cats available to this player (a part can be on the board)
        self.otherKittens = 0       #the total number of kittens of the other player (a part can be on the board)
        self.otherCats = 0          #the total number of cats of the other player (a part can be on the board)
        self.player = player        #if I play with 1 or -1 animals
        self.timeOut = 1            #timeout for constructor and play(). Will be filled by Brute
        self.maxMoves = 100         #max moves per game. Will be filled by Brute

        self.tournament = False     #true if the player is in tournament mode (filled by Brute)
        self.studentName = "student" #will be filled by Brute
        self.studentTag = "Boopzilla" #can be filled by student in the player class

        
        self._colors = {}
        self._colors[0] = "#ffffff"     #empty cell
        self._colors[1] = "#92DCE5"     #kitten 1
        self._colors[2] = "#92DCE5"     #cat 1
        self._colors[-1] = "#F7EC59"    #kitten -1
        self._colors[-2] = "#F7EC59"    #cat -2
        self._colors[3] = "#F2542D"     
        self._colors[4] = "#562C2C"
        self._colors[5] = "#127475"

        self.cellSize = 60          #width of one cell in pixels (for making png)
        self.kitImg = Image.open("images/kit2.png").resize((self.cellSize-2, self.cellSize-2))
        self.catImg = Image.open("images/cat2.png").resize((self.cellSize-2, self.cellSize-2))

    def countAnimals(self, board):
        """ 
            return number of cats and kittens on the board in dict
        """
        animals = { -1:0, -2:0, 1:0, 2:0 }
        for row in range(len(board)):
            for col in range(len(board[row])):
                v = abs(board[row][col])
                if v == 1 or v == 2:
                    animals[ board[row][col] ] += 1
        return animals


    def inside(self, row, col):
        """
            return true of row, col is valid cell coordinates in the board 
        """
        return row >=0 and row < 6 and col >=0 and col < 6

    def checkAnimals(self):
        """ 
            return true if the number of animals on the board is less or equal to available animals
        """
        animals = self.countAnimals(self.board)
        return (animals[-1] + animals[-2] <= 8) and (animals[1] + animals[2]) <= 8


    def pool(self):
        return { self.player*1: self.kittens, self.player*2: self.cats,  -self.player*1: self.otherKittens, -self.player*2: self.otherCats }

    def draw(self, board, filename, highlight = {}, circles = {}, lines = {} ):
        """
            create .png file with the given board
            board: 2D array with values 0 (empty cell), 1 or -1 (kittens) and 2 or -2 (cats)
            filename: name of png file, must end with ".png" suffix
            highlight: key is (row,col), value is html color: this will fill cell (row,col) with the color (use html color)
            circles: key is (row, col), value is html color: this will draw circle at given cell
            lines: key is (row1, col1, row2, col2), value is html color: this will draw line from cell (row1, col1) to cell (row2, col2)

            examples of calling this method are in player.py
        """
        x0 = self.cellSize
        y0 = 0

        def getCellCoord(row, col):
            return x0+col*self.cellSize, y0+row*self.cellSize, x0+(col+1)*self.cellSize, y0+(row+1)*self.cellSize

        def getCircleCoords(row, col):
            return x0 + col*self.cellSize + self.cellSize/2, y0 + row*self.cellSize + self.cellSize/2

        def drawAnimals(kittens, cats, player):
            poolcoord = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(6,1) ]
            animals = [player*1]*kittens + [player*2]*cats
            if len(animals) > 8 or kittens < 0 or cats < 0:
                print("ERROR: You have wrong number of animals in the pool. You have: ",kittens, "kittens and",cats, "cats. This is not acceptable")
                exit()
            for i in range(len(animals)):
                y,x = poolcoord[i]
                if player == -1:
                    x = 7-x
                x *= self.cellSize
                y *= self.cellSize
                if abs(animals[i]) == 2:
                    draw.rectangle( (x,y, x+self.cellSize, y+self.cellSize) , fill=self._colors[ animals[i] ] )
                    img.paste(self.catImg,(x,y), self.catImg)
                elif abs(animals[i]) == 1:
                    draw.rectangle( (x,y, x+self.cellSize, y+self.cellSize) , fill=self._colors[ animals[i] ] )
                    img.paste(self.kitImg,(x,y), self.kitImg)
 

        width = self.cellSize*8
        height = self.cellSize*7
        img = Image.new('RGB',(width,height),"white")
        draw = ImageDraw.Draw(img)
        for row in range(len(board)):
            for col in range(len(board[row])):
                value = board[row][col] 
                draw.rectangle( getCellCoord(row, col)  , fill=self._colors[ value ] )

                if (row,col) in highlight:
                    color = highlight[(row,col)]        
                    draw.rectangle( getCellCoord(row, col)  , fill=color )

                if abs(value) == 1:
                    x,y,*_ = getCellCoord( row, col)
                    img.paste(self.kitImg,(x,y), self.kitImg)
                elif abs(value) == 2:
                    x,y,*_ = getCellCoord( row, col)
                    img.paste(self.catImg,(x,y), self.catImg)

        for cell in circles:
            row, col = cell
            x,y = getCircleCoords(row, col)
            eps = self.cellSize/4
            draw.ellipse( (x-eps, y-eps, x+eps, y+eps), fill = circles[cell], outline = 'black')

        for line in lines:
            r1, c1, r2, c2 = line
            x1,y1 = getCircleCoords(r1, c1)
            x2,y2 = getCircleCoords(r2, c2)
            draw.line((x1,y1,x2,y2), fill=lines[line], width=3)
            draw_arrow(draw, (x1,y1), (x2,y2), arrow_length=20, arrow_angle=40, fill=lines[line], width=3)

        _gridColor = "#aaaaaa"
        for i in range(1,6):
            draw.line([x0,y0+i*self.cellSize, x0+self.cellSize*6, y0+i*self.cellSize ], fill = _gridColor, width = 2)
            draw.line([x0+i*self.cellSize,0,x0+i*self.cellSize, y0+6*self.cellSize ], fill = _gridColor, width = 2)

        animalsOnBoard = self.countAnimals(board)
        drawAnimals(self.kittens - animalsOnBoard[self.player*1], self.cats - animalsOnBoard[self.player*2], self.player)
        drawAnimals(self.otherKittens - animalsOnBoard[-self.player*1], self.otherCats - animalsOnBoard[-self.player*2], -self.player)

        eps = 2
        draw.line([x0,y0+eps,  x0+self.cellSize*6,y0+eps, x0+self.cellSize*6-eps,y0 + self.cellSize*6-eps, x0, self.cellSize*6-eps, x0, y0], fill = _gridColor, width = 5 )
                
        img.save(filename)

    def printBoard(self, board):
        for row in board:
            for col in row:
                print("{:3d}".format(col), end=" ")
            print()



def copyBoard(source, destination):
    for row in range(len(source)):
        for col in range(len(source)):
            destination[row][col] = source[row][col]


def updatePlayer(activePlayer, passivePlayer, newBoard, row, col, animalPlaced, triple, filenameprefix = ""):
    """
        place animal to (row, col), and update both player. 
        activePlayer: one that makes the last move
        passivePlayer: the second player
        newBoard: copy of active playes board with new situation. this board will be copied to passive player.
        triple: cells of cats/kittens for exchanged, [ [row1, col1], [row2, col2], [row3, col3] ]
        filenameprefix: of output png files will have this pregix
    """

    copyBoard(newBoard, activePlayer.board)
    copyBoard(newBoard, passivePlayer.board)
    
    if filenameprefix != "":
        fn = "{}-a.png".format(filenameprefix)
        activePlayer.draw(activePlayer.board, fn, circles = { (row,col):"blue"} )

    animals = activePlayer.countAnimals(activePlayer.board)
    if animals[-2] == 8 or animals[2] == 8:
        return True
    
    if animalPlaced == 10:
        activePlayer.cats += 1
        activePlayer.kittens -= 1
        passivePlayer.otherCats += 1
        passivePlayer.otherKittens -= 1

    if len(triple) == 3 or animalPlaced == 10:

        if filenameprefix != "":
            fn = "{}-b.png".format(filenameprefix)
            activePlayer.draw(activePlayer.board, fn, circles = { tuple(cell):"red" for cell in triple } )


        animals = [ newBoard[ cell[0] ][ cell[1] ] for cell in triple ]
        numKittens = animals.count(1*activePlayer.player)
        numCats = animals.count(2*activePlayer.player)


        if numCats == 3:
            return True

        if (numKittens > 0) and (numCats + numKittens == 3):
            activePlayer.kittens -= numKittens
            activePlayer.cats += numKittens
        passivePlayer.otherCats = activePlayer.cats
        passivePlayer.otherKittens = activePlayer.kittens

        #remove triple from the board
        for cell in triple:
            row, col = cell
            newBoard[row][col] = 0 
        copyBoard(newBoard, activePlayer.board)
        copyBoard(newBoard, passivePlayer.board)

        if filenameprefix != "":
            fn = "{}-c.png".format(filenameprefix)
            activePlayer.draw(activePlayer.board, fn)

    return False




def draw_arrow(draw, start, end, arrow_length=10, arrow_angle=30, fill="black", width=2):
    """
        draw: ImageDraw.Draw object
        start: (x1, y1) starting point
        end: (x2, y2) ending point
        arrow_length: Length of the arrowhead sides
        arrow_angle: Angle between arrow line and arrowhead edges (degrees)
        fill: Color of the arrow
        width: Line thickness
    """
    x1, y1 = start
    x2, y2 = end
    
    # Draw the main line
    draw.line((x1, y1, x2, y2), fill=fill, width=width)

    # Compute the angle of the line
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Compute arrowhead points
    left = (
        x2 - arrow_length * math.cos(angle - math.radians(arrow_angle)),
        y2 - arrow_length * math.sin(angle - math.radians(arrow_angle))
    )
    right = (
        x2 - arrow_length * math.cos(angle + math.radians(arrow_angle)),
        y2 - arrow_length * math.sin(angle + math.radians(arrow_angle))
    )

    # Draw the arrowhead
    draw.polygon([end, left, right], fill=fill)

