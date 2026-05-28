from OpenGL.GL import *
from pygame.locals import *
import math
import heapq
import random

CELL_SIZE = 40

def draw_circle(x, y, r, color, segments=32):
    """Dibuja un círculo aproximado con polígonos"""
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(segments + 1):
        angle = i * (2.0 * math.pi / segments)
        glVertex2f(x + r * math.cos(angle), y + r * math.sin(angle))
    glEnd()

def draw_empty_circle(x, y, r, color, line_width=2.0, segments=64):
    """Dibuja anillos (representando las ondas)"""
    glLineWidth(line_width)
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        angle = i * (2.0 * math.pi / segments)
        glVertex2f(x + r * math.cos(angle), y + r * math.sin(angle))
    glEnd()
    glLineWidth(1.0)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_r = 24
        self.r = 24

        # Física de mov.
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = 8.0
        self.acceleration = 1.2
        self.friction = 0.92

        self.color = (0.0, 0.46, 1.0)
        self.time_alive = 0

        # Sistema de Puntuación
        self.score = 0
        self.is_hunter = False
        self.hunter_timer = 0
        self.base_color = (0.0, 0.46, 1.0)

    def update(self, keys, width, height, walls):
        # Estado de ataque (Power-Up)
        if self.is_hunter:
            self.hunter_timer -= 1
            self.color = (1.0, 1.0, 0.0)
            if self.hunter_timer <= 0:
                self.is_hunter = False
                self.color = self.base_color
        else:
            self.color = self.base_color

        self.time_alive += 1
        self.r = self.base_r + math.sin(self.time_alive * 0.1) * 0.8

        if keys[K_w] or keys[K_UP]:
            self.vy += self.acceleration
        if keys[K_s] or keys[K_DOWN]:
            self.vy -= self.acceleration
        if keys[K_a] or keys[K_LEFT]:
            self.vx -= self.acceleration
        if keys[K_d] or keys[K_RIGHT]:
            self.vx += self.acceleration

        self.vx *= self.friction
        self.vy *= self.friction

        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            ratio = self.max_speed / speed
            self.vx *= ratio
            self.vy *= ratio

        # COLISIONES
        self.x += self.vx
        for wall in walls:
            if self.check_collision(wall):
                if self.vx > 0:
                    self.x = wall.x - self.base_r
                elif self.vx < 0:
                    self.x = wall.x + wall.w + self.base_r
                self.vx = 0

        self.y += self.vy
        for wall in walls:
            if self.check_collision(wall):
                if self.vy > 0:
                    self.y = wall.y - self.base_r
                elif self.vy < 0:
                    self.y = wall.y + wall.h + self.base_r
                self.vy = 0

        # Bordes del mapa
        if self.x - self.base_r < 0:
            self.x = self.base_r
            self.vx *= -0.4
        if self.x + self.base_r > width:
            self.x = width - self.base_r
            self.vx *= -0.4
        if self.y - self.base_r < 0:
            self.y = self.base_r
            self.vy *= -0.4
        if self.y + self.base_r > height:
            self.y = height - self.base_r
            self.vy *= -0.4

    def draw(self):
        draw_circle(self.x, self.y, self.r, self.color)

    def check_collision(self, wall):
        closest_x = max(wall.x, min(self.x, wall.x + wall.w))
        closest_y = max(wall.y, min(self.y, wall.y + wall.h))
        dx = self.x - closest_x
        dy = self.y - closest_y
        return (dx**2 + dy**2) < (self.base_r ** 2)


class SoundWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 24.0
        self.max_radius = 500.0
        self.expansion_speed = 12.0
        self.active = True
        self.base_color = (0.0, 1.0, 1.0)

    def update(self):
        self.radius += self.expansion_speed
        if self.radius > self.max_radius:
            self.active = False

    def draw(self):
        intensity = max(0.0, 1.0 - (self.radius / self.max_radius))
        current_color = (
            self.base_color[0] * intensity,
            self.base_color[1] * intensity,
            self.base_color[2] * intensity,
        )
        draw_empty_circle(self.x, self.y, self.radius, current_color)


class Wall:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.brightness = 0.0
        self.base_color = (0.0, 1.0, 1.0)

    def update(self, waves):
        if self.brightness > 0:
            self.brightness = max(0.0, self.brightness - 0.015)

        for wave in waves:
            closest_x = max(self.x, min(wave.x, self.x + self.w))
            closest_y = max(self.y, min(wave.y, self.y + self.h))
            distance = math.hypot(wave.x - closest_x, wave.y - closest_y)
            if abs(distance - wave.radius) < 15.0:
                self.brightness = 1.0

    def draw(self):
        if self.brightness > 0:
            current_color = (
                self.base_color[0] * self.brightness,
                self.base_color[1] * self.brightness,
                self.base_color[2] * self.brightness,
            )
            glColor3f(*current_color)
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(self.x, self.y)
            glVertex2f(self.x + self.w, self.y)
            glVertex2f(self.x + self.w, self.y + self.h)
            glVertex2f(self.x, self.y + self.h)
            glEnd()
            glLineWidth(1.0)


class Fruit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 8
        self.color = (0.0, 1.0, 0.0)
        self.active = True

    def draw(self):
        if not self.active: return
        glColor3f(*self.color)
        glBegin(GL_POLYGON)
        glVertex2f(self.x, self.y + self.r)
        glVertex2f(self.x + self.r, self.y)
        glVertex2f(self.x, self.y - self.r)
        glVertex2f(self.x - self.r, self.y)
        glEnd()


