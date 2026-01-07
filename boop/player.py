import base as BASE
import random, copy
import time
import os

"""
This file contains Player class, where you implement your player according the Boop rules.
To test your player, use section "if __name__ == "__main__" at the end of the file
You can run this file: python3 player.py, which should simulate a game of teo players and provide a set of png images.

However, this file does not verify if you play according to the rules or not. This functionality is on Brute only.
Anyway, if running this script produces an error, you have to fix it first before uploading to Brute.
Please do not use Brute as debugger tool :-)

"""

class TTEntry:
    def __init__(self, value, depth, flag):
        self.value = value
        self.depth = depth
        self.flag = flag

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
                

    def __init__(self, index, value):
        self.index = index
        self.pos = (1 << index)
        self.pos_zero = (1 << (36 - 1)) ^ self.pos
        self.value = value
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
    __slots__ = ('move_pos', 'type', 'is_winning', 'is_losing', 'value', 'p_kitten_count', 'e_kitten_count', 'p_cat_count', 'e_cat_count', 'boards')
    def __init__(self, move_pos: MovePos, type: int):
        self.move_pos = move_pos
        self.type = type
        self.is_winning = False
        self.is_losing = False
        self.value = 0
        self.p_kitten_count = 0
        self.e_kitten_count = 0
        self.p_cat_count = 0
        self.e_cat_count = 0
        self.boards = None

    def set_count(self, move: 'Move'):
        self.p_kitten_count = move.p_kitten_count
        self.e_kitten_count = move.e_kitten_count
        self.p_cat_count = move.p_cat_count
        self.e_cat_count = move.e_cat_count 


