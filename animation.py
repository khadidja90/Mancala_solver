import pygame
import sys
import time
import math

from engine import Play, MAX, MIN

# =====================================================
# INIT PYGAME
# =====================================================
pygame.init()
# =====================================================
# AUDIO INIT
# =====================================================
pygame.mixer.init()

# Musique de fond
pygame.mixer.music.load("assets/mysterious-african-music-349048.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # -1 = boucle infinie

# Effets sonores
click_sound = pygame.mixer.Sound("assets/mixkit-select-click-1109.wav")
drop_sound  = pygame.mixer.Sound("assets/dropping-of-the-ring-404874.mp3")

click_sound.set_volume(0.8)
drop_sound.set_volume(0.9)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mancala Game")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 28, bold=True)
INFO_FONT = pygame.font.SysFont("arial", 22, bold=True)
TURN_FONT = pygame.font.SysFont("arial", 26, bold=True)
HOVER_FONT = pygame.font.SysFont("arial", 18, bold=True)   # <<< AJOUT

ANIM_DELAY = 300

# =====================================================
# LOAD IMAGES
# =====================================================
def load(img):
    return pygame.transform.smoothscale(
        pygame.image.load(img).convert_alpha(),
        (WIDTH, HEIGHT)
    )

splash_img = load("assets/splash.png")
start_img = load("assets/start_game.png")
instruction_img = load("assets/instructions.png")
mode_img = load("assets/mode.png")
tour_img = load("assets/tour.png")
board_img = load("assets/board.png")
score_img = load("assets/score.png")
play_again_img = load("assets/play_againe.png")

# =====================================================
# SCREENS
# =====================================================
SPLASH, START, INSTRUCTION, MODE, TOUR, GAME, SCORE, PLAY_AGAIN = (
    "splash", "start", "instruction", "mode", "tour", "game", "score", "play_again"
)

current_screen = SPLASH
splash_start = time.time()

# =====================================================
# ENGINE / STATE
# =====================================================
engine = None
selected_mode = None

# IA VISUEL
ai_selected_pit = None
ai_show_time = 0
AI_DISPLAY_DURATION = 2000

# =====================================================
# BUTTONS
# =====================================================
START_BUTTON = pygame.Rect(300, 280, 300, 70)
CONTINUE_BUTTON = pygame.Rect(250, 520, 300, 60)

LEFT_BUTTON  = pygame.Rect(250, 250, 260, 90)
RIGHT_BUTTON = pygame.Rect(250, 330, 260, 90)

OK_BUTTON = pygame.Rect(300, 420, 200, 60) 

PLAY_AGAIN_BUTTON = pygame.Rect(230, 240, 340, 70) 
HOME_BUTTON       = pygame.Rect(230, 330, 340, 70)

# =====================================================
# BOARD GEOMETRY
# =====================================================
PITS, COMP_PITS = {}, {}
start_x, size, gap = 170, 60, 20

y_human = 330
for i, p in enumerate("ABCDEF"):
    PITS[p] = pygame.Rect(start_x + i*(size+gap), y_human, size, size)

y_comp = 200
for i, p in enumerate("GHIJKL"):
    COMP_PITS[p] = pygame.Rect(start_x + (5-i)*(size+gap), y_comp, size, size)

ALL_PITS = {**PITS, **COMP_PITS}

C_STORE = pygame.Rect(80, 250, 50, 120)
H_STORE = pygame.Rect(650, 250, 50, 120)

# =====================================================
# MARBLES
# =====================================================
marble_imgs = [
    pygame.transform.smoothscale(
        pygame.image.load(f"assets/marble{i}.png").convert_alpha(), (16, 16)
    )
    for i in range(1, 5)
]

def marble_positions(rect, count):
    res = []
    cx, cy = rect.center
    r = min(rect.width, rect.height) // 3
    for i in range(count):
        a = 2 * math.pi * i / max(1, count)
        res.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return res

def draw_marbles_custom(board):
    for d in (PITS, COMP_PITS):
        for pit, rect in d.items():
            for i, pos in enumerate(marble_positions(rect, board[pit])):
                screen.blit(marble_imgs[i % 4], pos)

    for store, rect in [
        (engine.game.HUMAN_STORE, H_STORE),
        (engine.game.COMPUTER_STORE, C_STORE)
    ]:
        for i, pos in enumerate(marble_positions(rect, board[store])):
            screen.blit(marble_imgs[i % 4], pos)

def draw_marbles():
    draw_marbles_custom(engine.game.state.board)

# =====================================================
# HOVER TOOLTIP  <<< AJOUT
# =====================================================
def draw_tooltip(x, y, text):
    surf = HOVER_FONT.render(text, True, (255, 255, 255))
    rect = surf.get_rect(center=(x, y))
    bg = pygame.Rect(rect.left-6, rect.top-4, rect.width+12, rect.height+8)

    pygame.draw.rect(screen, (0, 0, 0), bg)
    pygame.draw.rect(screen, (255, 215, 0), bg, 2)
    screen.blit(surf, rect)

def draw_hover_info():
    if not engine:
        return

    mx, my = pygame.mouse.get_pos()

    for pit, rect in ALL_PITS.items():
        if rect.collidepoint(mx, my):
            draw_tooltip(rect.centerx, rect.top - 10,
                         f"{engine.game.state.board[pit]} marbles")
            return

    if H_STORE.collidepoint(mx, my):
        draw_tooltip(H_STORE.centerx, H_STORE.top - 10,
                     f"{engine.game.state.board[engine.game.HUMAN_STORE]} marbles")

    if C_STORE.collidepoint(mx, my):
        draw_tooltip(C_STORE.centerx, C_STORE.top - 10,
                     f"{engine.game.state.board[engine.game.COMPUTER_STORE]} marbles")

# =====================================================
# ANIMATION
# =====================================================
def animate_move(start_pit, path):
    if not path:
        return

    temp_board = engine.game.state.board.copy()
    for t in path:
        temp_board[t] -= 1

    for t in path:
        temp_board[t] += 1

        
        drop_sound.play()

        screen.blit(board_img, (0, 0))
        draw_marbles_custom(temp_board)
        draw_ai_selection()
        draw_side_scores()
        draw_turn_info()
        pygame.display.flip()
        pygame.time.delay(ANIM_DELAY)


# =====================================================
# IA SELECTION
# =====================================================
def draw_ai_selection():
    if not ai_selected_pit:
        return
    if pygame.time.get_ticks() - ai_show_time > AI_DISPLAY_DURATION:
        return

    rect = ALL_PITS.get(ai_selected_pit)
    if rect:
        pygame.draw.rect(screen, (255, 215, 0), rect, 5)

# =====================================================
# SCORES + TURN
# =====================================================
def draw_side_scores():
    h = engine.game.state.board[engine.game.HUMAN_STORE]
    c = engine.game.state.board[engine.game.COMPUTER_STORE]

    screen.blit(INFO_FONT.render(f"AI Score : {c}", True, (0,0,0)), (30,100))
    screen.blit(INFO_FONT.render(f"Your Score : {h}", True, (0,0,0)),
                (WIDTH - 220, 500))

def draw_turn_info():
    if selected_mode == "AI_AI":
        text = "AI 1 turn" if engine.turn == MAX else "AI 2 turn"
    else:
        text = "Your turn" if engine.turn == MIN else "AI turn"

    txt = TURN_FONT.render(text, True, (20,20,20))
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 20))

