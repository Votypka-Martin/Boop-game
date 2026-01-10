import base as BASE
import random, copy
import time
import os

class TTEntry:#třída pro uložení hodnoty vyhodnocené pozice
    def __init__(self, value, depth, flag):
        self.value = value#hodnota pozice
        self.depth = depth#hloubka, ve které byla pozice vyhodnocena
        self.flag = flag#označení určující, jak byla hodnota získána, 1 = přsné vyhodnocení, 2 = horní odhad, 3 = dolní odhad

class MovePos:
    first_bit_mask = [#maska bitů kolem vložené pozice - jedná se o bity, které se budou potenciálně přesouvat kvůli odsunu koťat a koček
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,1,0,1,0],
        [0,1,1,1,0],
        [0,0,0,0,0]
    ]

    second_bit_mask = [#maska bitů určující jednak blokující bity (ty které zastaví přesun) a jednak pozice, na které se první bity mohou přesunout
        [1,0,1,0,1],
        [0,0,0,0,0],
        [1,0,0,0,1],
        [0,0,0,0,0],
        [1,0,1,0,1]
    ]
    valid_bits = tuple(i for i in range(42) if i % 7 != 6)#celá pozice jednoho typu figur je zakódována do 42 bitů, 36 slouží pro figury, zbylých 6 je přidáno, aby bylo možné vyhodnotit výhru čistě na základě bitových posunů
    first_bit_indexes = [(1,1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)]#indexy prvních bitů - slouží pro generování konkrétních pozic
    second_bit_indexes = [(0, 0), (0, 2), (0, 4), (2, 0), (2, 4), (4, 0), (4, 2), (4, 4)]#indexy druhých bitů
    mask = 0b011111101111110111111011111101111110111111#maska celé pozice - 1 v místě, kde se mohou nacházet figury, 0 v místě kde ne

    @classmethod
    def combine(cls, board, mask, index):#metoda pro vložení masky do herní plochy na základě pozice - pozice je určována indexem
        board = [[0]*6 for _ in range(6)]
        dx = index % 7 - 2
        dy = index // 7 - 2
        for y in range(5):
            if y + dy < 0 or y + dy >= 6:
                continue
            for x in range(5):
                if x + dx < 0 or x + dx >= 6:
                    continue
                board[y + dy][x + dx] = mask[y][x]

        return board

    @classmethod
    def get_first_bit_mask(cls, second_bit_mask, index):#metoda pro získání masky prvních bitů na základě masky druhých bitů
        bit_board = [[0]*6 for _ in range(6)]
        x = index % 7
        y = index // 7
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
    def get_second_bit_mask(cls, first_bit_mask, index):#metoda pro získání masky druhých bitů na základě masky prvních bitů
        bit_board = [[0]*6 for _ in range(6)]
        x = index % 7
        y = index // 7
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
    def piece_count_difference(cls, board1, board2):#metoda pro získání rozdily počtu figur v jedné a druhé pozici
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
    def to_bitboard(cls, board):#metoda pro převod 2d seznamu do int proměnné
        bit_board = 0
        for y in range(6):
            for x in range(6):
                if board[y][x] == 1:
                    bit_board |= 1 << (y*7 + x)
        return bit_board
    
    @classmethod
    def bitboard_to_string(cls, bitboard):#metoda pro získání stringu z int proměnné - pouze pro debug
        s = ""
        for i in range(42):
            if i % 7 == 6:
                s += "\n"
                continue
            s += str((bitboard >> i) & 1)
        return s
                

    def __init__(self, index, value):
        if index % 7 == 6:#pokud je zbytek po dělení indexu 7 roven 6, pak pozice odpovídá místu redundantních bitů a nebude použita
            return
        self.index = index#uložení umístění tahu
        self.pos = (1 << index)#uložení masky tahu - 1 na místě, kam bude tah vložen
        self.pos_zero = MovePos.mask ^ self.pos#uložení masky pro odstranění tahu - 0 na místě, kam bude tah vložen - používáno v případě odebírání kotěte
        self.value = value#základní hodnota tahu - tahy uprostřed mají vyšší hodnotu než tahy u kraje
        self.create_bit_masks()

    def create_bit_masks(self):#metoda pro předgenerování výsledných pozic po provedení tahu
        mask = MovePos.mask
        board = [[0]*6 for _ in range(6)]
        self.first_bit_mask = MovePos.to_bitboard(MovePos.combine(board, MovePos.first_bit_mask, self.index))#získání masky prvních bitů
        self.second_bit_mask = MovePos.to_bitboard(MovePos.combine(board, MovePos.second_bit_mask, self.index))#získání masky druhých bitů
        self.second_bit_zero_masks = {}#slovník ve kterém jsou masky pro odstranění prvních bitů z pozice, pokud jsou blokovány druhým bitem - tyto bity se posouvat nebudou
        self.first_bit_shift = {}#slovník ve kterém budou všechny možné výsledné pozice přesunu prvního bitu do pozice druhého - odsun po vložení tahu
        self.out_piece_counts = {}#slovník ve kterém jsou počty figur, které byly po provedení tahu odstraněny z herní plochy
        for val in range(256):#celkově existuje 8 pozic, kde teoreticky může dojít k přesunu po vložení tahu - pozice kolem prováděného tahu - aby byly vytvořeny všechny možné kombninace, je potřeba vytvořit 2^8 (256) hodnot
            mask1 = [[0]*5 for _ in range(5)]#maska ve které budou uloženy pozice blokací
            mask2 = [[0]*5 for _ in range(5)]#maska ve které budou uloženy pozice k přesouvání
            for i in range(8):#do masek je vložena hodnota na pozici bitů
                mask1[MovePos.second_bit_indexes[i][0]][MovePos.second_bit_indexes[i][1]] = (val >> i) & 1
                mask2[MovePos.first_bit_indexes[i][0]][MovePos.first_bit_indexes[i][1]] = (val >> i) & 1
            
            second_bit_mask = MovePos.combine(board, mask1, self.index)#po vytvoření masek se vloží do herní plochy na místo tahu
            first_bit_mask = MovePos.combine(board, mask2, self.index)

            second_bit_board = MovePos.to_bitboard(second_bit_mask)#po získání výsledné plochy je plocha převedena do int proměnné
            first_bit_board = MovePos.to_bitboard(first_bit_mask)

            second_zero_mask = MovePos.to_bitboard(MovePos.get_first_bit_mask(second_bit_mask, self.index))#pozice prvních bitů pro odstranění kv§li blokaci bude na stejném místě, jako je pozice druhých bitů - první bit je druhým blokován a kvůli tomu nebude přesouván
            self.second_bit_zero_masks[second_bit_board] = (~second_zero_mask) & mask#aby bity z pozice zmizely, je získána negace masky - tam kde byly 1 budou 0 a naopak
            first_bit_shift = MovePos.to_bitboard(second_bit_mask)#po odsunutí se první bity dostanou do pozice druhých bitů
            self.first_bit_shift[first_bit_board] = first_bit_shift
            self.out_piece_counts[first_bit_board] = MovePos.piece_count_difference(first_bit_mask, second_bit_mask)#uložení rozdílu v počtu figur po vložení tahu

