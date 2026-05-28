import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math
import random

from entities import Player, SoundWave, Wall, Fruit, Star, Enemy, Camera, Exit, CELL_SIZE
from levels import get_level, MAX_LEVEL

# Global Config
WIDTH, HEIGHT = 800, 600
FPS = 60

def draw_text(x, y, text, font, color=(255, 255, 255)):
    """Renderiza texto de Pygame y lo dibuja en el contexto de OpenGL como píxeles 2D"""
    text_surface = font.render(text, True, color)
    # Pygame dibuja de arriba a abajo, OpenGL de abajo a arriba
    text_data = pygame.image.tostring(text_surface, "RGBA", True)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDrawPixels(
        text_surface.get_width(),
        text_surface.get_height(),
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        text_data
    )
    glDisable(GL_BLEND)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_bar(x, y, bar_w, bar_h, fill_ratio, fill_color, bg_color=(30, 30, 30)):
    """Dibuja una barra de progreso en coordenadas de pantalla (0-255 para colores)"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glColor3f(bg_color[0]/255, bg_color[1]/255, bg_color[2]/255)
    glBegin(GL_QUADS)
    glVertex2f(x,         y)
    glVertex2f(x + bar_w, y)
    glVertex2f(x + bar_w, y + bar_h)
    glVertex2f(x,         y + bar_h)
    glEnd()

    fill_w = bar_w * max(0.0, min(1.0, fill_ratio))
    glColor3f(fill_color[0]/255, fill_color[1]/255, fill_color[2]/255)
    glBegin(GL_QUADS)
    glVertex2f(x,          y)
    glVertex2f(x + fill_w, y)
    glVertex2f(x + fill_w, y + bar_h)
    glVertex2f(x,          y + bar_h)
    glEnd()

    glDisable(GL_BLEND)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid(map_width, map_height, step=100):
    glColor3f(0.06, 0.06, 0.06)
    glBegin(GL_LINES)
    for x in range(0, map_width + 1, step):
        glVertex2f(x, 0)
        glVertex2f(x, map_height)
    for y in range(0, map_height + 1, step):
        glVertex2f(0, y)
        glVertex2f(map_width, y)
    glEnd()

def init_opengl():
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0.02, 0.02, 0.02, 1.0)

def create_nav_grid(map_w, map_h, walls, cell_size):
    """Convierte el mapa continuo en una matriz discreta de 0 y 1s para navegación"""
    cols = map_w // cell_size
    rows = map_h // cell_size
    grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            cell_x = c * cell_size
            cell_y = r * cell_size
            for wall in walls:
                if (cell_x < wall.x + wall.w and cell_x + cell_size > wall.x and
                        cell_y < wall.y + wall.h and cell_y + cell_size > wall.y):
                    grid[r][c] = 1
                    break
    return grid

def main():
    pygame.init()
    pygame.font.init()

    display_flags = DOUBLEBUF | OPENGL
    pygame.display.set_mode((WIDTH, HEIGHT), display_flags)
    pygame.display.set_caption("Resonance - Entregable 3")

    init_opengl()
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("Courier", 72, bold=True)
    font_menu  = pygame.font.SysFont("Courier", 36, bold=True)
    font_hud   = pygame.font.SysFont("Arial",   24, bold=True)

    MAP_WIDTH, MAP_HEIGHT = 1600, 1200

    # VARIABLES GLOBALES DEL JUEGO
    state         = "MENU"
    menu_idx      = 0
    high_score    = 0
    current_score = 0
    game_started  = False
    current_level = 1

    # VARIABLES SESIÓN ACTUAL
    player              = None
    camera              = None
    waves               = []
    fruits              = []
    stars               = []
    enemies             = []
    walls               = []
    nav_grid            = []
    exit_obj            = None
    survival_mode       = False
    enemy_spawn_timer    = 0
    enemy_spawn_interval = 0

    def reset_game():
        nonlocal player, camera, waves, fruits, stars, enemies, walls, nav_grid, exit_obj
        nonlocal survival_mode, enemy_spawn_timer, enemy_spawn_interval
        data     = get_level(current_level)
        walls    = data['walls']
        fruits   = data['fruits']
        stars    = data['stars']
        enemies  = data['enemies']
        exit_obj = data['exit']
        sx, sy   = data['player_start']
        player   = Player(sx, sy)
        camera   = Camera(WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT)
        waves    = []
        nav_grid = create_nav_grid(MAP_WIDTH, MAP_HEIGHT, walls, CELL_SIZE)
        survival_mode = data.get('survival', False)
        enemy_spawn_interval = 1200 if survival_mode else 0
        enemy_spawn_timer    = enemy_spawn_interval

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == KEYDOWN:
                if state == "PLAYING":
                    if event.key == K_ESCAPE:
                        state = "MENU"
                    elif event.key == K_SPACE:
                        waves.append(SoundWave(player.x, player.y))

                elif state == "MENU":
                    if event.key == K_UP or event.key == K_DOWN:
                        menu_idx = 1 - menu_idx
                    elif event.key == K_RETURN:
                        if menu_idx == 0:
                            current_level = 1
                            reset_game()
                            game_started = True
                            state = "PLAYING"
                        elif menu_idx == 1 and game_started:
                            state = "PLAYING"

                elif state == "GAME_OVER":
                    if event.key == K_RETURN:
                        state = "MENU"

                elif state == "WIN":
                    if event.key == K_RETURN:
                        if current_level < MAX_LEVEL:
                            current_level += 1
                            reset_game()
                            state = "PLAYING"
                        else:
                            state = "MENU"

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if state == "MENU":
            draw_text(WIDTH//2 - 200, HEIGHT - 150, "RESONANCE", font_title, color=(0, 255, 255))
            c_new  = (255, 255, 0) if menu_idx == 0 else (100, 100, 100)
            c_cont = (255, 255, 0) if menu_idx == 1 else (100, 100, 100)
            if not game_started:
                c_cont = (40, 40, 40)
            draw_text(WIDTH//2 - 150, HEIGHT//2,      "> Nueva Partida", font_menu, color=c_new)
            draw_text(WIDTH//2 - 150, HEIGHT//2 - 50, "> Continuar",     font_menu, color=c_cont)

        elif state == "WIN":
            win_title = "NIVEL COMPLETADO"
            win_score = f"Puntuacion: {player.score}"
            win_hint  = "Presiona ENTER para volver al Menu"
            draw_text(WIDTH//2 - font_title.size(win_title)[0]//2, HEIGHT - 200, win_title, font_title, color=(0, 255, 0))
            draw_text(WIDTH//2 - font_menu.size(win_score)[0]//2,  HEIGHT//2,    win_score, font_menu,  (255, 255, 255))
            draw_text(WIDTH//2 - font_hud.size(win_hint)[0]//2,    100,          win_hint,  font_hud,   (150, 150, 150))

        elif state == "GAME_OVER":
            draw_text(WIDTH//2 - 200, HEIGHT - 200, "GAME OVER",                          font_title, color=(255, 0, 0))
            draw_text(WIDTH//2 - 150, HEIGHT//2,    f"Puntuacion Final: {current_score}", font_menu,  (255, 255, 255))
            draw_text(WIDTH//2 - 150, HEIGHT//2 - 50, f"Max. Historico: {high_score}",   font_menu,  (0, 255, 0))
            draw_text(WIDTH//2 - 220, 100, "Presiona ENTER para volver al Menu",          font_hud,   (150, 150, 150))

        elif state == "PLAYING":
            keys = pygame.key.get_pressed()
            player.update(keys, MAP_WIDTH, MAP_HEIGHT, walls)
            camera.update(player.x, player.y)

            # Recolección y reaparición de frutas
            for fruit in fruits:
                if fruit.active and math.hypot(player.x - fruit.x, player.y - fruit.y) < (player.r + fruit.r):
                    fruit.active = False
                    player.score += 10
                    if fruit.respawn_delay > 0:
                        fruit.respawn_timer = fruit.respawn_delay
                fruit.update()

            for star in stars:
                if star.active and math.hypot(player.x - star.x, player.y - star.y) < (player.r + star.r):
                    star.active = False
                    player.is_hunter = True
                    player.hunter_timer = FPS * 10

            # Enemigos
            for enemy in enemies:
                enemy.update(nav_grid)
                if enemy.active:
                    dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
                    if dist < (player.r + enemy.r):
                        if player.is_hunter:
                            enemy.active = False
                            player.score += 50
                        else:
                            current_score = player.score
                            if current_score > high_score:
                                high_score = current_score
                            game_started = False
                            menu_idx = 0
                            state = "GAME_OVER"

            # Ondas y ecolocalización
            for wave in waves:
                wave.update()
                for enemy in enemies:
                    dist = math.hypot(wave.x - enemy.x, wave.y - enemy.y)
                    if abs(dist - wave.radius) < 15.0:
                        enemy.calculate_path(wave.x, wave.y, nav_grid)
                        enemy.state = 'INVESTIGATING'
                        # La onda "ilumina" al enemigo por 3 segundos
                        enemy.visibility_timer = FPS * 3

            waves = [w for w in waves if w.active]
            for wall in walls:
                wall.update(waves)

            # Salida (no existe en modo supervivencia)
            all_fruits = False
            if exit_obj is not None:
                all_fruits = all(not f.active for f in fruits)
                exit_obj.update(waves, all_fruits)
                if all_fruits:
                    dist = math.hypot(player.x - exit_obj.x, player.y - exit_obj.y)
                    if dist < (player.r + exit_obj.r):
                        state = "WIN"

            # Spawning progresivo de enemigos en supervivencia
            if survival_mode:
                enemy_spawn_timer -= 1
                if enemy_spawn_timer <= 0:
                    edge = random.randint(0, 3)
                    if edge == 0:
                        sx, sy = random.randint(60, 1540), 60
                    elif edge == 1:
                        sx, sy = random.randint(60, 1540), 1140
                    elif edge == 2:
                        sx, sy = 60, random.randint(60, 1140)
                    else:
                        sx, sy = 1540, random.randint(60, 1140)
                    new_enemy = Enemy(sx, sy)
                    new_enemy.visibility_timer = FPS * 3
                    enemies.append(new_enemy)
                    enemy_spawn_interval = max(300, int(enemy_spawn_interval * 0.95))
                    enemy_spawn_timer = enemy_spawn_interval

            # Renderizado
            camera.apply()

            draw_grid(MAP_WIDTH, MAP_HEIGHT)
            glColor3f(0.15, 0.15, 0.15)
            glBegin(GL_LINE_LOOP)
            glVertex2f(0, 0)
            glVertex2f(MAP_WIDTH, 0)
            glVertex2f(MAP_WIDTH, MAP_HEIGHT)
            glVertex2f(0, MAP_HEIGHT)
            glEnd()

            for wall in walls:
                wall.draw()
            for fruit in fruits:
                fruit.draw()
            for star in stars:
                star.draw()
            for wave in waves:
                wave.draw()
            for enemy in enemies:
                enemy.draw(player.is_hunter)
            if exit_obj is not None:
                exit_obj.draw(all_fruits)
            player.draw()

            # HUD
            draw_text(20, HEIGHT - 40, f"SCORE: {player.score}", font_hud, color=(0, 255, 0))
            if player.is_hunter:
                draw_text(WIDTH//2 - 60, HEIGHT - 40, "MODO CAZADOR", font_hud, (255, 255, 0))
            if survival_mode:
                active_count = sum(1 for e in enemies if e.active)
                draw_text(WIDTH - 230, HEIGHT - 40, f"ENEMIGOS: {active_count}", font_hud, color=(255, 50, 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