class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 12
        self.color = (1.0, 1.0, 0.0)
        self.active = True

    def draw(self):
        if not self.active: return
        glColor3f(*self.color)
        glBegin(GL_POLYGON)
        glVertex2f(self.x, self.y + self.r)
        glVertex2f(self.x + self.r, self.y + self.r / 2)
        glVertex2f(self.x + self.r, self.y - self.r / 2)
        glVertex2f(self.x, self.y - self.r)
        glVertex2f(self.x - self.r, self.y - self.r / 2)
        glVertex2f(self.x - self.r, self.y + self.r / 2)
        glEnd()


def heuristic(a, b):
    """Calcula la distancia Euclidiana (línea recta) entre dos puntos en la cuadrícula"""
    return math.hypot(a[0] - b[0], a[1], b[1])

def a_star_search(grid, start, goal):
    """
    grid: Matriz de 0 y 1's
    start: Tupla (col, fila) de inicio
    goal: Tupla (col, fila) de destino
    Retorna --> Lista de tuplas [(col, fila), ...] formando la ruta, o [] si no hay.
    """
    rows = len(grid)
    cols = len(grid[0])

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    # 8 posibles direcciones: cardinales + diagonales
    directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in directions:
            neighbor_col = current[0] + dx
            neighbor_row = current[1] + dy

            if 0 <= neighbor_col < cols and 0 <= neighbor_row < rows:
                if grid[neighbor_row][neighbor_col] == 1:
                    continue

                move_cost = math.hypot(dx, dy)
                tentative_g = g_score[current] + move_cost
                neighbor = (neighbor_col, neighbor_row)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

    return []


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 40
        self.color = (1.0, 0.0, 0.0)
        self.speed = 4.5

        # Estados: 'IDLE', 'INVESTIGATING', 'SEARCHING'
        self.state = 'IDLE'
        self.path = []
        self.active = True

        # Frames restantes de visibilidad; el enemigo solo se renderiza cuando este valor > 0
        self.visibility_timer = 0

        # Frames hasta el próximo destino de patrulla; valor inicial aleatorio para desincronizar enemigos
        self.wander_timer = random.randint(60, 180)
        # Cantidad de pasos de búsqueda restantes antes de volver a IDLE
        self.search_steps = 0

    def calculate_path(self, target_x, target_y, grid):
        """Convierte coordenadas a índices, corre A* y guarda la ruta en píxeles"""
        start_col = int(self.x // CELL_SIZE)
        start_row = int(self.y // CELL_SIZE)
        goal_col  = int(target_x // CELL_SIZE)
        goal_row  = int(target_y // CELL_SIZE)

        grid_path = a_star_search(grid, (start_col, start_row), (goal_col, goal_row))

        self.path = []
        for col, row in grid_path:
            self.path.append((col * CELL_SIZE + CELL_SIZE / 2,
                              row * CELL_SIZE + CELL_SIZE / 2))

    def update(self, nav_grid):
        if not self.active: return
        if self.visibility_timer > 0:
            self.visibility_timer -= 1

        if self.state == 'IDLE':
            # Patrulla: cuando no hay ruta activa, elige un destino aleatorio lejano
            if len(self.path) == 0:
                self.wander_timer -= 1
                if self.wander_timer <= 0:
                    target_x = self.x + random.randint(-300, 300)
                    target_y = self.y + random.randint(-300, 300)
                    self.calculate_path(target_x, target_y, nav_grid)
                    # Delay mínimo para evitar recalcular A* en bucle si el destino es inaccesible
                    self.wander_timer = 10

        elif self.state == 'INVESTIGATING':
            # Llegó al origen del sonido → inicia exploración local
            if len(self.path) == 0:
                self.state = 'SEARCHING'
                self.search_steps = 3

        elif self.state == 'SEARCHING':
            if len(self.path) == 0:
                if self.search_steps > 0:
                    # Explora un punto aleatorio en radio reducido (merodea la zona)
                    target_x = self.x + random.randint(-80, 80)
                    target_y = self.y + random.randint(-80, 80)
                    self.calculate_path(target_x, target_y, nav_grid)
                    self.search_steps -= 1
                else:
                    self.state = 'IDLE'

        if len(self.path) > 0:
            target_x, target_y = self.path[0]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed:
                self.x = target_x
                self.y = target_y
                self.path.pop(0)
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, is_player_hunter):
        if not self.active: return
        # if self.visibility_timer <= 0: return

        if is_player_hunter:
            self.color = (1.0, 0.5, 0.0)
        else:
            self.color = (1.0, 0.0, 0.0)

        draw_circle(self.x, self.y, self.r, self.color)

        # DEBUG: traza la ruta planeada por A*
        if len(self.path) > 0:
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(self.x, self.y)
            for px, py in self.path:
                glVertex2f(px, py)
            glEnd()


class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0
        self.y = 0

    def update(self, target_x, target_y):
        self.x = target_x - (self.width / 2)
        self.y = target_y - (self.height / 2)
        self.x = max(0, min(self.x, self.map_width - self.width))
        self.y = max(0, min(self.y, self.map_height - self.height))

    def apply(self):
        glLoadIdentity()
        glTranslatef(-self.x, -self.y, 0)