class Player(BASE.Base):
    def __init__(self, name, player):
        BASE.Base.__init__(self, player)     #we call constructor of the Base class first. Do not remove this line
        self.studentName = name             #parameter name will be filled with Brute and it contains your login
        self.studentTag = "Boop master"
        self.__current_move = 0
        self.__move_default_values = [
            1,1,1,1,1,1,
            1,5,5,5,5,1,
            1,5,7,7,5,1,
            1,5,7,7,5,1,
            1,5,5,5,5,1,
            1,1,1,1,1,1
        ]
        self.__move_pos = [MovePos(i, self.__move_default_values[i]) for i in range(36)]
        self.__cat_stack_counts = {}
        self.__create_cat_stack_counts()
        self.__bit_counts = {0: 0}
        self.__create_bit_counts(3)
        self.__transposition_table = {}
        self.__outer_square_mask = 0b111111100001100001100001100001111111
        self.__mid_square_mask = 0b000000011110010010010010011110000000
        self.__inner_square_mask = 0b000000000000001100001100000000000000

    def play(self):
        self.__current_move += 1
        if self.__current_move > self.maxMoves:
            return []
        self.__transposition_table = {}
        tt = self.__transposition_table
        p_k_board, e_k_board, p_c_board, e_c_board = self.__generate_bitboards()
        board = p_k_board | e_k_board | p_c_board | e_c_board
        if board == 0: 
            self.kittens-=1
            return [[3, 3], self.player, self.__generate_board(1 << 21, 0, 0, 0), []]
        default_move = Move(self.__move_pos[0], 0)
        default_move.boards = p_k_board, e_k_board, p_c_board, e_c_board
        default_move.p_kitten_count = self.kittens
        default_move.e_kitten_count = self.otherKittens
        default_move.p_cat_count = self.cats
        default_move.e_cat_count = self.otherCats
        end_time = time.perf_counter() + self.timeOut * 0.95
        depth = 3
        best_move = None
        best_move_value = -10000000
        win = False
        moves = self.__get_possible_moves(self.kittens, self.cats, board)
        if len(moves) == 0:
            return []
        filtered_moves = []
        for m in moves:
            self.__play_move(m, default_move, board)
            if m.is_winning:
                best_move = m
                win = True
                break 
            if m.is_losing:
                continue
            m.value += self.__eval_move(m)
            filtered_moves.append(m)

        while depth < 5 and not win:
            for m in filtered_moves: 
                tt_entry = tt.get(m.boards)
                if tt_entry is not None:
                    m.value = tt_entry.value
            filtered_moves.sort(key = lambda move: move.value, reverse = True)
            for m in filtered_moves:
                m_value = self.__play_enemy(m, depth, 0, 1, -10000000, 10000000, end_time)
                if m_value > best_move_value:
                    best_move_value = m_value
                    best_move = m
                if m_value >= 900000:
                    win = True
                    break
            depth += 2
            best_move_value = -10000000

        if best_move is None:
            return []
        
        self.__play_final_move(best_move, default_move, board)
        final_board = self.__generate_board(best_move.boards[0], best_move.boards[1], best_move.boards[2], best_move.boards[3])
        triples = self.__get_triples(final_board)
        self.kittens = best_move.p_kitten_count
        self.cats = best_move.p_cat_count
        self.otherKittens = best_move.e_kitten_count
        self.otherCats = best_move.e_cat_count
        self.board = final_board
        self.kittens = best_move.p_kitten_count
        self.cats = best_move.p_cat_count
        self.otherKittens = best_move.e_kitten_count
        self.otherCats = best_move.e_cat_count
        return [[best_move.move_pos.index // 6, best_move.move_pos.index % 6], best_move.type * self.player if best_move.type != 10 else 10, copy.deepcopy(final_board), triples]
    
    def __get_triples(self, board):
        cat_triples = []
        for i in range(6):
            for j in range(6):
                # horizontal
                if j < 4 and self.__is_cat_row(board[i][j], board[i][j+1], board[i][j+2]):
                    cat_triples = [[i,j], [i,j+1], [i,j+2]]
                elif j < 4 and self.__is_kitten_row(board[i][j], board[i][j+1], board[i][j+2]):
                    return [[i,j], [i,j+1], [i,j+2]]
                # vertical
                if i < 4 and self.__is_cat_row(board[i][j], board[i+1][j], board[i+2][j]):
                    cat_triples = [[i,j], [i+1,j], [i+2,j]]
                elif i < 4 and self.__is_kitten_row(board[i][j], board[i+1][j], board[i+2][j]):
                    return [[i,j], [i+1,j], [i+2,j]]
                # diagonal1
                if i < 4 and j < 4 and self.__is_cat_row(board[i][j], board[i+1][j+1], board[i+2][j+2]):
                    cat_triples = [[i,j], [i+1,j+1], [i+2,j+2]]
                elif i < 4 and j < 4 and self.__is_kitten_row(board[i][j], board[i+1][j+1], board[i+2][j+2]):
                    return [[i,j], [i+1,j+1], [i+2,j+2]]
                # diagonal2
                if i >= 2 and j < 4 and self.__is_cat_row(board[i][j], board[i-1][j+1], board[i-2][j+2]):
                    cat_triples = [[i,j], [i-1,j+1], [i-2,j+2]]
                elif i >= 2 and j < 4 and self.__is_kitten_row(board[i][j], board[i-1][j+1], board[i-2][j+2]):
                    return [[i,j], [i-1,j+1], [i-2,j+2]]
        return cat_triples
    
    def __is_cat_row(self, cell1, cell2, cell3):
        return cell1 == self.player * 2 and cell1 == cell2 and cell2 == cell3

    def __is_kitten_row(self, cell1, cell2, cell3):
        if cell1 < 0 and cell2 < 0 and cell3 < 0 and self.player == -1:
            return abs(cell1 + cell2 + cell3) < 6
        if cell1 > 0 and cell2 > 0 and cell3 > 0 and self.player == 1:
            return cell1 + cell2 + cell3 < 6

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

    def __play(self, move, depth, reverse_depth, depth_increment, alpha, beta, end_time):
        p_k_count, p_c_count= move.p_kitten_count, move.p_cat_count
        if p_k_count == 0 and p_c_count == 0:
            return 1000000 - reverse_depth
        
        o_alpha = alpha
        o_beta = beta

        value = -1000000
        tt = self.__transposition_table
        key = p_k_board, e_k_board, p_c_board, e_c_board = move.boards
        
        tt_entry = tt.get(key)
        if tt_entry is not None:
            if tt_entry.depth >= depth:
                if tt_entry.flag == 1:# exact
                    return tt_entry.value
                elif tt_entry.flag == 2:# upper estimate
                    beta = min(beta, tt_entry.value)
                elif tt_entry.flag == 3:# lower estimate
                    alpha = max(alpha, tt_entry.value)
                if alpha >= beta:
                    return tt_entry.value

        if depth <= 0 :#or end_time < time.perf_counter():
            return move.value

        board = p_k_board | e_k_board | p_c_board | e_c_board
       
        moves = self.__get_possible_moves(p_k_count, p_c_count, board)
        filtered_moves = []
        for m in moves:
            self.__play_move(m, move, board)
            if m.is_winning:
                return 1000000 - reverse_depth
            if m.is_losing:
                continue                   
            tt_entry = tt.get(m.boards)
            if tt_entry is not None:
                if tt_entry.flag == 1:# exact
                    m.value = tt_entry.value + 200
                if tt_entry.flag == 2:# upper estimate
                    m.value = tt_entry.value - 100
                if tt_entry.flag == 3:# lower estimate
                    m.value = tt_entry.value + 100
            else:
                m.value += self.__eval_move(m)
            filtered_moves.append(m)
        filtered_moves.sort(key = lambda move: move.value, reverse = True)
        depth_search = max(36 - reverse_depth * 7, 4)
        i = 0
        for m in filtered_moves:
            value = max(value, self.__play_enemy(m, depth - depth_increment, reverse_depth + depth_increment, depth_increment, alpha, beta, end_time))
            if value >= beta:
                break
            alpha = max(alpha, value)
            i += 1
            if i % depth_search == 0:
                depth_increment += 1
        if value <= o_alpha:
            flag = 2
        elif value >= o_beta:
            flag = 3
        else:
            flag = 1
        tt_entry = TTEntry(value, depth, flag)
        tt[key] = tt_entry
        return value

    def __play_enemy(self, move, depth, reverse_depth, depth_increment, alpha, beta, end_time):
        e_k_count, e_c_count= move.e_kitten_count, move.e_cat_count
        if e_k_count == 0 and e_c_count == 0:
            return -1000000 + reverse_depth
        
        o_alpha = alpha
        o_beta = beta
         
        value = 1000000
        tt = self.__transposition_table
        key = p_k_board, e_k_board, p_c_board, e_c_board = move.boards
        
        tt_entry = tt.get(key)
        if tt_entry is not None:
            if tt_entry.depth >= depth:
                if tt_entry.flag == 1:# exact
                    return tt_entry.value
                elif tt_entry.flag == 2:# upper estimate
                    beta = min(beta, tt_entry.value)
                elif tt_entry.flag == 3:# lower estimate
                    alpha = max(alpha, tt_entry.value)
                if alpha >= beta:
                    return tt_entry.value
        
        if depth <= 0: #or end_time < time.perf_counter():
            return move.value

        board = p_k_board | e_k_board | p_c_board | e_c_board
       
        moves = self.__get_possible_moves(e_k_count, e_c_count, board)
        filtered_moves= []
        for m in moves:
            self.__play_move(m, move, board, False)
            if m.is_losing:
                return -1000000 + reverse_depth
            if m.is_winning:
                continue
            tt_entry = tt.get(m.boards)
            if tt_entry is not None:
                if tt_entry.flag == 1:# exact
                    m.value = tt_entry.value - 200
                if tt_entry.flag == 2:# upper estimate
                    m.value = tt_entry.value + 100
                if tt_entry.flag == 3:# lower estimate
                    m.value = tt_entry.value - 100
            else:
                m.value += self.__eval_move(m)
            filtered_moves.append(m)
        filtered_moves.sort(key = lambda move: move.value)
        depth_search = max(36 - reverse_depth * 7, 4)
        i = 0
        for m in filtered_moves:
            value = min(value, self.__play(m, depth - depth_increment, reverse_depth + depth_increment, depth_increment, alpha, beta, end_time))
            if value <= alpha:
                break
            beta = min(beta, value)
            i += 1
            if i % depth_search == 0:
                depth_increment += 1

        if value <= o_alpha:
            flag = 2
        elif value >= o_beta:
            flag = 3
        else:
            flag = 1

        tt_entry = TTEntry(value, depth, flag)
        tt[key] = tt_entry
        return value
    
    def __get_possible_moves(self, p_kittens: int, p_cats: int, board: int) -> list[Move]:
        i = 0
        moves = []
        if p_cats + p_kittens == 0:
            for i in range(36):
                if board & (1 << i) > 0:
                    moves.append(Move(self.__move_pos[i], 10))
        elif p_cats == 0:
            for i in range(36):
                if board & (1 << i) == 0:
                    moves.append(Move(self.__move_pos[i], 1))
        elif p_kittens == 0:
            for i in range(36):
                if board & (1 << i) == 0:
                    moves.append(Move(self.__move_pos[i], 2))
        else:
            for i in range(36):
                if board & (1 << i) == 0:
                    moves.append(Move(self.__move_pos[i], 1))
                    moves.append(Move(self.__move_pos[i], 2))
        return moves
    
    def __play_final_move(self, move: Move, last_move: Move, board: int):
        move_pos = move.move_pos
        type = move.type
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = last_move.boards
        if type == 10:
            move.boards = player_kittens_board & move.move_pos.pos_zero, enemy_kittens_board, player_cats_board, enemy_cats_board
            move.p_cat_count += 1

        move_pos = move.move_pos
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
        move.set_count(last_move)
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
            move.p_cat_count -= 1
        else:
            player_kittens_board |= move_pos.pos
            move.p_kitten_count -= 1
        move.boards = player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board
        
        move.p_kitten_count += p_kittens
        move.e_kitten_count += e_kittens
        move.p_cat_count += p_cats
        move.e_cat_count += e_cats

    def __play_move(self, move: Move, last_move: Move, board: int, player = True):
        move_pos = move.move_pos
        type = move.type
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = last_move.boards
        if type == 10:
            move.set_count(last_move)
            if player:
                move.boards = player_kittens_board & move.move_pos.pos_zero, enemy_kittens_board, player_cats_board, enemy_cats_board
                move.value = move_pos.value
                move.p_cat_count += 1
            else:
                move.boards = player_kittens_board, enemy_kittens_board & move.move_pos.pos_zero, player_cats_board, enemy_cats_board
                move.value = -move_pos.value
                move.e_cat_count += 1
            return
        move.set_count(last_move)
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

            if player:
                player_cats_board |= move_pos.pos
                move.p_cat_count -= 1
            else:
                enemy_cats_board |= move_pos.pos
                move.e_cat_count -= 1
            
        else:
            if player:
                player_kittens_board |= move_pos.pos
                move.p_kitten_count -= 1
            else:
                enemy_kittens_board |= move_pos.pos
                move.e_kitten_count -= 1
        
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

        move.is_winning = False
        move.is_losing = False

        if self.__is_winning(player_cats_board):
            move.is_winning = True
        if self.__is_winning(enemy_cats_board):
            move.is_losing = True

        if move.is_winning or move.is_losing:
            return
        
        move.boards = player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board
        move.value = (move_pos.value if player else -move_pos.value) + (e_kittens - p_kittens) * 10 + (e_cats - p_cats) * 100 + (promoted_p_cats - promoted_e_cats) * 100
       
        move.p_kitten_count += p_kittens
        move.e_kitten_count += e_kittens
        move.p_cat_count += promoted_p_cats + p_cats
        move.e_cat_count += promoted_e_cats + e_cats

    def __eval_move(self, move: Move):
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = move.boards
        p_con_two = self.__bit_counts.get(self.__connected_two(player_cats_board), 4)
        e_con_two = self.__bit_counts.get(self.__connected_two(enemy_cats_board), 4)
        p_outer_cats = self.__bit_counts.get(player_cats_board & self.__outer_square_mask, 4)
        e_outer_cats = self.__bit_counts.get(enemy_cats_board & self.__outer_square_mask, 4)
        p_mid_cats = self.__bit_counts.get(player_cats_board & self.__mid_square_mask, 4)
        e_mid_cats = self.__bit_counts.get(enemy_cats_board & self.__mid_square_mask, 4)
        p_inner_cats = self.__bit_counts.get(player_cats_board & self.__inner_square_mask, 4)
        e_inner_cats = self.__bit_counts.get(enemy_cats_board & self.__inner_square_mask, 4)

        p_inner_kittens = self.__bit_counts.get(player_kittens_board & self.__inner_square_mask, 4)
        e_inner_kittens = self.__bit_counts.get(enemy_kittens_board & self.__inner_square_mask, 4)
        p_mid_kittens = self.__bit_counts.get(player_kittens_board & self.__mid_square_mask, 4)
        e_mid_kittens = self.__bit_counts.get(enemy_kittens_board & self.__mid_square_mask, 4)

        return (p_con_two - e_con_two) * 2000 + (p_inner_cats - e_inner_cats) * 200 + (p_mid_cats - e_mid_cats) * 100 + (p_outer_cats - e_outer_cats) * 10 + (p_inner_kittens - e_inner_kittens) * 10 + (p_mid_kittens - e_mid_kittens) * 5 + (move.p_cat_count - move.e_cat_count) * 50 + (move.e_kitten_count - move.p_kitten_count) * 5
    
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
                val = cell * self.player
                if val == 1:
                    kitten_bitboard |= 1 << i
                elif val == 2:
                    cat_bitboard |= 1 << i
                elif val == -1:
                    enemy_kitten_bitboard |= 1 << i
                elif val == -2:
                    enemy_cat_bitboard |= 1 << i
                i += 1

        return kitten_bitboard, enemy_kitten_bitboard, cat_bitboard,  enemy_cat_bitboard
    
    def __generate_board(self, kitten_bitboard, enemy_kitten_bitboard, cat_bitboard, enemy_cat_bitboard):
        board = [[0] * 6 for _ in range(6)]
        for i in range(36):
            if kitten_bitboard & (1 << i) > 0:
                board[i // 6][i % 6] = 1 * self.player
            elif cat_bitboard & (1 << i) > 0:
                board[i // 6][i % 6] = 2 * self.player
            elif enemy_kitten_bitboard & (1 << i) > 0:
                board[i // 6][i % 6] = -1 * self.player
            elif enemy_cat_bitboard & (1 << i) > 0:
                board[i // 6][i % 6] = -2 * self.player
        return board
    
    def print_board(self):
        board = self.board
        s_board = ''
        for row in board:
            s_board += '----' * len(row) + '-\n'
            for col in row:
                s = str(col) + ' '
                if len(s) == 2:
                    s = ' ' + s
                s_board += '|' + s
            s_board += '|\n'
        s_board += '----' * len(row) + '-\n'
        print(s_board)


"""
PUT ALL YOUR TEST INTO THIS SECTION:

The simple game here assumes that you play correctly. There are no checks here if the moves are valid or not.

"""

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

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

    #p1.draw(p1.board, "base.png")       #draw (empty) board and save in into base.png
    
    moveIdx = 0                         #index of the move, also use to index images
    while True:
        move1 = p1.play()               #the first player is on move
        if len(move1) > 0:
            move, animal, newboard, triple = move1  #unpack the move
            isEnd = BASE.updatePlayer(p1,p2,newboard, move[0], move[1], animal, triple, "move-{:03d}-p1".format(moveIdx))  #update the players, and save image
            clear()
            print("Move:", move, "Animal:", animal, "Triple:", triple, "\n")
            p1.print_board()
            input("Press enter to continue")
            if isEnd:
                print(p1.studentName, "wins")
                break

        move2 = p2.play()               #the second player is on move
        if len(move2) > 0:
            last_board = p1.board
            move, animal, newboard, triple = move2  #unpack move
            isEnd = BASE.updatePlayer(p2,p1,newboard, move[0], move[1], animal, triple, "move-{:03d}-p2".format(moveIdx))
            clear()
            print("Move:", move, "Animal:", animal, "Triple:", triple, "\n")
            p2.print_board()
            input("Press enter to continue")
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



