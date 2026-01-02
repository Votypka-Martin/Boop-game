import base as BASE
import random, copy
import time

"""
This file contains Player class, where you implement your player according the Boop rules.
To test your player, use section "if __name__ == "__main__" at the end of the file
You can run this file: python3 player.py, which should simulate a game of teo players and provide a set of png images.

However, this file does not verify if you play according to the rules or not. This functionality is on Brute only.
Anyway, if running this script produces an error, you have to fix it first before uploading to Brute.
Please do not use Brute as debugger tool :-)

"""

class TTEntry:
    def __init__(self, key, value, depth, flag):
        self.key = key
        self.value = value
        self.depth = depth
        self.flag = flag

class TranspositionTable:
    def __init__(self, bit_size):
        self.mask = (1 << bit_size) - 1
        self.table = [None] * (1 << bit_size)
    
    def __getitem__(self, key: int) -> TTEntry:
        entry = self.table[key & self.mask]
        if entry is not None and entry.key == key:
            return entry
        return None
    
    def __setitem__(self, key: int, value: TTEntry):
        index = key & self.mask
        entry = self.table[index]
        if entry is None or value.depth > entry.depth:
            self.table[index] = value

class MovePos:
    first_bit_mask = [
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,1,0,1,0],
        [0,1,1,1,0],
        [0,0,0,0,0]
    ]

    second_bit_mask = [
        [1,0,1,0,1],
        [0,0,0,0,0],
        [1,0,0,0,1],
        [0,0,0,0,0],
        [1,0,1,0,1]
    ]

    first_bit_indexes = [(1,1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)]
    second_bit_indexes = [(0, 0), (0, 2), (0, 4), (2, 0), (2, 4), (4, 0), (4, 2), (4, 4)]

    @classmethod
    def combine(cls, board, mask, index):
        board = [[0]*6 for _ in range(6)]
        dx = index % 6 - 2
        dy = index // 6 - 2
        for y in range(5):
            if y + dy < 0 or y + dy >= 6:
                continue
            for x in range(5):
                if x + dx < 0 or x + dx >= 6:
                    continue
                board[y + dy][x + dx] = mask[y][x]

        return board

    @classmethod
    def get_first_bit_mask(cls, second_bit_mask, index):
        bit_board = [[0]*6 for _ in range(6)]
        x = index % 6
        y = index // 6
        if x - 2 >= 0:
            if second_bit_mask[y][x-2] == 1: 
                bit_board[y][x-1] = 1
            if y - 2 >= 0 and second_bit_mask[y-2][x-2] == 1:
                bit_board[y-1][x-1] = 1
            if y + 2 < 6 and second_bit_mask[y+2][x-2] == 1:
                bit_board[y+1][x-1] = 1
        if x + 2 < 6:
            if second_bit_mask[y][x+2] == 1:
                bit_board[y][x+1] = 1
            if y - 2 >= 0 and second_bit_mask[y-2][x+2] == 1:
                bit_board[y-1][x+1] = 1
            if y + 2 < 6 and second_bit_mask[y+2][x+2] == 1:
                bit_board[y+1][x+1] = 1
        if y - 2 >= 0 and second_bit_mask[y-2][x] == 1:
            bit_board[y-1][x] = 1
        if y + 2 < 6 and second_bit_mask[y+2][x] == 1:
            bit_board[y+1][x] = 1

        return bit_board
    
    @classmethod
    def get_second_bit_mask(cls, first_bit_mask, index):
        bit_board = [[0]*6 for _ in range(6)]
        x = index % 6
        y = index // 6
        if x - 2 >= 0:
            if first_bit_mask[y][x-1] == 1:
                bit_board[y][x-2] = 1
            if y - 2 >= 0 and first_bit_mask[y-1][x-1] == 1:
                bit_board[y-2][x-2] = 1
            if y + 2 < 6 and first_bit_mask[y+1][x-1] == 1:
                bit_board[y+2][x-2] = 1
        if x + 2 < 6:
            if first_bit_mask[y][x+1] == 1:
                bit_board[y][x+2] = 1
            if y - 2 >= 0 and first_bit_mask[y-1][x+1] == 1:
                bit_board[y-2][x+2] = 1
            if y + 2 < 6 and first_bit_mask[y+1][x+1] == 1:
                bit_board[y+2][x+2] = 1
        if y - 2 >= 0 and first_bit_mask[y-1][x] == 1:
            bit_board[y-2][x] = 1
        if y + 2 < 6 and first_bit_mask[y+1][x] == 1:
            bit_board[y+2][x] = 1

        return bit_board

    @classmethod
    def piece_count_difference(cls, board1, board2):
        count1 = 0
        count2 = 0
        for y in range(6):
            for x in range(6):
                if board1[y][x] == 1:
                    count1 += 1
                if board2[y][x] == 1:
                    count2 += 1
        return abs(count1 - count2)
    
    @classmethod
    def to_bitboard(cls, board):
        bit_board = 0
        for y in range(6):
            for x in range(6):
                if board[y][x] == 1:
                    bit_board |= 1 << (y*6 + x)
        return bit_board
    
    @classmethod
    def bitboard_to_string(cls, bitboard):
        s = ""
        for i in range(36):
            s += str((bitboard >> i) & 1) + ("\n" if (i % 6 == 5) else "")
        return s
                

    def __init__(self, index):
        self.index = index
        self.pos = (1 << index)
        self.pos_zero = (1 << (36 - 1)) ^ self.pos
        self.create_bit_masks()

    def create_bit_masks(self):
        mask = (1 << 36) - 1
        board = [[0]*6 for _ in range(6)]
        self.first_bit_mask = MovePos.to_bitboard(MovePos.combine(board, MovePos.first_bit_mask, self.index))
        self.second_bit_mask = MovePos.to_bitboard(MovePos.combine(board, MovePos.second_bit_mask, self.index))
        self.second_bit_zero_masks = {}
        self.first_bit_shift = {}
        self.out_piece_counts = {}
        for val in range(256):
            mask1 = [[0]*5 for _ in range(5)]
            mask2 = [[0]*5 for _ in range(5)]
            for i in range(8):
                mask1[MovePos.second_bit_indexes[i][0]][MovePos.second_bit_indexes[i][1]] = (val >> i) & 1
                mask2[MovePos.first_bit_indexes[i][0]][MovePos.first_bit_indexes[i][1]] = (val >> i) & 1
            
            second_bit_mask = MovePos.combine(board, mask1, self.index)
            first_bit_mask = MovePos.combine(board, mask2, self.index)

            second_bit_board = MovePos.to_bitboard(second_bit_mask)
            first_bit_board = MovePos.to_bitboard(first_bit_mask)

            second_zero_mask = MovePos.to_bitboard(MovePos.get_first_bit_mask(second_bit_mask, self.index))
            self.second_bit_zero_masks[second_bit_board] = (~second_zero_mask) & mask
            first_bit_shift = MovePos.to_bitboard(second_bit_mask)
            self.first_bit_shift[first_bit_board] = first_bit_shift
            self.out_piece_counts[first_bit_board] = MovePos.piece_count_difference(first_bit_mask, second_bit_mask)

