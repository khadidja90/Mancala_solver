
import copy
import math

MAX = 1   # IA
MIN = -1  # HUMAIN ou IA 2


# =========================
# 1. MancalaBoard
# =========================
class MancalaBoard:
    def __init__(self):
        self.board = {
            'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4, 'F': 4,
            'G': 4, 'H': 4, 'I': 4, 'J': 4, 'K': 4, 'L': 4,
            1: 0,
            2: 0
        }

        self.A_side = ('A', 'B', 'C', 'D', 'E', 'F')
        self.G_side = ('G', 'H', 'I', 'J', 'K', 'L')

        self.opposite = {
            'A': 'L', 'B': 'K', 'C': 'J', 'D': 'I', 'E': 'H', 'F': 'G',
            'G': 'F', 'H': 'E', 'I': 'D', 'J': 'C', 'K': 'B', 'L': 'A'
        }

        self.next_pit = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': 1,
            1: 'G',
            'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K', 'K': 'L', 'L': 2,
            2: 'A'
        }

    def possibleMoves(self, pits):
        return [p for p in pits if self.board[p] > 0]

    def doMove(self, pits, store, opponent_store, pit):
        seeds = self.board[pit]
        self.board[pit] = 0
        current = pit

        path = []  #  CHEMIN D’ANIMATION

        while seeds > 0:
            current = self.next_pit[current]
            if current == opponent_store:
                continue
            self.board[current] += 1
            seeds -= 1
            path.append(current)

        # Capture
        if current in pits and self.board[current] == 1:
            opp = self.opposite[current]
            if self.board[opp] > 0:
                self.board[store] += self.board[opp] + 1
                self.board[current] = 0
                self.board[opp] = 0

        return current == store, path


# =========================
# 2. Game
# =========================
class Game:
    def __init__(self):
        self.state = MancalaBoard()
        self.HUMAN_PITS = self.state.A_side
        self.COMPUTER_PITS = self.state.G_side
        self.HUMAN_STORE = 1
        self.COMPUTER_STORE = 2

    def gameOver(self):
        if all(self.state.board[p] == 0 for p in self.HUMAN_PITS):
            for p in self.COMPUTER_PITS:
                self.state.board[self.COMPUTER_STORE] += self.state.board[p]
                self.state.board[p] = 0
            return True

        if all(self.state.board[p] == 0 for p in self.COMPUTER_PITS):
            for p in self.HUMAN_PITS:
                self.state.board[self.HUMAN_STORE] += self.state.board[p]
                self.state.board[p] = 0
            return True

        return False

    def evaluate(self):
        return self.state.board[self.COMPUTER_STORE] - self.state.board[self.HUMAN_STORE]


# =========================
# 3. Minimax Alpha-Beta
# =========================
def MinimaxAlphaBetaPruning(game, player, depth, alpha, beta):
    if game.gameOver() or depth == 0:
        return game.evaluate(), None

    bestValue = -math.inf if player == MAX else math.inf

    pits = game.COMPUTER_PITS if player == MAX else game.HUMAN_PITS
    store = game.COMPUTER_STORE if player == MAX else game.HUMAN_STORE
    opp_store = game.HUMAN_STORE if player == MAX else game.COMPUTER_STORE

    for pit in game.state.possibleMoves(pits):
        child = copy.deepcopy(game)
        extra, _ = child.state.doMove(pits, store, opp_store, pit)
        next_player = player if extra else -player

        value, _ = MinimaxAlphaBetaPruning(child, next_player, depth - 1, alpha, beta)

        if player == MAX:
            bestValue = max(bestValue, value)
            alpha = max(alpha, bestValue)
        else:
            bestValue = min(bestValue, value)
            beta = min(beta, bestValue)

        if beta <= alpha:
            break

    return bestValue, None


# =========================
# 4. Play class 
# =========================

class Play:
    def __init__(self, mode="HUMAN_AI", human_first=True, depth_max=6, depth_min=4):
        self.game = Game()
        self.mode = mode

        self.depth_max = depth_max  # IA MAX (plus forte)
        self.depth_min = depth_min  # IA MIN (plus faible)

        self.turn = MIN if human_first else MAX
        self.last_move_path = []

        # ---------------- CMD PRINT ----------------
        print("===================================")
        print("MODE CHOISI :", self.mode)
        print("Premier joueur :", "Humain" if self.turn == MIN else "IA")
        print("Board initial :", self.game.state.board)
        print("===================================\n")

    def human_move(self, pit):
        if pit not in self.game.state.possibleMoves(self.game.HUMAN_PITS):
            return False

        print("\n--- TOUR HUMAIN ---")
        print("Humain choisit pit :", pit)
        print("Board avant le coup :", self.game.state.board)

        extra, path = self.game.state.doMove(self.game.HUMAN_PITS,
                                             self.game.HUMAN_STORE,
                                             self.game.COMPUTER_STORE,
                                             pit)
        self.last_move_path = path

        print("Board après le coup humain :", self.game.state.board)
        if extra:
            print("Humain obtient un tour supplémentaire !")
        else:
            self.turn = MAX

        return extra

    def ai_move(self, pits, store, opp_store, name="IA"):
        print(f"\n--- TOUR {name} ---")
        print(f"Board avant le coup {name} :", self.game.state.board)

        bestValue = -math.inf
        bestPit = None

        # Déterminer depth pour affichage (AI vs AI)
        depth_current = self.depth_max if self.turn == MAX else self.depth_min
        print(f"{name} utilise depth = {depth_current}")

        for pit in self.game.state.possibleMoves(pits):
            child = copy.deepcopy(self.game)
            extra, _ = child.state.doMove(pits, store, opp_store, pit)

            value, _ = MinimaxAlphaBetaPruning(
                child,
                MAX if extra else MIN,
                depth_current - 1,
                -math.inf,
                math.inf
            )

            print(f"{name} teste pit {pit} → valeur {value}")

            if value > bestValue:
                bestValue = value
                bestPit = pit

        print(f"{name} choisit pit :", bestPit)

        extra, path = self.game.state.doMove(pits, store, opp_store, bestPit)
        self.last_move_path = path

        print(f"Board après le coup {name} :", self.game.state.board)
        if extra:
            print(f"{name} obtient un tour supplémentaire !")
        else:
            self.turn *= -1

        return bestPit

    def is_game_over(self):
        return self.game.gameOver()
