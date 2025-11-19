import pygame 
import sys
import random
import math

pygame.init()

# --- Screen setup ---
WIDTH, HEIGHT = 600, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tic Tac Toe Ultimate")
clock = pygame.time.Clock()

# --- Colors ---
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
CURSOR_COLOR = (0, 255, 0)
BUTTON_COLOR = (0, 102, 204)
BUTTON_HOVER = (0, 153, 255)
TEXT_COLOR = (255, 255, 255)
WIN_TEXT = (255, 215, 0)

# --- Board setup ---
BOARD_ROWS, BOARD_COLS = 3, 3
LINE_WIDTH = 15
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE_RATIO = 0.2

# --- Fonts ---
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 70)

# --- Sounds ---
click_sound = pygame.mixer.Sound("click.wav")
win_sound = pygame.mixer.Sound("win.wav")
click_sound.set_volume(0.5)
win_sound.set_volume(0.8)

# --- Game variables ---
board = [[None]*BOARD_COLS for _ in range(BOARD_ROWS)]
player = 'X'
game_over = False
main_menu = True
ai_menu = False
vs_ai = False
ai_level = "Easy"
winner = None
x_wins = 0
o_wins = 0
selected_cell = [0, 0]
keyboard_active = False
animations = []
ignore_mouse_clicks = False
# --- Opening animation ---
opening = True
opening_start = pygame.time.get_ticks()
opening_text = "TIC TAC TOE"
LETTER_MS = 120  # milliseconds per letter
BOUNCE_MS = 400  # bounce duration per letter
OPEN_HOLD_MS = 700  # hold after full text appears
# style
LETTER_COLORS = [WIN_TEXT, CIRCLE_COLOR, CROSS_COLOR, BUTTON_HOVER, TEXT_COLOR]

# --- Functions ---
def draw_text(text, size, color, x, y):
    font_obj = pygame.font.Font(None, size)
    label = font_obj.render(text, True, color)
    rect = label.get_rect(center=(x, y))
    screen.blit(label, rect)

def draw_lines():
    SQUARE_SIZE = min(screen.get_width(), screen.get_height()-150)//3
    board_origin = ((screen.get_width() - SQUARE_SIZE*3)//2, 50)
    for i in range(1, 3):
        # Horizontal
        pygame.draw.line(screen, LINE_COLOR,
                         (board_origin[0], board_origin[1]+i*SQUARE_SIZE),
                         (board_origin[0]+SQUARE_SIZE*3, board_origin[1]+i*SQUARE_SIZE),
                         LINE_WIDTH)
        # Vertical
        pygame.draw.line(screen, LINE_COLOR,
                         (board_origin[0]+i*SQUARE_SIZE, board_origin[1]),
                         (board_origin[0]+i*SQUARE_SIZE, board_origin[1]+SQUARE_SIZE*3),
                         LINE_WIDTH)
    return board_origin, SQUARE_SIZE

def draw_figures(board_origin, SQUARE_SIZE):
    SPACE = int(SQUARE_SIZE*SPACE_RATIO)
    CIRCLE_RADIUS = SQUARE_SIZE//3

    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            center = (board_origin[0] + col*SQUARE_SIZE + SQUARE_SIZE//2,
                      board_origin[1] + row*SQUARE_SIZE + SQUARE_SIZE//2)
            for anim in animations[:]:
                r, c, kind, progress = anim
                if r == row and c == col:
                    if kind == 'O':
                        radius = int(CIRCLE_RADIUS * progress)
                        pygame.draw.circle(screen, CIRCLE_COLOR, center, radius, CIRCLE_WIDTH)
                    else:
                        line_len = int((SQUARE_SIZE-2*SPACE) * progress)
                        pygame.draw.line(screen, CROSS_COLOR,
                                         (board_origin[0]+col*SQUARE_SIZE+SPACE, board_origin[1]+row*SQUARE_SIZE+SPACE),
                                         (board_origin[0]+col*SQUARE_SIZE+SPACE+line_len, board_origin[1]+row*SQUARE_SIZE+SPACE+line_len),
                                         CROSS_WIDTH)
                        pygame.draw.line(screen, CROSS_COLOR,
                                         (board_origin[0]+col*SQUARE_SIZE+SPACE, board_origin[1]+row*SQUARE_SIZE+SQUARE_SIZE-SPACE),
                                         (board_origin[0]+col*SQUARE_SIZE+SPACE+line_len, board_origin[1]+row*SQUARE_SIZE+SQUARE_SIZE-SPACE-line_len),
                                         CROSS_WIDTH)
                    anim[3] += 0.1
                    if anim[3] >= 1:
                        animations.remove(anim)
            if board[row][col] == 'O' and all(not(a[0]==row and a[1]==col) for a in animations):
                pygame.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X' and all(not(a[0]==row and a[1]==col) for a in animations):
                pygame.draw.line(screen, CROSS_COLOR,
                                 (board_origin[0]+col*SQUARE_SIZE+SPACE, board_origin[1]+row*SQUARE_SIZE+SQUARE_SIZE-SPACE),
                                 (board_origin[0]+col*SQUARE_SIZE+SQUARE_SIZE-SPACE, board_origin[1]+row*SQUARE_SIZE+SPACE),
                                 CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (board_origin[0]+col*SQUARE_SIZE+SPACE, board_origin[1]+row*SQUARE_SIZE+SPACE),
                                 (board_origin[0]+col*SQUARE_SIZE+SQUARE_SIZE-SPACE, board_origin[1]+row*SQUARE_SIZE+SQUARE_SIZE-SPACE),
                                 CROSS_WIDTH)
    # Keyboard cursor
    if keyboard_active and not game_over:
        r, c = selected_cell
        pygame.draw.rect(screen, CURSOR_COLOR,
                         (board_origin[0]+c*SQUARE_SIZE+5, board_origin[1]+r*SQUARE_SIZE+5,
                          SQUARE_SIZE-10, SQUARE_SIZE-10), 3)

def check_winner(player):
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] == player:
            return True
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] == player:
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False