class Move:
    def __init__(self, move_pos: MovePos, type: int, value: int):
        self.move_pos = move_pos
        self.type = type
        self.value = value


class Player(BASE.Base):
    def __init__(self, name, player):
        BASE.Base.__init__(self, player)     #we call constructor of the Base class first. Do not remove this line
        self.studentName = name             #parameter name will be filled with Brute and it contains your login
        self.studentTag = "Boop master"
        self.__kitten_bitboard = 0                
        self.__enemy_kitten_bitboard = 0
        self.__cat_bitboard = 0
        self.__enemy_cat_bitboard = 0
        self.__zobrist_keys = [
            [
                [
                    [
                        [random.getrandbits(64) for _ in range(36)]#squares
                        for _ in range(8)#player kittens
                    ]
                    for _ in range(8)#enemy kittens
                ]
                for _ in range(2)#pieces
            ]
            for _ in range(2)#sides
        ]
        self.__move_pos = [MovePos(i) for i in range(36)]
        self.__kitten_moves = [Move(move_pos, 1, 0) for move_pos in self.__move_pos]
        self.__cat_moves = [Move(move_pos, 2, 0) for move_pos in self.__move_pos]
        self.__remove_kitten_moves = [Move(move_pos, 10, 0) for move_pos in self.__move_pos]
        self.__cat_stack_counts = {}
        self.__create_cat_stack_counts()
        

    def play(self):
        """ returns [ move, animal, newboard, triples ]
            or [] if no movement is possible.
            row: int, index of row to place the animal
            col: int, index of col to place the animal
            animal: -1 or -2 (if self.player==-1); or  1 or 2 (if self.player==1), or 10 (see later)
            newboard: deepcopy of you board with new situation AFTER placing the animal AND applying repulsion
            triples: [ [row1, col1], [row2, col2], [row3, col3] ] of triples of your color detected in the newboard.
            if no triples are detected, use [] instead.

            if animal == 10, then row,col defines cell from which you want to remove your kitten, and newboard contains situation AFTER removing the kitten
        """
        return []
    
    def test_play_move(self):    
        k, ek, c, ec = self.__play_move(self.__kitten_moves[20], 0, 0, 0, 0)
        print(MovePos.bitboard_to_string(k))
        k, ek, c, ec = self.__play_move(self.__kitten_moves[15], k, ek, c, ec)
        print(MovePos.bitboard_to_string(k))
        k, ek, c, ec = self.__play_move(self.__kitten_moves[20], k, ek, c, ec)
        print(MovePos.bitboard_to_string(k))
        k, ek, c, ec = self.__play_move(self.__kitten_moves[25], k, ek, c, ec)
        print(MovePos.bitboard_to_string(k))
        k, ek, c, ec = self.__play_move(self.__kitten_moves[20], k, ek, c, ec)
        print(MovePos.bitboard_to_string(k))

    def __create_cat_stack_counts(self):
        self.__cat_stack_counts[0] = 0
        for i in range(36):
            self.__cat_stack_counts[1 << i] = 3
        for i in range(36):
            for j in range(i + 1, 36):
                self.__cat_stack_counts[1 << i | 1 << j] = 6

    def __play(self, depth, alpha, beta, start_time, time_limit):
        pass

    def __play_enemy(self, depth, alpha, beta, start_time, time_limit):
        pass

    def __get_moves(self):
        return []
    
    def __get_enemy_moves(self):
        return []
    
    def __sort_moves(self, moves):
        return moves
    
    def __board_value(self):
        return 0

    def __play_move(self, move: Move, player_kittens_board: int, enemy_kittens_board: int, player_cats_board: int, enemy_cats_board: int):
        move_pos, type = move.move_pos, move.type
        cat_stack_counts = self.__cat_stack_counts
        first_bit_mask, second_bit_mask = move_pos.first_bit_mask, move_pos.second_bit_mask
        second_bit_zero_masks, first_bit_shift, out_piece_counts = move_pos.second_bit_zero_masks, move_pos.first_bit_shift, move_pos.out_piece_counts
        board = player_kittens_board | player_cats_board | enemy_kittens_board | enemy_cats_board
        block = second_bit_mask & board
        
        key = player_kittens_board & first_bit_mask
        second_bit_zero_mask = second_bit_zero_masks[block]
        key &= second_bit_zero_mask
        p_kittens = out_piece_counts[key]
        player_kittens_board = player_kittens_board & (~key) | first_bit_shift[key]

        key = enemy_kittens_board & first_bit_mask
        second_bit_zero_mask = second_bit_zero_masks[block]
        key &= second_bit_zero_mask
        e_kittens = out_piece_counts[key]
        enemy_kittens_board = enemy_kittens_board & (~key) | first_bit_shift[key]

        p_cats = 0
        e_cats = 0
        if type == 2:
            key = player_cats_board & first_bit_mask
            second_bit_zero_mask = second_bit_zero_masks[block]
            key &= second_bit_zero_mask
            p_cats = out_piece_counts[key]
            player_cats_board = player_cats_board & (~key) | first_bit_shift[key]

            key = enemy_cats_board & first_bit_mask
            second_bit_zero_mask = second_bit_zero_masks[block]
            key &= second_bit_zero_mask
            e_cats = out_piece_counts[key]
            enemy_cats_board = enemy_cats_board & (~key) | first_bit_shift[key]

            player_cats_board |= move_pos.pos
        else:
            player_kittens_board |= move_pos.pos

        
        p_mask, p_cat_count_key = self.__replace_kittens_masks(player_kittens_board | player_cats_board)
        e_mask, e_cat_count_key = self.__replace_kittens_masks(enemy_kittens_board | enemy_cats_board)

        if p_mask != 0:
            p_mask = ~p_mask
            p_cats += cat_stack_counts[p_cat_count_key]
            player_kittens_board &= p_mask
            player_cats_board &= p_mask

        if e_mask != 0:
            e_mask = ~e_mask
            e_cats += cat_stack_counts[e_cat_count_key]
            enemy_kittens_board &= e_mask
            enemy_cats_board &= e_mask
        
        return player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board

    
    def __replace_kittens_masks(self, board):
        hor = board & (board >> 1) & (board >> 2)
        mask1 = 0
        mask2 = 0
        if hor > 0:
            hor &= ~(hor & (hor >> 1))
            mask1 = hor | hor << 1 | hor << 2
            mask2 = hor
        else:
            ver = board & (board >> 6) & (board >> 12)
            if ver > 0:
                ver &= ~(ver & (ver >> 6))
                mask1 = ver | ver << 6 | ver << 12
                mask2 = ver
            else:
                dig1 = board & (board >> 7) & (board >> 14)
                if dig1 > 0:
                    dig1 &= ~(dig1 & (dig1 >> 7))
                    mask1 = dig1 | dig1 << 7 | dig1 << 14
                    mask2 = dig1
                else:
                    dig2 = board & (board >> 5) & (board >> 10)
                    if dig2 > 0:
                        dig2 &= ~(dig2 & (dig2 >> 5))
                        mask1 = dig2 | dig2 << 5 | dig2 << 10
                        mask2 = dig2
        return mask1, mask2           
    
    def __place_token(self, move, board):
        return board | move

    def __remove_token(self, move, board):
        return board & ~(move)
    
    def __generate_bitboards(self):
        self.__kitten_bitboard = 0
        self.__cat_bitboard = 0
        self.__enemy_kitten_bitboard = 0
        self.__enemy_cat_bitboard = 0
        i = 0
        for row in self.board:
            for cell in row:
                i += 1
                val = cell * self.player
                if val == 1:
                    self.__kitten_bitboard |= 1 << i
                elif val == 2:
                    self.__cat_bitboard |= 1 << i
                elif val == -1:
                    self.__enemy_kitten_bitboard |= 1 << i
                elif val == -2:
                    self.__enemy_cat_bitboard |= 1 << i


