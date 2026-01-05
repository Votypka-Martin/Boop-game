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
        self.default_value = value
        self.value = value
        self.boards = [[0]*4 for _ in range(20)]
        self.p_kitten_count = [0] * 20
        self.e_kitten_count = [0] * 20
        self.p_cat_count = [0] * 20
        self.e_cat_count = [0] * 20

    def set_count(self, move: Move, depth: int):
        last_depth = depth - 1
        self.p_kitten_count[depth] = move.p_kitten_count[last_depth]
        self.e_kitten_count[depth] = move.e_kitten_count[last_depth]
        self.p_cat_count[depth] = move.p_cat_count[last_depth]
        self.e_cat_count[depth] = move.e_cat_count[last_depth]
        


class Player(BASE.Base):
    def __init__(self, name, player):
        BASE.Base.__init__(self, player)     #we call constructor of the Base class first. Do not remove this line
        self.studentName = name             #parameter name will be filled with Brute and it contains your login
        self.studentTag = "Boop master"
        self.__kitten_bitboard = 0                
        self.__enemy_kitten_bitboard = 0
        self.__cat_bitboard = 0
        self.__enemy_cat_bitboard = 0
        self.__move_pos = [MovePos(i) for i in range(36)]
        self.__move_default_values = [
            1,1,1,1,1,1,
            1,5,5,5,5,1,
            1,5,7,7,5,1,
            1,5,7,7,5,1,
            1,5,5,5,5,1,
            1,1,1,1,1,1
        ]
        self.__kitten_moves = [Move(self.__move_pos[i], 1, self.__move_default_values[i]) for i in range(36)]
        self.__cat_moves = [Move(self.__move_pos[i], 2, self.__move_default_values[i]) for i in range(36)]
        self.__remove_kitten_moves = [Move(self.__move_pos[i], 10, 8 - self.__move_default_values[i]) for i in range(36)]
        self.__cat_stack_counts = {}
        self.__create_cat_stack_counts()
        self.__bit_counts = {0: 0}
        self.__create_bit_counts(3)
        self.__outer_square_mask = 0b111111100001100001100001100001111111
        self.__mid_square_mask = 0b000000011110010010010010011110000000
        self.__inner_square_mask = 0b000000000000001100001100000000000000

        self.__transposition_table = {}
        

    def play(self):
        self.__transposition_table = {}
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
        pass

    def __create_bit_counts(self, max_bit_count, pos = 0, key = 0, count = 1):
        if max_bit_count == 0 or pos == 36:
            return
        for i in range(pos, 36):
            new_key = key | 1 << i
            self.__bit_counts[new_key] = count
            self.__create_bit_counts(max_bit_count - 1, i + 1, new_key, count + 1)

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
    
    def __get_possible_moves(self, p_kittens: int, p_cats: int, board: int):
        i = 0
        moves = []
        if p_cats + p_kittens == 0:
            while i < 36:
                if board & (1 << i) > 0:
                    moves.append(self.__remove_kitten_moves[i])
                i += 1
        elif p_cats == 0:
            while i < 36:
                if board & (1 << i) == 0:
                    moves.append(self.__kitten_moves[i])
                i += 1
        elif p_kittens == 0:
            while i < 36:
                if board & (1 << i) == 0:
                    moves.append(self.__cat_moves[i])
                i += 1
        else:
            while i < 36:
                if board & (1 << i) == 0:
                    moves.append(self.__kitten_moves[i])
                    moves.append(self.__cat_moves[i])
                i += 1
        return moves

    def __sort_moves(self, moves: list[Move], last_move: Move, board, depth):
        for move in moves:
            self.__play_move(move, last_move, board, depth)
        moves.sort(key = lambda move: move.value, reverse = True)

    def __play_move(self, move: Move, last_move: Move, board: int, depth: int):
        type = move.type
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = last_move.boards[depth]
        if type == 10:
            boards = player_kittens_board & move.move_pos.pos_zero, enemy_kittens_board, player_cats_board, enemy_cats_board
            move.boards[depth] = boards
            move.value = move.default_value
            move.set_count(last_move, depth)
            move.p_cat_count[depth] += 1
            return
        move_pos = move.move_pos
        cat_stack_counts = self.__cat_stack_counts
        first_bit_mask, second_bit_mask = move_pos.first_bit_mask, move_pos.second_bit_mask
        second_bit_zero_masks, first_bit_shift, out_piece_counts = move_pos.second_bit_zero_masks, move_pos.first_bit_shift, move_pos.out_piece_counts
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
            move.p_cat_count[depth] -= 1
        else:
            player_kittens_board |= move_pos.pos
            move.p_kitten_count[depth] -= 1

        
        p_mask, p_cat_count_key = self.__replace_kittens_masks(player_kittens_board, player_cats_board)
        e_mask, e_cat_count_key = self.__replace_kittens_masks(enemy_kittens_board, enemy_cats_board)
        promoted_p_cats = 0
        promoted_e_cats = 0

        if p_mask != 0:
            p_mask = ~p_mask
            promoted_p_cats = cat_stack_counts[p_cat_count_key]
            player_kittens_board &= p_mask
            player_cats_board &= p_mask

        if e_mask != 0:
            e_mask = ~e_mask
            promoted_e_cats = cat_stack_counts[e_cat_count_key]
            enemy_kittens_board &= e_mask
            enemy_cats_board &= e_mask

        if self.__is_winning(player_cats_board):
            move.value = 1000000
            return
        if self.__is_winning(enemy_cats_board):
            move.value = -1000000
            return
        
        move.boards[depth] = player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board
        #TODO add loading value from transposition table
        p_c_2 = self.__bit_counts.get(self.__connected_two(player_cats_board), 4)
        e_c_2 = self.__bit_counts.get(self.__connected_two(enemy_cats_board), 4)
        move.value = move.default_value + (e_kittens - p_kittens) * 10 + (e_cats - p_cats) * 100 + (promoted_p_cats - promoted_e_cats) * 100 + (p_c_2 - e_c_2) * 2000
        move.set_count(last_move, depth)
        move.p_kitten_count[depth] += p_kittens
        move.e_kitten_count[depth] += e_kittens
        move.p_cat_count[depth] += promoted_p_cats + p_cats
        move.e_cat_count[depth] += promoted_e_cats + e_cats
    
    def __replace_kittens_masks(self, kittens, cats):
        board = kittens | cats
        hor = board & (board >> 1) & (board >> 2)
        if hor > 0:
            hor &= ~(hor & (hor >> 1))
            mask1 = hor | hor << 1 | hor << 2
            mask2 = hor
            if mask1 & kittens > 0:
                return mask1, mask2
        ver = board & (board >> 6) & (board >> 12)
        if ver > 0:
            ver &= ~(ver & (ver >> 6))
            mask1 = ver | ver << 6 | ver << 12
            mask2 = ver
            if mask1 & kittens > 0:
                return mask1, mask2
        dig1 = board & (board >> 7) & (board >> 14)
        if dig1 > 0:
            dig1 &= ~(dig1 & (dig1 >> 7))
            mask1 = dig1 | dig1 << 7 | dig1 << 14
            mask2 = dig1
            if mask1 & kittens > 0:
                return mask1, mask2
        dig2 = board & (board >> 5) & (board >> 10)
        if dig2 > 0:
            dig2 &= ~(dig2 & (dig2 >> 5))
            mask1 = dig2 | dig2 << 5 | dig2 << 10
            mask2 = dig2
            if mask1 & kittens > 0:
                return mask1, mask2
        return 0, 0           
   
    def __is_winning(self,cat_board):
        if (cat_board & (cat_board >> 1) & (cat_board >> 2)) != 0:
            return True
        if (cat_board & (cat_board >> 6) & (cat_board >> 12)) != 0:
            return True
        if (cat_board & (cat_board >> 7) & (cat_board >> 14)) != 0:
            return True
        if (cat_board & (cat_board >> 5) & (cat_board >> 10)) != 0:
            return True
        return False
    
    def __connected_two(self, board):
        hor = board & (board >> 1)
        ver = board & (board >> 6)
        dig1 = board & (board >> 7)
        dig2 = board & (board >> 5)
        return hor | ver | dig1 | dig2
    
    def __generate_bitboards(self):
        kitten_bitboard = 0
        cat_bitboard = 0
        enemy_kitten_bitboard = 0
        enemy_cat_bitboard = 0
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

        return kitten_bitboard, cat_bitboard, enemy_kitten_bitboard, enemy_cat_bitboard


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



