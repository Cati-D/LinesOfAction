import operator

import pygame
from copy import deepcopy
import time

# dimensiunile
WIDTH, HEIGHT = 800, 800
ROWS, COLUMNS = 8, 8
SQUARE_SIZE = HEIGHT // ROWS

# culorile in rgb, voi folosi conventia de culori folosita pe wiikipedia
BROWN = (165, 42, 42)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (108, 247, 87)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
PINK = (255, 192, 203)

# configurez fereastra
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Druta Cati - Lines of Action')


# tabla de joc
class Board:
    # constructor
    def __init__(self):
        self.board = []
        self.brown_left = self.yellow_left = 12
        self.create_table()
        self.board_for_debug = []
        self.piece_brown = []
        self.piece_yellow = []
        self.init_array()
        self.direction = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

    def init_array(self):
        for column in range(1, 7):
            self.piece_brown.append((0, column))
            self.piece_brown.append((7, column))
            self.piece_yellow.append((column, 0))
            self.piece_yellow.append((column, 7))

    # denesarea patratelelor de pe tabla de joc
    def draw_square(self, window):
        window.fill(GREEN)
        for row in range(ROWS + 1):
            for column in range(COLUMNS + 1):
                pygame.draw.lines(window, BLACK, True, ((0, column * SQUARE_SIZE), (row * SQUARE_SIZE, column * SQUARE_SIZE)))  # desenare linii
            pygame.draw.lines(window, BLACK, True,
                              ((row * SQUARE_SIZE, 0), (row * SQUARE_SIZE, column * SQUARE_SIZE)))  # desenare coloane

    # functie de calcul a scorului jocului
    def evaluate(self):
        return 20

    def alternate_evaluate(self):
        return 20

    def move_piece(self, piece, row, column):
        if self.valid(row, column):
            # interschimbarea elementelor de pe indicele curent (unde se afla piesa) si noua pozitie
            cpy1, cpy2 = piece.row, piece.column
            # elimin din vectorii de pozitii piesele care sunt cucerite si actualizez noua pozitie a pieselor
            if piece.color == BROWN:
                self.piece_brown.remove((cpy1, cpy2))
                self.piece_brown.append((row, column))
                # print(self.board[row][column])
                # if self.board[row][column] == YELLOW:
                #     self.piece_yellow.remove((row, column))
            if piece.color == YELLOW:
                self.piece_yellow.remove((cpy1, cpy2))
                self.piece_yellow.append((row, column))
                # if self.board[row][column] == BROWN:
                #     self.piece_brown.remove((row, column))
            self.remove(row, column)
            self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][
                piece.column]
            self.board[piece.row][piece.column] = 0
            self.board_for_debug[piece.row][piece.column], self.board_for_debug[row][column] = self.board_for_debug[row][
                                                                                               column], \
                                                                                           self.board_for_debug[
                                                                                               piece.row][piece.column]
            piece.move(row, column)
            self.board_for_debug[cpy1][cpy2] = 'Green'
            self.update_pieces()
        else:
            pass

    # returnez o piese in functie de linie si coloana
    def get_piece(self, row, column):
        return self.board[row][column]

    # functie de obtinere a tuturor pieselor
    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    # creez tabla de joc
    def create_table(self):
        for row in range(ROWS):
            self.board.append([])
            for column in range(COLUMNS):
                if (row == 0 or row == ROWS - 1) and (column != 0 and column != COLUMNS - 1):
                    # verificam daca suntem pe prima sau ultima linie, in caz afirmativ completez cu piese maro, evitand colturile
                    self.board[row].append(Pieces(row, column, BROWN))
                elif (column == 0 or column == COLUMNS - 1) and (row != 0 and row != ROWS - 1):
                    # verific daca sunt pe prima sau ultima coloana, in caz afirmativ, completez cu piese galbene, evitand colturile
                    self.board[row].append(Pieces(row, column, YELLOW))
                else:
                    # dac anu am nicio piesa de drept pe caseta, completez cu 0
                    self.board[row].append(0)
            # print(self.board[row][0].__repr__)

    # construiesc matricea pe baza tablei pentru debug - afisez culoarea de pe tabla3
    def _init_board_for_debug(self):
        for row in range(ROWS):
            self.board_for_debug.append([])
            for column in range(COLUMNS):
                if isinstance(self.board[row][column], Pieces):
                    if str(self.board[row][column]) == str(BROWN):
                        self.board_for_debug[row].append("Brown")
                    elif str(self.board[row][column]) == str(YELLOW):
                        self.board_for_debug[row].append("Yellow")
                else:
                    self.board_for_debug[row].append("Green")
        return self.board_for_debug

    def print_for_debug(self):
        if not self.board_for_debug:
            self._init_board_for_debug()
        for row in range(ROWS):
            print(self.board_for_debug[row])
        print("*********************************************************************")

    # desenez piesele pe tabla
    def draw(self, window):
        self.draw_square(window)
        for row in range(ROWS):
            for column in range(COLUMNS):
                piece = self.board[row][column]
                if piece:
                    piece.draw(window)

    # obtin muntarile posibile
    def get_valid_moves(self, piece):
        moves = []  # pozitiile pentru potentialele pozitii
        row = piece.row
        column = piece.column

        nb_pieces_row = 0  # numarul de piese de pe linie, se numara si piesa curenta
        for i in range(COLUMNS):
            if self.board[row][i] != 0:
                nb_pieces_row += 1

        nb_pieces_column = 0  # numarul de piese de pe coloana, se numara si piesa curenta
        for i in range(ROWS):
            if self.board[i][column] != 0:
                nb_pieces_column += 1

        nb_pieces_diagonal_left_up = 0  # stanga sus
        nb_pieces_diagonal_left_down = 0  # stanga jos
        nb_pieces_diagonal_right_up = 0  # dreapta sus
        nb_pieces_diagonal_right_down = 0  # dreapta jos
        x = piece.row
        y = piece.column
        z = 0
        while (x - z) >= 0 and (y - z) >= 0:
            if self.board[x - z][y - z] != 0:
                nb_pieces_diagonal_left_up += 1
            z += 1
        z = 0
        while x + z < ROWS and y + z < COLUMNS:
            if self.board[x + z][y + z] != 0:
                nb_pieces_diagonal_right_down += 1
            z += 1
        z = 0
        while x - z >= 0 and y + z < COLUMNS:
            if self.board[x - z][y + z] != 0:
                nb_pieces_diagonal_right_up += 1
            z += 1
        z = 0
        while x + z < ROWS and y - z >= 0:
            if self.board[x + z][y - z] != 0:
                nb_pieces_diagonal_left_down += 1
            z += 1

        # vreau sa le adaug in lista de miscari pe cele valide
        # verific pentru linie, stanga
        if self.valid_move(row, column - nb_pieces_row, piece) is not None:
            moves.append((row, column - nb_pieces_row))
        # verific pentru linie, dreapta
        if self.valid_move(row, column + nb_pieces_row, piece) is not None:
            moves.append((row, column + nb_pieces_row))
        # verific pentru coloana, sus
        if self.valid_move(row - nb_pieces_column, column, piece) is not None:
            moves.append((row - nb_pieces_column, column))
        # verific pentru coloana, jos
        if self.valid_move(row + nb_pieces_column, column, piece) is not None:
            moves.append((row + nb_pieces_column, column))
        # verific diagonala colt stanga sus
        if self.valid_move(row - (nb_pieces_diagonal_left_up + nb_pieces_diagonal_right_down - 1),
                           column - (nb_pieces_diagonal_left_up + nb_pieces_diagonal_right_down - 1),
                           piece) is not None:
            moves.append((row - (nb_pieces_diagonal_left_up + nb_pieces_diagonal_right_down - 1),
                          column - (nb_pieces_diagonal_left_up + nb_pieces_diagonal_right_down - 1)))
        # verific diagonala colt stanga jos
        if self.valid_move(row + (nb_pieces_diagonal_left_down + nb_pieces_diagonal_right_up - 1),
                           column - (nb_pieces_diagonal_left_down + nb_pieces_diagonal_right_up - 1),
                           piece) is not None:
            moves.append((row + (nb_pieces_diagonal_left_down + nb_pieces_diagonal_right_up - 1),
                          column - (nb_pieces_diagonal_left_down + nb_pieces_diagonal_right_up - 1)))
        # verific diagonala colt dreapta jos
        if self.valid_move(row + nb_pieces_diagonal_right_down + nb_pieces_diagonal_right_up - 1,
                           column + nb_pieces_diagonal_right_down + nb_pieces_diagonal_left_up - 1, piece) is not None:
            moves.append((row + nb_pieces_diagonal_right_down + nb_pieces_diagonal_right_up - 1,
                          column + nb_pieces_diagonal_right_down + nb_pieces_diagonal_right_up - 1))
        # verific diagonala colt dreapta sus
        if self.valid_move(row - nb_pieces_diagonal_right_up - nb_pieces_diagonal_left_down + 1,
                           column + nb_pieces_diagonal_right_up + nb_pieces_diagonal_left_down - 1, piece) is not None:
            moves.append((row - nb_pieces_diagonal_right_up - nb_pieces_diagonal_left_down + 1,
                          column + nb_pieces_diagonal_right_up + nb_pieces_diagonal_left_down - 1))

        return moves

    def update_pieces(self):
        v = self.get_all_pieces(YELLOW)
        for i in self.piece_yellow:
            if self.board[i[0]][i[1]] not in v:
                self.piece_yellow.remove(i)

        w = self.get_all_pieces(BROWN)
        for i in self.piece_brown:
            if self.board[i[0]][i[1]] not in w:
                self.piece_brown.remove(i)
        # print(self.get_all_pieces(YELLOW), "galben")
        # print(self.piece_yellow)
        # print(self.get_all_pieces(BROWN), "maro")
        # print(self.piece_brown)

    @staticmethod
    def valid(i, j):
        if i < 0 or i > ROWS - 1 or j < 0 or j > COLUMNS - 1:
            return False
        return True

    def valid_move(self, i, j, piece):
        if i < 0 or i > ROWS - 1 or j < 0 or j > COLUMNS - 1 or (
                self.board[i][j] != 0 and piece.color == self.board[i][j].color):
            return None
        return i, j

    def remove(self, row, column):  # scad nr de piese
        if self.valid(row, column):
            if self.board[row][column] != 0:
                if self.board[row][column].color == BROWN:
                    self.brown_left -= 1
                else:
                    self.yellow_left -= 1
        else:
            pass

    def winner(self):
        if self.winner_brown() is None and self.winner_yellow() is None:
            return None

    def winner_yellow(self):
        if self.yellow_left == 1:
            return YELLOW

        self.piece_yellow.sort(key=operator.itemgetter(0))
        first_yellow_piece = self.piece_yellow[0]
        yellow_connected = self.DFS(first_yellow_piece[0], first_yellow_piece[1], YELLOW)
        if yellow_connected == self.yellow_left:
            return YELLOW

        return None


    def winner_brown(self):
        if self.brown_left == 1:
            return BROWN
        # retin pozitiile aparitiilor primelor piese pe tabla de joc
        self.piece_brown.sort(key=operator.itemgetter(0))
        first_brown_piece = self.piece_brown[0]

        brown_connected = self.DFS(first_brown_piece[0], first_brown_piece[1], BROWN)
        if brown_connected == self.brown_left:  # verirific daca nr de piese conexe este egal cu numarul de piese ramase
            return BROWN
        return None

    # functie in care verific daca am remiza
    def both_winner(self):
        if self.winner_brown() == BROWN and self.winner_yellow() == YELLOW:
            return True


    def DFS(self, i, j, c):
        connected_piece = 0  # numarul de piese conexe
        visited, stack = set(), [(i, j)]
        while stack:
            i, j = stack.pop()
            for k in range(len(self.direction)):
                dx = i + self.direction[k][0]
                dy = j + self.direction[k][1]
                if (-1 < dx < ROWS and -1 < dy < COLUMNS) and ((dx, dy) not in visited) and self.board[dx][dy] != 0 and \
                        self.board[dx][dy].color == c:
                    connected_piece += 1
                    visited.add((dx, dy))
                    stack.append((dx, dy))
        return connected_piece

    #     if self.verify_neighbor(self.board[self.piece_brown[0][0]][self.piece_brown[0][1]]):
    #         return BROWN
    #     if self.verify_neighbor(self.board[self.piece_yellow[0][0]][self.piece_yellow[0][1]]):
    #         return YELLOW
    #
    # def verify_neighbor(self, piece): # verific ca oricare piesa sa aiba vecini de aceeasi culoare
    #     if piece.color == BROWN:
    #         if ((piece.row - 1, piece.column) in self.piece_brown) or ((piece.row - 1, piece.column - 1) in self.piece_brown) or ((piece.row - 1, piece.column + 1) in self.piece_brown) or ((piece.row, piece.column - 1) in self.piece_brown) or ((piece.row, piece.column + 1) in self.piece_brown) or ((piece.row + 1, piece.column) in self.piece_brown) or ((piece.row + 1, piece.column - 1) in self.piece_brown) or ((piece.row + 1, piece.column + 1) in self.piece_brown):
    #             return False
    #     if piece.color == YELLOW:
    #         if ((piece.row - 1, piece.column) in self.piece_yellow) or ((piece.row - 1, piece.column - 1) in self.piece_yellow) or ((piece.row - 1, piece.column + 1) in self.piece_yellow) or ((piece.row, piece.column - 1) in self.piece_yellow) or ((piece.row, piece.column + 1) in self.piece_yellow) or ((piece.row + 1, piece.column) in self.piece_yellow) or ((piece.row + 1, piece.column - 1) in self.piece_yellow) or ((piece.row + 1, piece.column + 1) in self.piece_yellow):
    #             return False
    #     return True