class Move:#třída reprezentující tah
    __slots__ = ('move_pos', 'type', 'is_winning', 'is_losing', 'value', 'p_kitten_count', 'e_kitten_count', 'p_cat_count', 'e_cat_count', 'boards')
    def __init__(self, move_pos: MovePos, type: int):
        self.move_pos = move_pos#uložení pozice tahu - instance třídy MovePos
        self.type = type#typ tahu - 1 kotě, 2 kočka, 10 odebrání kotěte
        self.is_winning = False#zda je tah výherní
        self.is_losing = False#zda je tah proherní
        self.value = 0#hodnota tahu
        self.p_kitten_count = 0#počet koťat, která má hráč k dispozici - ta která ještě může zahrát
        self.e_kitten_count = 0#počet koťat, která má protihrač k dispozici
        self.p_cat_count = 0#počet koček, které má hráč k dispozici
        self.e_cat_count = 0#počet koček, které má protihrač k dispozici
        self.boards = None#herní pozice pro každou z figur - koťata hráče, kočky hráče, koťata protihráče, kočky protihráče

    def set_count(self, move: 'Move'):#nastavení počtu figur podle předchozího tahu
        self.p_kitten_count = move.p_kitten_count
        self.e_kitten_count = move.e_kitten_count
        self.p_cat_count = move.p_cat_count
        self.e_cat_count = move.e_cat_count 


