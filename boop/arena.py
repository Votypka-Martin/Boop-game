from player import Player as Player1
from player2 import Player as Player2
import base as BASE
import os
import random


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def random_board():
    board = [[0] * 6 for _ in range(6)]
    random_pos = []
    token = 1
    for i in range(4):
        row = random.randint(0, 5)
        col = random.randint(0, 5)
        while (row, col) in random_pos:
            row = random.randint(0, 5)
            col = random.randint(0, 5)
        random_pos.append((row, col))
        board[row][col] = token
        token *= -1
    return board

if __name__ == "__main__":
    BASE.Base.init_gui()
    p1 = Player2("Positive player",1)     #we create two instances of your player. One for +1 color
    p2 = Player1("Negative player",-1)    #and second for the -1 color

    p1.kittens = 8                      #set up how many cats/kittens you have
    p1.cats = 0

    p2.kittens = 8                      #set this up for both player
    p2.cats = 0

    p1.otherCats = p2.cats              #these variables inform other player about your pieces
    p1.otherKittens = p2.kittens
    p2.otherCats = p1.cats
    p2.otherKittens = p1.kittens
    p1.board = random_board()
    p1.draw(p1.board, "base.png")       #draw (empty) board and save in into base.png
    moveIdx = 0                         #index of the move, also use to index images
    while True:
        
        move1 = p1.play()              #the first player is on move
        if len(move1) > 0:
            row, col, animal, newboard, triple = move1  #unpack the move
            isEnd = BASE.updatePlayer(p1,p2,newboard, row, col, animal, triple, "move-{:03d}-p1".format(moveIdx))  #update the players, and save image
            print("Move:", (row, col), "Animal:", animal, "Triple:", triple, "Kittens:", p1.kittens, "Cats:", p1.cats, "Other Kittens:", p1.otherKittens, "Other Cats:", p1.otherCats, "\n")
            p1.print_board()
            if isEnd:
                print(p1.studentName, "wins")
                break

        move2 = p2.play()               #the second player is on move
        if len(move2) > 0:
            
            row, col, animal, newboard, triple = move2  #unpack move
            isEnd = BASE.updatePlayer(p2,p1,newboard, row, col, animal, triple, "move-{:03d}-p2".format(moveIdx))
            print("Move:", (row, col), "Animal:", animal, "Triple:", triple,"Kittens:", p2.kittens, "Cats:", p2.cats, "Other Kittens:", p2.otherKittens, "Other Cats:", p2.otherCats, "\n")
            p2.print_board()
            if isEnd:
                print(p2.studentName,"wins")
                break

        if len(move1) == 0 and len(move2) == 0:
            print("Both players return []")
            break
        moveIdx += 1
        if moveIdx > 150:
            print("Maximum number of moves reached")
            break

    print("End of game")   

    if BASE.Base.stop_event is not None:
        BASE.Base.stop_event.wait()