class Pieces:
    PADDING = 15
    BORDER = 3

    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color

        self.x = 0
        self.y = 0
        self.calculate_position()

    def calculate_position(self):
        self.x = SQUARE_SIZE * self.column + SQUARE_SIZE // 2  # ajungem in mijlocul casetei
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def draw(self, window):
        pygame.draw.circle(window, RED, (self.x, self.y),
                           SQUARE_SIZE // 2 - self.PADDING + self.BORDER)  # ultimul parametru este raza cercurlui care se deseneaza
        pygame.draw.circle(window, self.color, (self.x, self.y), SQUARE_SIZE // 2 - self.PADDING)

    # modificarea pozitiei dupa ce are loc mutarea
    def move(self, row, column):
        self.row = row
        self.column = column
        self.calculate_position()

    def __repr__(self):
        return str(self.color)


class Game:
    def __init__(self, window):
        self._init()
        self.selected = None
        self.window = window

    def update_display(self):  # updatez tabla de joc
        self.board.draw(self.window)
        if self.selected:
            self.draw_valid_moves(self.valid_moves)

        if self.board.both_winner():
            for piece in self.board.piece_brown:
                pygame.draw.circle(self.window, GOLD, (
                    piece[1] * SQUARE_SIZE + SQUARE_SIZE // 2, piece[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
                pygame.display.update()
            for row in range(ROWS):
                for piece in self.board.piece_yellow:
                    pygame.draw.circle(self.window, GOLD, (
                        piece[1] * SQUARE_SIZE + SQUARE_SIZE // 2, piece[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
                    pygame.display.update()
            time.sleep(3)
            pygame.draw.rect(window, PINK, (0, 0, 800, 800))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 64)
            text = font.render('        !!!      DRAW      !!!', True, GOLD)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(3)

        elif self.board.winner_brown() == BROWN:  # castiga maro
            for row in range(ROWS):
                for piece in self.board.piece_brown:
                    pygame.draw.circle(self.window, GOLD, (
                    piece[1] * SQUARE_SIZE + SQUARE_SIZE // 2, piece[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
                    pygame.display.update()
            time.sleep(3)
            pygame.draw.rect(window, PINK, (0, 0, 800, 800))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 64)
            text = font.render('!!!      BROWN WON      !!!', True, GOLD)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(3)
        elif self.board.winner_yellow() == YELLOW:  # castiga galben
            # self.board.update_array()
            for row in range(ROWS):
                for piece in self.board.piece_yellow:
                    pygame.draw.circle(self.window, GOLD, (
                        piece[1] * SQUARE_SIZE + SQUARE_SIZE // 2, piece[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
                    pygame.display.update()
            time.sleep(3)
            pygame.draw.rect(window, PINK, (0, 0, 800, 800))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 64)
            text = font.render('!!!      YELLOW WON      !!!', True, GOLD)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(3)
        else:
            pass
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = BROWN
        self.valid_moves = {}
        self.board.print_for_debug()

    def reset(self):
        self._init()

    def select_piece(self, row, column):
        if self.selected:
            result = self._move(row, column)
            if not result:
                self.selected = None
                self.select_piece(row, column)
        piece = self.board.get_piece(row, column)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        return False

    def _move(self, row, column):
        piece = self.board.get_piece(row, column)
        # verificam ca pozitia pe care dorim sa mutam piesa sa nu contina o piesa de aceeasi culoare
        if self.selected and piece != self.turn and (row, column) in self.valid_moves:
            self.board.move_piece(self.selected, row, column)
            # self.board.print_for_debug()
            self.change_turn()
        else:
            return False

        return True

    # denez cate un cerc albastru pe locul unde vreau sa mut piesa
    def draw_valid_moves(self, moves):
        for move in moves:
            (row, column) = move
            pygame.draw.circle(self.window, BLUE,
                               (column * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == BROWN:
            self.turn = YELLOW
            # afisez al cui este randul
            pygame.draw.rect(window, PINK, (180, 180, 430, 430))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 50)
            text = font.render('               YELLOW TURN', True, BROWN)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(0.5)
            self.board.print_for_debug()
        else:
            self.turn = BROWN
            pygame.draw.rect(window, PINK, (180, 180, 430, 430))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 50)
            text = font.render('                BROWN TURN', True, BROWN)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(0.5)
            self.board.print_for_debug()

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()


# functie auiliara de simulare mutari pentru minmax
def simulate_move(piece, move, board):
    board.move_piece(piece, move[0], move[1])
    return board


# functie care imi returneaza mutarile posibile pentru un anumit tip de piese
# functie succesor - memoreaza starile in care duc mutarile posibile simultan
def get_all_moves(board, color):
    moves = []

    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        # print(piece)
        for move in valid_moves:
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.column)
            new_board = simulate_move(temp_piece, move, temp_board)
            moves.append(new_board)
    return moves


# implementarea algoritmului minmax
def minmax(current_board, depth, player_choice):
    """
    :param current_board: pozitia in care se afla tabla de joc in prezent
    :param depth: adancimea arborelui
    :param player_choice: bool care verifica daca jucatorul a ales min sau max
    """

    if depth == 0 or current_board.winner() is not None:
        return current_board.evaluate(), current_board

    if player_choice:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(current_board, BROWN):  # am hardcodat, maximul sa fie maro
            evaluation = minmax(move, depth - 1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(current_board, YELLOW):
            evaluation = minmax(move, depth - 1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        return minEval, best_move

def minmax_yellow(current_board, depth, player_choice):
    """
    :param current_board: pozitia in care se afla tabla de joc in prezent
    :param depth: adancimea arborelui
    :param player_choice: bool care verifica daca jucatorul a ales min sau max
    """
    if depth == 0 or current_board.winner() is not None:
        return current_board.evaluate(), current_board

    if player_choice:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(current_board, YELLOW):  # am hardcodat, maximul sa fie galben
            evaluation = minmax(move, depth - 1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(current_board, BROWN):
            evaluation = minmax(move, depth - 1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        return minEval, best_move


# alpha-beta
def alpha_beta_brown(alpha, beta, table, depth, player_choice):
    if depth == 0 or table.winner() is not None:
        return table.alternate_evaluate(), table

    if alpha > beta:
        return table.alternate_evaluate(), table

    if player_choice:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(table, BROWN):
            evaluation = alpha_beta_brown(alpha, beta, move, depth - 1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
            alpha = max(alpha, evaluation)
            if alpha == evaluation and alpha >= beta:
                break
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(table, YELLOW):
            evaluation = alpha_beta_brown(alpha, beta, move, depth - 1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
            beta = min(beta, evaluation)
            if beta == evaluation and alpha >= beta:
                break
        return minEval, best_move


# extrag din matrice pozitia pe care ma aflu atunci cand dau click
def get_coordinate_from_mouse(position):
    x, y = position
    row = y // SQUARE_SIZE
    column = x // SQUARE_SIZE
    return row, column


# butoane
def button(x, y, w, h, inactive, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        window.blit(inactive, (x, y))
        if click[0] == 1 and action is not None:
            action()
    else:
        window.blit(inactive, (x, y))


# mainul pentru 2 playeri
def main_players():
    run = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()
    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                row, column = get_coordinate_from_mouse(position)
                game.select_piece(row, column)

        game.update_display()
    pygame.quit()


####################################################### MINMAX #########################################################


# meniu pentru alegere adancimea arborelui player vs ai
def depth_selector_player_ai():
    intro1 = True
    pygame.init()
    while intro1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                intro1 = False
                quit()

        window.fill(YELLOW)

        title = pygame.image.load("titlu.png")
        titleText = window.blit(title, title.get_rect())  # title is an image
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        depth1 = pygame.image.load("depth1.png")
        depth2 = pygame.image.load("depth2.png")

        button(200, 200, 195, 80, depth1, main1)
        button(200, 300, 195, 80, depth2, main2)

        pygame.display.update()
        pygame.time.Clock().tick(15)

#menu selectare adancime arbore ai vs ai minmax
def depth_selector_ai_ai():
    intro2 = True
    pygame.init()
    while intro2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                intro2 = False
                quit()

        window.fill(YELLOW)

        title = pygame.image.load("titlu.png")
        titleText = window.blit(title, title.get_rect())  # title is an image
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        depth1 = pygame.image.load("depth1.png")
        depth2 = pygame.image.load("depth2.png")

        # button(x, y, w, h, inactive, active, action=None)
        button(200, 200, 195, 80, depth1, main_ai1)
        button(200, 300, 195, 80, depth2, main_ai2)

        pygame.display.update()
        pygame.time.Clock().tick(15)


def algminmax():
    intro3 = True
    # pygame.init()
    while intro3:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # intro3 = False
                quit()

        window.fill(YELLOW)

        title = pygame.image.load("titlu.png")
        title_text = window.blit(title, title.get_rect())  # titlul care este imagine
        title_text.center = ((WIDTH / 2), (HEIGHT / 2))

        playerVSplayer = pygame.image.load("pvsp.png")
        playerVSai = pygame.image.load("pvsai.png")
        aiVSai = pygame.image.load("aivsai.png")

        button(200, 400, 195, 80, playerVSplayer, main_players)
        button(200, 500, 195, 80, playerVSai, depth_selector_player_ai)
        button(200, 600, 195, 80, aiVSai, depth_selector_ai_ai)

        pygame.display.update()
        pygame.time.Clock().tick(15)


# main default pentru player vs ai
def main(depth):
    run = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()

    while run:
        clock.tick(60)

        if game.turn == BROWN:
            value, new_board = minmax(game.get_board(), depth, True)
            game.ai_move(new_board)

        # verificam daca alegem sa inchidem fereastra
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                row, column = get_coordinate_from_mouse(position)
                game.select_piece(row, column)

        game.update_display()
    pygame.quit()


# apeluri pentru main minmax
def main1():
    main(1)


def main2():
    main(2)


# main ai vs ai minmax
def main_ai(depth):
    run = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()
    while run:
        clock.tick(60)

        if game.turn == BROWN:
            value, new_board = minmax(game.get_board(), depth, True)
            game.ai_move(new_board)
        else:
            value, new_board = minmax_yellow(game.get_board(), depth, True)
            game.ai_move(new_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                row, column = get_coordinate_from_mouse(position)
                game.select_piece(row, column)
        game.update_display()
    pygame.quit()


# mainuri minmaxx
def main_ai1():
    main_ai(1)


def main_ai2():
    main_ai(2)


################################################# ALPHA BETA ###########################################################


def depth_selector_ai_ai_ab():
    intro4 = True
    pygame.init()
    while intro4:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                intro4 = False
                quit()

        window.fill(YELLOW)

        title = pygame.image.load("titlu.png")
        titleText = window.blit(title, title.get_rect())  # title is an image
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        depth1 = pygame.image.load("depth1.png")
        depth2 = pygame.image.load("depth2.png")
        depth3 = pygame.image.load("depth3.png")

        # button(x, y, w, h, inactive, active, action=None)
        button(200, 200, 195, 80, depth1, main_ai_1)
        button(200, 300, 195, 80, depth2, main_ai_2)
        button(200, 400, 195, 80, depth3, main_ai_3)

        pygame.display.update()
        pygame.time.Clock().tick(15)


# main ai vs ai alpha
def main_ai_alpha(depth):
    run = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()
    while run:
        clock.tick(60)
        if game.turn == BROWN:
            value, new_board = minmax_yellow(game.get_board(), depth, True)
            game.ai_move(new_board)
        else:
            value, new_board = alpha_beta_brown(0, 0, game.get_board(), depth, True)
            game.ai_move(new_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                row, column = get_coordinate_from_mouse(position)
                game.select_piece(row, column)
        game.update_display()
    pygame.quit()


def algmalphabeta():
    intro = True
    pygame.init()
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # intro = False
                pygame.quit()
                quit()

        window.fill(YELLOW)

        title = pygame.image.load("titlu.png")
        title_text = window.blit(title, title.get_rect())  # titlul care este imagine
        title_text.center = ((WIDTH / 2), (HEIGHT / 2))

        playerVSplayer = pygame.image.load("pvsp.png")
        playerVSai = pygame.image.load("pvsai.png")
        aiVSai = pygame.image.load("aivsai.png")

        button(200, 400, 195, 80, playerVSplayer, main_players)
        button(200, 500, 195, 80, playerVSai, depth_selector_player_ai)
        button(200, 600, 195, 80, aiVSai, depth_selector_ai_ai_ab)


        pygame.display.update()
        pygame.time.Clock().tick(15)

# mainuri alphabeta
def main_ai_1():
    main_ai_alpha(1)


def main_ai_2():
    main_ai_alpha(2)


def main_ai_3():
    main_ai_alpha(3)


###################################################### MENIU PRINCIPAL #################################################

# meniu mod joc
def game_intro():
    intro = True
    # pygame.init()
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                intro = False
                quit()

        window.fill(YELLOW)

        title = pygame.image.load("titlu.png")
        titleText = window.blit(title, title.get_rect())  # title is an image
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        alphabeta = pygame.image.load("alphabeta.png")
        balgminmax = pygame.image.load("minmax.png")

        button(200, 200, 195, 80, alphabeta, algmalphabeta)
        button(200, 300, 195, 80, balgminmax, algminmax)

        pygame.display.update()
        pygame.time.Clock().tick(15)


# run
game_intro()