def is_draw():
    return all(all(cell is not None for cell in row) for row in board)

def get_winning_cells(player):
    """Return list of three (row,col) tuples for the winning line for player, or None."""
    # rows
    for row in range(BOARD_ROWS):
        if board[row][0] == board[row][1] == board[row][2] == player:
            return [(row, 0), (row, 1), (row, 2)]
    # cols
    for col in range(BOARD_COLS):
        if board[0][col] == board[1][col] == board[2][col] == player:
            return [(0, col), (1, col), (2, col)]
    # diag TL-BR
    if board[0][0] == board[1][1] == board[2][2] == player:
        return [(0, 0), (1, 1), (2, 2)]
    # diag TR-BL
    if board[0][2] == board[1][1] == board[2][0] == player:
        return [(0, 2), (1, 1), (2, 0)]
    return None

def restart_game(keep_scores=True):
    global board, player, game_over, winner, animations, selected_cell, keyboard_active
    board = [[None]*BOARD_COLS for _ in range(BOARD_ROWS)]
    player = 'X'
    game_over = False
    winner = None
    animations = []
    selected_cell = [0, 0]
    keyboard_active = False
    if not keep_scores:
        global x_wins, o_wins
        x_wins, o_wins = 0, 0

def draw_button(text, x, y, w, h, hover):
    color = BUTTON_HOVER if hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    label = font.render(text, True, TEXT_COLOR)
    label_rect = label.get_rect(center=(x+w//2, y+h//2))
    screen.blit(label, label_rect)
    return pygame.Rect(x, y, w, h)

def draw_circle_button(text, cx, cy, radius, hover):
    color = BUTTON_HOVER if hover else BUTTON_COLOR
    pygame.draw.circle(screen, color, (cx, cy), radius)
    label = font.render(text, True, TEXT_COLOR)
    label_rect = label.get_rect(center=(cx, cy))
    screen.blit(label, label_rect)
    return (cx, cy, radius)
 

def centered_button(text, y, w=200, h=60):
    x = (screen.get_width() - w)//2
    mouse = pygame.mouse.get_pos()
    hover = x < mouse[0] < x+w and y < mouse[1] < y+h
    return draw_button(text, x, y, w, h, hover)

def ai_move():
    empty = [(r,c) for r in range(3) for c in range(3) if board[r][c] is None]
    if ai_level=="Easy":
        return random.choice(empty)
    elif ai_level=="Medium":
        for r,c in empty:
            board[r][c]='O'
            if check_winner('O'):
                board[r][c]=None
                return (r,c)
            board[r][c]='X'
            if check_winner('X'):
                board[r][c]=None
                return (r,c)
            board[r][c]=None
        return random.choice(empty)
    else:
        best_score=-float('inf')
        best_move=None
        for r,c in empty:
            board[r][c]='O'
            score=minimax(board,0,False)
            board[r][c]=None
            if score>best_score:
                best_score=score
                best_move=(r,c)
        return best_move

def minimax(board_state, depth, is_max):
    if check_winner('O'): return 1
    if check_winner('X'): return -1
    if is_draw(): return 0
    empty=[(r,c) for r in range(3) for c in range(3) if board_state[r][c] is None]
    if is_max:
        best=-float('inf')
        for r,c in empty:
            board_state[r][c]='O'
            best=max(best,minimax(board_state,depth+1,False))
            board_state[r][c]=None
        return best
    else:
        best=float('inf')
        for r,c in empty:
            board_state[r][c]='X'
            best=min(best,minimax(board_state,depth+1,True))
            board_state[r][c]=None
        return best

# --- Main loop ---
while True:
    screen.fill(BG_COLOR)
    mouse = pygame.mouse.get_pos()

    # Opening animation: type out the title letter-by-letter. Click or press any key to skip.
    if opening:
        elapsed = pygame.time.get_ticks() - opening_start
        # allow skip
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                opening = False
        # compute how many letters to show
        letters = min(len(opening_text), max(0, elapsed // LETTER_MS))
        # when full text shown long enough, end animation
        if letters >= len(opening_text) and elapsed >= len(opening_text)*LETTER_MS + OPEN_HOLD_MS:
            opening = False

        # draw animated background
        screen.fill(BG_COLOR)
        # background expanding circle
        max_r = min(screen.get_width(), screen.get_height())
        bg_radius = int(min(max_r//2, (elapsed / (len(opening_text)*LETTER_MS + OPEN_HOLD_MS)) * max_r))
        pygame.draw.circle(screen, (20, 120, 110), (screen.get_width()//2, screen.get_height()//2), bg_radius, width=0)

        # draw each visible letter with a small bounce and color
        total_width = 0
        sizes = []
        for ch in opening_text[:letters]:
            s = big_font.render(ch, True, TEXT_COLOR)
            sizes.append(s)
            total_width += s.get_width()

        x = screen.get_width()//2 - total_width//2
        for i, surf in enumerate(sizes):
            # per-letter bounce offset
            letter_elapsed = elapsed - i*LETTER_MS
            bounce = 0
            if letter_elapsed > 0:
                t = (letter_elapsed % BOUNCE_MS) / BOUNCE_MS
                bounce = int(math.sin(t*math.pi) * 12)
            # color cycle
            color = LETTER_COLORS[i % len(LETTER_COLORS)]
            # render letter with color
            ch_text = big_font.render(opening_text[i], True, color)
            rect = ch_text.get_rect()
            rect.topleft = (x, screen.get_height()//2 - rect.height//2 - bounce)
            screen.blit(ch_text, rect)
            x += rect.width

        pygame.display.update()
        clock.tick(60)
        continue

    if main_menu:
        draw_text("TIC TAC TOE", 80, TEXT_COLOR, screen.get_width()//2, 200)
        pvp_btn = centered_button("2 Player", 350)
        ai_btn = centered_button("Play vs AI", 450)
        quit_btn = centered_button("Quit", 550)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if pvp_btn.collidepoint(event.pos):
                    main_menu=False
                    vs_ai=False
                    # Starting a new game from menu resets the scorecard
                    restart_game(keep_scores=False)
                    ignore_mouse_clicks = True
                elif ai_btn.collidepoint(event.pos):
                    main_menu=False
                    ai_menu=True
                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    elif ai_menu:
        draw_text("Select AI Level", 60, TEXT_COLOR, screen.get_width()//2, 200)
        easy_btn = centered_button("Easy", 350)
        medium_btn = centered_button("Medium", 450)
        hard_btn = centered_button("Hard", 550)
        back_btn = centered_button("Back", 650)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if easy_btn.collidepoint(event.pos):
                    ai_level="Easy"
                    vs_ai=True
                    ai_menu=False
                    # Starting a new AI game from menu resets the scorecard
                    restart_game(keep_scores=False)
                    ignore_mouse_clicks = True
                elif medium_btn.collidepoint(event.pos):
                    ai_level="Medium"
                    vs_ai=True
                    ai_menu=False
                    restart_game(keep_scores=False)
                    ignore_mouse_clicks = True
                elif hard_btn.collidepoint(event.pos):
                    ai_level="Hard"
                    vs_ai=True
                    ai_menu=False
                    restart_game(keep_scores=False)
                    ignore_mouse_clicks = True
                elif back_btn.collidepoint(event.pos):
                    ai_menu=False
                    main_menu=True

    else:
        board_origin, SQUARE_SIZE = draw_lines()
        draw_figures(board_origin, SQUARE_SIZE)
        draw_text(f"Score - X: {x_wins}  O: {o_wins}", 40, TEXT_COLOR, screen.get_width()//2, screen.get_height()-90)
        # Restart button shown on the right side
        restart_x = screen.get_width() - 120
        restart_y = screen.get_height() - 70
        restart_hover = restart_x < mouse[0] < restart_x + 100 and restart_y < mouse[1] < restart_y + 50
        restart_btn = draw_button("Restart", restart_x, restart_y, 100, 50, restart_hover)
        back_btn = draw_button("Back", 10, screen.get_height()-70, 100, 50, 10 < mouse[0] < 110 and screen.get_height()-70 < mouse[1] < screen.get_height()-20)

        if game_over:
            msg = "Draw!" if winner=="Draw" else f"Player {winner} Wins!"
            draw_text(msg, 60, WIN_TEXT, screen.get_width()//2, screen.get_height()-150)
            # Draw rectangular Play Again button (centered) when game over
            play_y = screen.get_height() - 240
            play_btn = centered_button("Play Again", play_y, w=220, h=70)
            # Draw winning line for X or O (slope/straight)
            if winner in ("X", "O"):
                win_cells = get_winning_cells(winner)
                if win_cells:
                    (r0, c0) = win_cells[0]
                    (r2, c2) = win_cells[2]
                    start = (board_origin[0] + c0 * SQUARE_SIZE + SQUARE_SIZE//2,
                             board_origin[1] + r0 * SQUARE_SIZE + SQUARE_SIZE//2)
                    end = (board_origin[0] + c2 * SQUARE_SIZE + SQUARE_SIZE//2,
                           board_origin[1] + r2 * SQUARE_SIZE + SQUARE_SIZE//2)
                    # draw a thick line with WIN_TEXT color
                    pygame.draw.line(screen, WIN_TEXT, start, end, max(8, LINE_WIDTH))

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If the user moves or clicks the mouse, switch out of keyboard mode
            if event.type==pygame.MOUSEMOTION:
                keyboard_active = False
            if event.type==pygame.MOUSEBUTTONDOWN:
                keyboard_active = False
                # Ignore clicks if flagged elsewhere
                if restart_btn.collidepoint(event.pos):
                    # Restart pressed in-game: reset scorecard
                    restart_game(keep_scores=False)
                # Play Again rectangular button click: if visible and clicked, preserve scores
                if game_over and play_btn.collidepoint(event.pos):
                    restart_game(keep_scores=True)
                    ignore_mouse_clicks = True
                if back_btn.collidepoint(event.pos):
                    main_menu=True
                    # Back pressed in-game: reset scorecard
                    restart_game(keep_scores=False)
            if event.type==pygame.MOUSEBUTTONUP:
                # Allow mouse clicks again after the menu-selection click is released
                ignore_mouse_clicks = False
            if event.type==pygame.KEYDOWN:
                keyboard_active=True
                if event.key==pygame.K_UP:
                    selected_cell[0]=(selected_cell[0]-1)%3
                elif event.key==pygame.K_DOWN:
                    selected_cell[0]=(selected_cell[0]+1)%3
                elif event.key==pygame.K_LEFT:
                    selected_cell[1]=(selected_cell[1]-1)%3
                elif event.key==pygame.K_RIGHT:
                    selected_cell[1]=(selected_cell[1]+1)%3
                elif event.key==pygame.K_RETURN:
                    r,c = selected_cell
                    if board[r][c] is None and not game_over:
                        animations.append([r,c,player,0])
                        board[r][c]=player
                        click_sound.play()
                        if check_winner(player):
                            win_sound.play()
                            winner=player
                            game_over=True
                            if player=='X': x_wins+=1
                            else: o_wins+=1
                        elif is_draw():
                            game_over=True
                            winner="Draw"
                        else:
                            player='O' if player=='X' else 'X'

        # Mouse input (always allowed; moving/clicking the mouse disables keyboard mode)
        if not game_over:
            if pygame.mouse.get_pressed()[0] and not ignore_mouse_clicks:
                x, y = pygame.mouse.get_pos()
                if board_origin[1] <= y <= board_origin[1]+SQUARE_SIZE*3:
                    col = (x - board_origin[0]) // SQUARE_SIZE
                    row = (y - board_origin[1]) // SQUARE_SIZE
                    if 0 <= row < 3 and 0 <= col < 3:
                        if board[row][col] is None:
                            animations.append([row,col,player,0])
                            board[row][col]=player
                            click_sound.play()
                            if check_winner(player):
                                win_sound.play()
                                winner=player
                                game_over=True
                                if player=='X': x_wins+=1
                                else: o_wins+=1
                            elif is_draw():
                                game_over=True
                                winner="Draw"
                            else:
                                player='O' if player=='X' else 'X'

        # AI move
        if vs_ai and player=='O' and not game_over:
            pygame.time.delay(200)
            r,c = ai_move()
            animations.append([r,c,player,0])
            board[r][c]=player
            click_sound.play()
            if check_winner(player):
                win_sound.play()
                winner=player
                game_over=True
                if player=='X': x_wins+=1
                else: o_wins+=1
            elif is_draw():
                game_over=True
                winner="Draw"
            else:
                player='X'

    pygame.display.update()
    clock.tick(60)