class Player(BASE.Base):
    def __init__(self, name, player):
        BASE.Base.__init__(self, player)     
        self.studentName = name             
        self.studentTag = "Boop master"
        self.__current_move = 0
        self.__move_default_values = [#základní hodnoty pro jednotlivé pozice - 0 v pravém okraji jsou redundantní bity pro vyhodnocí výhry
            1,1,1,1,1,1,0,
            1,5,5,5,5,1,0,
            1,5,7,7,5,1,0,
            1,5,7,7,5,1,0,
            1,5,5,5,5,1,0,
            1,1,1,1,1,1,0,
        ]
        self.__move_pos = [MovePos(i, self.__move_default_values[i]) for i in range(42)]#vytvoření jednotlivých pozic tahů
        self.__cat_stack_counts = {}#slovník pro uložení toho, kolik bylo získáno koček na základě přeměny koťat v kočky
        self.__create_cat_stack_counts()
        self.__bit_counts = {0: 0}#slovník ve kterém jsou předuloženy počty bitů nastavených na jedna v jednotlivých pozicích - počty jsou generovány pouze pro 3 bity
        self.__create_bit_counts(3)
        self.__transposition_table = {}#tabulky jednotlivých vyhodnocených pozic
        self.__outer_square_mask = 0b011111101000010100001010000101000010111111# maska pro získání bitů u okraje
        self.__mid_square_mask = 0b000000000111100010010001001000111100000000# maska pro získání bitů, které jsou mezi středem a okrjem
        self.__inner_square_mask = 0b000000000000000001100000110000000000000000# maska pro získání bitů ve středu

    def play(self):#metoda pro vygenerování nového tahu      
        self.__current_move += 1
        if self.__current_move > self.maxMoves:#pokud bylo dosaženo maximalního počtu tahu, vrací se prazdný seznam
            return []
        self.__transposition_table = {}
        tt = self.__transposition_table
        p_k_board, e_k_board, p_c_board, e_c_board = self.__generate_bitboards()#získání int hodnot z aktuální pozice
        board = p_k_board | e_k_board | p_c_board | e_c_board#získání celkového bitboardu - proměnná, která obsahuje jedničky na místech, kde je jakákoliv figura
        if board == 0: #pokud je plocha kompletně prázdná, vrátí se jako první tah, tah který je ve středu plochy
            return [3, 3, self.player, self.__generate_board(1 << 24, 0, 0, 0), []]
        default_move = Move(self.__move_pos[0], 0)#základní tah, který slouží akorát ke generování dalších tahů
        default_move.boards = p_k_board, e_k_board, p_c_board, e_c_board
        animals = self.countAnimals(self.board)
        default_move.p_kitten_count = self.kittens - animals[self.player]
        default_move.e_kitten_count = self.otherKittens - animals[-self.player]
        default_move.p_cat_count = self.cats - animals[2 * self.player]
        default_move.e_cat_count = self.otherCats - animals[-2 * self.player]
        end_time = time.perf_counter() + self.timeOut * 0.95#vyhodnocení času ukončení výpočtu
        depth = 1#počáteční hloubka
        
        win = False#zda byla zjištěna výhra
        moves = self.__get_possible_moves(default_move.p_kitten_count, default_move.p_cat_count, board, p_k_board)#získání seznamu všech tahů
        if len(moves) == 0:
            return []
        best_move = moves[0]
        best_move_value = -10000000
        filtered_moves = []
        for m in moves:#evaluace všech tahů
            self.__play_move(m, default_move, board)
            if m.is_winning:#pokud některý tah okamžitě vyhraje, není nutné vyhodnocovat žádné další
                best_move = m
                win = True
                tt[m.boards] = TTEntry(1000000, depth, 1)
                break 
            if m.is_losing:#tahy, které okamžitě prohrají jsou vynechány
                continue
            m.value += self.__eval_move(m)
            filtered_moves.append(m)

        while time.perf_counter() < end_time and not win:#dokud je ještě čas a nebyla zjištěna výhra
            current_best_move = best_move#aktuální nejlepší tah
            for m in filtered_moves: 
                tt_entry = tt.get(m.boards)
                if tt_entry is not None:
                    m.value = tt_entry.value
            filtered_moves.sort(key = lambda move: move.value, reverse = True)#seřazení tahů od nejlepšího po nejhorší
            for m in filtered_moves:
                m_value = self.__play_enemy(m, depth, 0, -10000000, 10000000, end_time)#získání hodnoty tahu
                if m_value > best_move_value:#pokud je aktuální tah lepší než aktuálně nejlepší
                    best_move_value = m_value
                    current_best_move = m
                if m_value >= 900000:#pokud existuje tah, který vyhraje
                    win = True
                    break
                tt[m.boards] = TTEntry(m_value, depth, 1)
            if time.perf_counter() >= end_time:#pokud již vypršel čas, pak v aktuální hloubce nebylo prohledávání dokončeno a kvůli tomu se nebude celkově nejlepší tah měnit
                break
            best_move = current_best_move
            depth += 1#zvýšení hloubky hledání
            tt[best_move.boards] = TTEntry(best_move_value, depth, 1)
            best_move_value = -10000000

        if best_move is None:
            return []
        self.__play_final_move(best_move, default_move, board)#odehrání konečného tahu
        final_board = self.__generate_board(best_move.boards[0], best_move.boards[1], best_move.boards[2], best_move.boards[3])#vytvooření nové pozice po provedení tahu
        triples = self.__get_triples(final_board)#získání trojic k přeměně či výhře
        self.board = final_board
        print("Depth: " + str(depth))
        return [best_move.move_pos.index // 7, best_move.move_pos.index % 7, best_move.type * self.player if best_move.type != 10 else 10, copy.deepcopy(final_board), triples]
    
    def __get_triples(self, board):#metoda vracející pozici, kde jsou trojice k přeměně či výhře
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
    
    def __is_cat_row(self, cell1, cell2, cell3):#metoda pro zjištěníní, zda jsou na pozicích tři kočky
        return cell1 == self.player * 2 and cell1 == cell2 and cell2 == cell3

    def __is_kitten_row(self, cell1, cell2, cell3):#metoda pro zjištěníní, zda jsou na pozicích kombinace koček a koťat, která by měla být přeměněna
        if cell1 < 0 and cell2 < 0 and cell3 < 0 and self.player == -1:
            return abs(cell1 + cell2 + cell3) < 6
        if cell1 > 0 and cell2 > 0 and cell3 > 0 and self.player == 1:
            return cell1 + cell2 + cell3 < 6

    def __create_bit_counts(self, max_bit_count, pos = 0, key = 0, count = 1):#metoda generující počty 1 uvnitř hodnoty
        if max_bit_count == 0 or pos == 42:
            return
        for i in range(pos, 42):
            if i % 7 == 6:
                continue
            new_key = key | 1 << i
            self.__bit_counts[new_key] = count
            self.__create_bit_counts(max_bit_count - 1, i + 1, new_key, count + 1)

    def __create_cat_stack_counts(self):#metoda generující počty koček získaných na základě přeměny
        self.__cat_stack_counts[0] = 0
        for i in MovePos.valid_bits:
            self.__cat_stack_counts[1 << i] = 3
        for i in range(len(MovePos.valid_bits)):
            for j in range(i + 1, len(MovePos.valid_bits)):
                x = MovePos.valid_bits[j]
                y = MovePos.valid_bits[i]
                self.__cat_stack_counts[1 << x | 1 << y] = 6

    def __play(self, move, depth, reverse_depth, alpha, beta, end_time):#metoda, která zjišťuje hodnotu daného tahu
        p_k_count, p_c_count= move.p_kitten_count, move.p_cat_count
        
        o_alpha = alpha
        o_beta = beta

        value = -1000000
        tt = self.__transposition_table
        key = p_k_board, e_k_board, p_c_board, e_c_board = move.boards#klíč pro načítání z tabulky vyhodnocených pozic
        
        tt_entry = tt.get(key)
        if tt_entry is not None:
            if tt_entry.depth >= depth:
                if tt_entry.flag == 1:# exact
                    return tt_entry.value
                elif tt_entry.flag == 2:# upper estimate
                    beta = min(beta, tt_entry.value)
                elif tt_entry.flag == 3:# lower estimate
                    alpha = max(alpha, tt_entry.value)
                if alpha >= beta:#odstřižení pozice, pokud je alpha >= beta - pokud toto nastane, znamená to, že protihráč má k dipozici tah, který je pro něj lepší než je aktuální a aktuální by stejně nebyl vybrán, takže je jeho vyhodnocení možné přeskočit
                    return tt_entry.value

        if depth <= 0 or end_time < time.perf_counter():#pokud se nacházím v konečné hloubce anebo vypršel čas, vrátí se hodnota aktuální pozice
            if tt_entry is not None:
                return tt_entry.value
            return move.value
        board = p_k_board | e_k_board | p_c_board | e_c_board
        moves = self.__get_possible_moves(p_k_count, p_c_count, board, p_k_board)
        if len(moves) == 0:
            return 1000000 - reverse_depth#pokud nexistuje žádný tah, znamená to, že hráč má v herní ploše 8 koček a tím pádem vyhrál
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
        i = 0
        search_width = 15 - reverse_depth#do plné hloubky jsou prohledávány pouze potenciálně nejlepší tahy - hloubka pro ostatní se postupně snižuje
        depth_increment = 1
        for m in filtered_moves:
            value = max(value, self.__play_enemy(m, depth - depth_increment, reverse_depth + 1, alpha, beta, end_time))
            if value >= beta:
                break
            alpha = max(alpha, value)
            i += 1
            if i % search_width == 0:
                depth_increment += 1
        if value <= o_alpha:#pokud je hodnota menší než alpha anebo větší než beta, pak došlo k odříznutí větve - hodnota tahu není úplně přesná
            flag = 2
        elif value >= o_beta:
            flag = 3
        else:
            flag = 1
        tt_entry = TTEntry(value, depth, flag)
        tt[key] = tt_entry
        return value

    def __play_enemy(self, move, depth, reverse_depth, alpha, beta, end_time):#to samé pro protihráče
        e_k_count, e_c_count= move.e_kitten_count, move.e_cat_count
        
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
        
        if depth <= 0 or end_time < time.perf_counter():
            if tt_entry is not None:
                return tt_entry.value
            return move.value

        board = p_k_board | e_k_board | p_c_board | e_c_board
       
        moves = self.__get_possible_moves(e_k_count, e_c_count, board, e_k_board)
        if len(moves) == 0:
            return -1000000 + reverse_depth
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
        i = 0
        search_width = 15 - reverse_depth
        depth_increment = 1
        for m in filtered_moves:
            value = min(value, self.__play(m, depth - depth_increment, reverse_depth + 1, alpha, beta, end_time))
            if value <= alpha:
                break
            beta = min(beta, value)
            i += 1
            if i % search_width == 0:
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
    
    def __get_possible_moves(self, p_kittens: int, p_cats: int, board: int, kitten_board: int) -> list[Move]:#metoda pro získání všech možných tahů
        i = 0
        moves = []
        valid_bits = MovePos.valid_bits
        if p_cats + p_kittens == 0:
            for i in valid_bits:
                if kitten_board & (1 << i) > 0:
                    moves.append(Move(self.__move_pos[i], 10))
        elif p_cats == 0:
            for i in valid_bits:
                if board & (1 << i) == 0:
                    moves.append(Move(self.__move_pos[i], 1))
        elif p_kittens == 0:
            for i in valid_bits:
                if board & (1 << i) == 0:
                    moves.append(Move(self.__move_pos[i], 2))
        else:
            for i in valid_bits:
                if board & (1 << i) == 0:
                    moves.append(Move(self.__move_pos[i], 1))
                    moves.append(Move(self.__move_pos[i], 2))
        return moves
    
    def __play_final_move(self, move: Move, last_move: Move, board: int):#metoda pro odehrání finálního tahu - to samé jako pro odhrání normálního tahu,a korát nejsou odebírány trojice a vyhodnocovány výhry
        move_pos = move.move_pos
        type = move.type
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = last_move.boards
        if type == 10:
            move.boards = player_kittens_board & move.move_pos.pos_zero, enemy_kittens_board, player_cats_board, enemy_cats_board
            move.p_cat_count += 1
            return

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

    def __play_move(self, move: Move, last_move: Move, board: int, player = True):#metoda pro odehrání tahu
        move_pos = move.move_pos
        type = move.type
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = last_move.boards#získání aktuálních pozic
        if type == 10:#pokud je tah odebrání kotěte
            move.set_count(last_move)
            if player:#odebrání kotěte z pozice hráče
                move.boards = player_kittens_board & move.move_pos.pos_zero, enemy_kittens_board, player_cats_board, enemy_cats_board
                move.value = move_pos.value
                move.p_cat_count += 1
            else:#odebrání kotěte z pozice protihráče
                move.boards = player_kittens_board, enemy_kittens_board & move.move_pos.pos_zero, player_cats_board, enemy_cats_board
                move.value = -move_pos.value
                move.e_cat_count += 1
            return
        move.set_count(last_move)
        move_pos = move.move_pos#přednačtení potřebných hodnot do lokálních proměnných
        cat_stack_counts = self.__cat_stack_counts
        first_bit_mask, second_bit_mask = move_pos.first_bit_mask, move_pos.second_bit_mask
        second_bit_zero_masks, first_bit_shift, out_piece_counts = move_pos.second_bit_zero_masks, move_pos.first_bit_shift, move_pos.out_piece_counts
        block = second_bit_mask & board
        
        key = player_kittens_board & first_bit_mask#získání pozice koťat, která se budou potenciálně přesouvat 
        second_bit_zero_mask = second_bit_zero_masks[block]#získání pozice koťat, která jsou blokována a nebudou přesunuta
        key &= second_bit_zero_mask#odstranění blokovaných koťat
        p_kittens = out_piece_counts[key]#získání počtu koťat, která byla vysunuta z pozice
        player_kittens_board = player_kittens_board & (~key) | first_bit_shift[key]#vyhodnocení pozice po všech přesunech

        key = enemy_kittens_board & first_bit_mask#to samé akorát pro koťata protihráče
        second_bit_zero_mask = second_bit_zero_masks[block]
        key &= second_bit_zero_mask
        e_kittens = out_piece_counts[key]
        enemy_kittens_board = enemy_kittens_board & (~key) | first_bit_shift[key]

        p_cats = 0
        e_cats = 0
        if type == 2:
            #pokud byla zahrána kočka, pak se kromě koťat budou přesouvat i už zahrané kočky
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
                player_cats_board |= move_pos.pos#vložení zahrané kočky do pozice
                move.p_cat_count -= 1
            else:
                enemy_cats_board |= move_pos.pos
                move.e_cat_count -= 1
            
        else:
            if player:
                player_kittens_board |= move_pos.pos#vložení zahraného kotěte do pozice
                move.p_kitten_count -= 1
            else:
                enemy_kittens_board |= move_pos.pos
                move.e_kitten_count -= 1
        
        p_mask, p_cat_count_key = self.__replace_kittens_masks(player_kittens_board, player_cats_board)#získání masky pro odbrání trojice s alespoň jedním kotětem
        e_mask, e_cat_count_key = self.__replace_kittens_masks(enemy_kittens_board, enemy_cats_board)
        promoted_p_cats = 0
        promoted_e_cats = 0

        if p_mask != 0:
            p_mask = ~p_mask
            promoted_p_cats = cat_stack_counts[p_cat_count_key]#získání počtu nových koček
            player_kittens_board &= p_mask#odebrání trojice
            player_cats_board &= p_mask#odebrání trojice

        if e_mask != 0:
            e_mask = ~e_mask
            promoted_e_cats = cat_stack_counts[e_cat_count_key]
            enemy_kittens_board &= e_mask
            enemy_cats_board &= e_mask

        move.boards = player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board
        move.is_winning = False
        move.is_losing = False

        if self.__is_winning(player_cats_board):
            move.is_winning = True
        if self.__is_winning(enemy_cats_board):
            move.is_losing = True

        if move.is_winning or move.is_losing:
            return
        
        
        move.value = (move_pos.value if player else -move_pos.value) + (e_kittens - p_kittens) * 10 + (e_cats - p_cats) * 100 + (promoted_p_cats - promoted_e_cats) * 200#základní evaluce tahu
       
        move.p_kitten_count += p_kittens
        move.e_kitten_count += e_kittens
        move.p_cat_count += promoted_p_cats + p_cats
        move.e_cat_count += promoted_e_cats + e_cats

    def __eval_move(self, move: Move):#pokročilejší evaluace tahu - zde si můžeš s programem nejvíc pohrát, protože evaluce bude mít extrémní vliv na kvalitu vyhodnocení
        player_kittens_board, enemy_kittens_board, player_cats_board, enemy_cats_board = move.boards
        p_cats, e_cats, p_kittens, e_kittens = move.p_cat_count, move.e_cat_count, move.p_kitten_count, move.e_kitten_count
        p_con_two = self.__bit_counts.get(self.__connected_two(player_cats_board), 4)
        e_con_two = self.__bit_counts.get(self.__connected_two(enemy_cats_board), 4)

        if p_con_two > 0 and e_cats == 0 and p_cats > 0:#pokud má hráč v herní pozici dvcojici koček, má k dipozici další kočku a protihráč nemá kočku, kterou by mohl dvojici rozbít, jedná se o velmi dobrý tah pro hráče
            return 10000
        if e_con_two > 0 and p_cats == 0 and e_cats > 0:#to samé pro protihráče
            return -10000
        
        p_outer_cats = self.__bit_counts.get(player_cats_board & self.__outer_square_mask, 4)#kočky hráče u kraje
        e_outer_cats = self.__bit_counts.get(enemy_cats_board & self.__outer_square_mask, 4)#kočky protihráče u kraje
        p_mid_cats = self.__bit_counts.get(player_cats_board & self.__mid_square_mask, 4)#kočky hráče uprostřed
        e_mid_cats = self.__bit_counts.get(enemy_cats_board & self.__mid_square_mask, 4)#kočky protihráče uprostřed (mezi středem a krajem)
        p_inner_cats = self.__bit_counts.get(player_cats_board & self.__inner_square_mask, 4)#kočky hráče ve středu
        e_inner_cats = self.__bit_counts.get(enemy_cats_board & self.__inner_square_mask, 4)#kočky protihráče ve středu

        p_inner_kittens = self.__bit_counts.get(player_kittens_board & self.__inner_square_mask, 4)#koťata hráče ve středu
        e_inner_kittens = self.__bit_counts.get(enemy_kittens_board & self.__inner_square_mask, 4)#koťata protihráče ve středu
        p_mid_kittens = self.__bit_counts.get(player_kittens_board & self.__mid_square_mask, 4)#koťata hráče uprostřed
        e_mid_kittens = self.__bit_counts.get(enemy_kittens_board & self.__mid_square_mask, 4)#koťata protihráče uprostřed

        return (p_con_two - e_con_two) * 2000 + (p_inner_cats - e_inner_cats) * 200 + (p_mid_cats - e_mid_cats) * 100 + (p_outer_cats - e_outer_cats) * 10 + (p_inner_kittens - e_inner_kittens) * 10 + (p_mid_kittens - e_mid_kittens) * 5 + (p_cats - e_cats) * 200 + (p_kittens - e_kittens) * 5
    
    def __replace_kittens_masks(self, kittens, cats):#metoda pro získání masky pro odebrání trojice
        board = kittens | cats
        hor = board & (board >> 1) & (board >> 2)
        if hor > 0:
            hor &= ~(hor & (hor >> 1))
            mask1 = hor | hor << 1 | hor << 2
            mask2 = hor
            if mask1 & kittens > 0:
                return mask1, mask2
        ver = board & (board >> 7) & (board >> 14)
        if ver > 0:
            ver &= ~(ver & (ver >> 7))
            mask1 = ver | ver << 7 | ver << 14
            mask2 = ver
            if mask1 & kittens > 0:
                return mask1, mask2
        dig1 = board & (board >> 8) & (board >> 16)
        if dig1 > 0:
            dig1 &= ~(dig1 & (dig1 >> 8))
            mask1 = dig1 | dig1 << 8 | dig1 << 16
            mask2 = dig1
            if mask1 & kittens > 0:
                return mask1, mask2
        dig2 = board & (board >> 6) & (board >> 12)
        if dig2 > 0:
            dig2 &= ~(dig2 & (dig2 >> 6))
            mask1 = dig2 | dig2 << 6 | dig2 << 12
            mask2 = dig2
            if mask1 & kittens > 0:
                return mask1, mask2
        return 0, 0           
   
    def __is_winning(self,cat_board):#metoda pro vyhodnocení výhry - vymaskuje trojice
        if (cat_board & (cat_board >> 1) & (cat_board >> 2)) != 0:
            return True
        if (cat_board & (cat_board >> 7) & (cat_board >> 14)) != 0:
            return True
        if (cat_board & (cat_board >> 8) & (cat_board >> 16)) != 0:
            return True
        if (cat_board & (cat_board >> 6) & (cat_board >> 12)) != 0:
            return True
        return False
    
    def __connected_two(self, board):#metoda pro vymaskování dvojic
        hor = board & (board >> 1)
        ver = board & (board >> 7)
        dig1 = board & (board >> 8)
        dig2 = board & (board >> 6)
        return hor | ver | dig1 | dig2
    
    def __generate_bitboards(self):#získání int z 2d seznamu
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
            i+=1

        return kitten_bitboard, enemy_kitten_bitboard, cat_bitboard,  enemy_cat_bitboard
    
    def __generate_board(self, kitten_bitboard, enemy_kitten_bitboard, cat_bitboard, enemy_cat_bitboard):#získání 2d seznamu z int
        board = [[0] * 6 for _ in range(6)]
        for i in MovePos.valid_bits:
            if kitten_bitboard & (1 << i) > 0:
                board[i // 7][i % 7] = 1 * self.player
            elif cat_bitboard & (1 << i) > 0:
                board[i // 7][i % 7] = 2 * self.player
            elif enemy_kitten_bitboard & (1 << i) > 0:
                board[i // 7][i % 7] = -1 * self.player
            elif enemy_cat_bitboard & (1 << i) > 0:
                board[i // 7][i % 7] = -2 * self.player
        return board
    
    def print_board(self):#zobrazení pozice v terminálu
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
    BASE.Base.init_gui()
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