# =====================================================
# SCORE SCREEN
# =====================================================
def draw_score_screen():
    screen.blit(score_img, (0, 0))

    h_score = engine.game.state.board[engine.game.HUMAN_STORE]
    c_score = engine.game.state.board[engine.game.COMPUTER_STORE]

    txt_h = FONT.render(f"{h_score}", True, (0, 0, 0))
    txt_c = FONT.render(f"{c_score}", True, (0, 0, 0))

    screen.blit(txt_h, (WIDTH//2 - txt_h.get_width()//2 + 80, 260))
    screen.blit(txt_c, (WIDTH//2 - txt_c.get_width()//2 + 80, 340))

    if h_score > c_score:
        result = "PLAYER 1 WINS"
    elif c_score > h_score:
        result = "AI WINS"
    else:
        result = "DRAW"

    result_txt = FONT.render(result, True, (180, 0, 0))
    screen.blit(result_txt,
                (WIDTH//2 - result_txt.get_width()//2, 150))




# =====================================================
# MAIN LOOP
# =====================================================
running = True
while running:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        elif e.type == pygame.MOUSEBUTTONDOWN:
            x, y = e.pos

            # ---------------- START SCREEN ----------------
            if current_screen == START and START_BUTTON.collidepoint(x, y):
                click_sound.play()
                current_screen = INSTRUCTION

            # --------------- INSTRUCTION SCREEN -----------
            elif current_screen == INSTRUCTION and CONTINUE_BUTTON.collidepoint(x, y):
                click_sound.play()
                current_screen = MODE

            # ---------------- MODE SCREEN -----------------
            elif current_screen == MODE:
                if LEFT_BUTTON.collidepoint(x, y):
                    click_sound.play()
                    selected_mode = "HUMAN_AI"
                    current_screen = TOUR
                elif RIGHT_BUTTON.collidepoint(x, y):
                    click_sound.play()
                    selected_mode = "AI_AI"
                    engine = Play("AI_AI", False, 6)
                    engine.turn = MAX
                    current_screen = GAME

            # ---------------- TOUR SCREEN -----------------
            elif current_screen == TOUR:
                engine = Play("HUMAN_AI", LEFT_BUTTON.collidepoint(x, y), 6)
                current_screen = GAME

            # ---------------- GAME SCREEN -----------------
            elif current_screen == GAME and selected_mode == "HUMAN_AI" and engine.turn == MIN:
                for p, r in PITS.items():
                    if r.collidepoint(x, y):
                        engine.human_move(p)
                        animate_move(p, engine.last_move_path)

            # ---------------- SCORE SCREEN ----------------
            elif current_screen == SCORE:
                if OK_BUTTON.collidepoint(x, y):
                    click_sound.play()
                    current_screen = PLAY_AGAIN

            # ------------- PLAY_AGAIN SCREEN -------------
            elif current_screen == PLAY_AGAIN:
                if PLAY_AGAIN_BUTTON.collidepoint(x, y):
                    click_sound.play()
                    # Relancer le jeu
                    engine = Play(selected_mode, False, 6)
                    engine.turn = MIN if selected_mode == "HUMAN_AI" else MAX
                    current_screen = GAME
                elif HOME_BUTTON.collidepoint(x, y):
                    click_sound.play()
                    # Retour au menu START
                    current_screen = START

    # ================= IA =================
    if current_screen == GAME and engine and not engine.is_game_over():

        if engine.turn == MAX:
            pit = engine.ai_move(
                engine.game.COMPUTER_PITS,
                engine.game.COMPUTER_STORE,
                engine.game.HUMAN_STORE
            )
            ai_selected_pit = pit
            ai_show_time = pygame.time.get_ticks()
            animate_move(pit, engine.last_move_path)

        elif selected_mode == "AI_AI" and engine.turn == MIN:
            pit = engine.ai_move(
                engine.game.HUMAN_PITS,
                engine.game.HUMAN_STORE,
                engine.game.COMPUTER_STORE
            )
            ai_selected_pit = pit
            ai_show_time = pygame.time.get_ticks()
            animate_move(pit, engine.last_move_path)

    if current_screen == GAME and engine and engine.is_game_over():
        current_screen = SCORE

    # ================= DRAW =================
    if current_screen == GAME:
        screen.blit(board_img, (0, 0))
        draw_marbles()
        draw_hover_info()
        draw_ai_selection()
        draw_side_scores()
        draw_turn_info()

    elif current_screen == SCORE:
        draw_score_screen()
        # DEBUG : afficher le rectangle OK si besoin
        # pygame.draw.rect(screen, (255,0,0), OK_BUTTON, 2)

    elif current_screen == PLAY_AGAIN:
        screen.blit(play_again_img, (0, 0))
        # DEBUG : afficher rectangles si besoin
        # pygame.draw.rect(screen, (0,255,0), PLAY_AGAIN_BUTTON, 2)
        # pygame.draw.rect(screen, (0,0,255), HOME_BUTTON, 2)

    elif current_screen == SPLASH:
        screen.blit(splash_img, (0, 0))
        if time.time() - splash_start > 3:
            current_screen = START

    elif current_screen == START:
        screen.blit(start_img, (0, 0))

    elif current_screen == INSTRUCTION:
        screen.blit(instruction_img, (0, 0))

    elif current_screen == MODE:
        screen.blit(mode_img, (0, 0))

    elif current_screen == TOUR:
        screen.blit(tour_img, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()