"""
PUT ALL YOUR TEST INTO THIS SECTION:

The simple game here assumes that you play correctly. There are no checks here if the moves are valid or not.

"""

if __name__ == "__main__":
    p1 = Player("Positive player",1)     #we create two instances of your player. One for +1 color
    p2 = Player("Negative player",-1)    #and second for the -1 color

    p1.kittens = 8                      #set up how many cats/kittens you have
    p1.cats = 0

    p2.kittens = 8                      #set this up for both player
    p2.cats = 0

    p1.otherCats = p2.cats              #these variables inform other player about your pieces
    p1.otherKittens = p2.kittens
    p2.otherCats = p1.cats
    p2.otherKittens = p1.kittens

    p1.draw(p1.board, "base.png")       #draw (empty) board and save in into base.png
    
    moveIdx = 0                         #index of the move, also use to index images
    while True:
        move1 = p1.play()               #the first player is on move
        if len(move1) > 0:
            move, animal, newboard, triple = move1  #unpack the move
            isEnd = BASE.updatePlayer(p1,p2,newboard, move, animal, triple, "move-{:03d}-p1".format(moveIdx))  #update the players, and save image
            if isEnd:
                print(p1.studentName, "wins")
                break

        move2 = p2.play()               #the second player is on move
        if len(move2) > 0:
            move, animal, newboard, triple = move2  #unpack move
            isEnd = BASE.updatePlayer(p2,p1,newboard, move, animal, triple, "move-{:03d}-p2".format(moveIdx))
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



