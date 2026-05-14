import pygame # -> ventana, inputs, loop del juego
from pygame.locals import * # -> CONSTANTES e.g. DOUBLEBUF(double buffer - evitar flickering), OPENGL(contexto OpenGL)
from OpenGL.GL import * # -> Funciones core de OpenGL
from OpenGL.GLU import * # -> Funciones auxiliares de alto nivel e.g. `gluOrtho2D`
import sys
import math
import heapq

# Global Config
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40 # Tamaño de cada celda de navegación
FPS = 60

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

def draw_circle(x,y,r, color, segments=32):
    """Dibuja un círculo aproximado con polígonos"""
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x,y)

    for i in range(segments + 1):
        angle = i * (2.0 * math.pi / segments)
        cx = x + r * math.cos(angle)
        cy = y + r * math.sin(angle)
        glVertex2f(cx,cy)
    glEnd()

def draw_empty_circle(x,y,r,color,line_width=2.0,segments=64):
    """Dibujamos anillos (representando las ondas)"""
    glLineWidth(line_width)
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        angle = i * (2.0 * math.pi / segments)
        cx = x + r * math.cos(angle)
        cy = y + r * math.sin(angle)
        glVertex2f(cx,cy)
    glEnd()
    glLineWidth(1.0) # Reset al grosor

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

        self.color = (0.0, 0.46, 1.0) # Neon
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
            self.color = (1.0, 1.0, 0.0) # El player se vuelve amarillento
            if self.hunter_timer <= 0:
                self.is_hunter = False
                self.color = self.base_color
        else:
            self.color = self.base_color

        self.time_alive += 1

        # Efecto de pulsación (Variar el radio ligeramente)
        self.r = self.base_r + math.sin(self.time_alive * 0.1) * 0.8

        # Físicas (Aceleración)
        # (W,A,S,D o ↑, ↓, →, ←)
        if keys[K_w] or keys[K_UP]:
            self.vy += self.acceleration
        if keys[K_s] or keys[K_DOWN]:
            self.vy -= self.acceleration
        if keys[K_a] or keys[K_LEFT]:
            self.vx -= self.acceleration
        if keys[K_d] or keys[K_RIGHT]:
            self.vx += self.acceleration

        # Físicas (Fricción, Límite de Vel.)
        self.vx *= self.friction
        self.vy *= self.friction

        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            ratio = self.max_speed / speed
            self.vx *= ratio
            self.vy *= ratio

        # COLISIONES
        # Mover en X, y comprobar colisiones
        self.x += self.vx
        for wall in walls:
            if self.check_collision(wall):
                if self.vx > 0: # Si se movía a la der., lo empujamos a la izq.
                    self.x = wall.x - self.base_r
                elif self.vx < 0: # Si se movía a la izq., lo empujamos a la der.
                    self.x = wall.x + wall.w + self.base_r
                self.vx = 0 # Detener el momento en X

        # Mover en Y, y comprobar colisiones
        self.y += self.vy
        for wall in walls:
            if self.check_collision(wall):
                if self.vy > 0: # Si se movía hacia arriba, lo empujamos hacia abajo
                    self.y = wall.y - self.base_r
                elif self.vy < 0: # Si se movía hacia abajo, lo empujamos hacia arriba
                    self.y = wall.y + wall.h + self.base_r
                self.vy = 0 # Detener el momento en Y

        # Detección de bordes del mapa (usa base_r fijo, rebote suave)
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
        """Verificar colisión entre el player y pared"""
        closest_x = max(wall.x, min(self.x, wall.x + wall.w))
        closest_y = max(wall.y, min(self.y, wall.y + wall.h))

        distance_x = self.x - closest_x
        distance_y = self.y - closest_y

        distance_squared = distance_x**2 + distance_y**2

        return distance_squared < (self.base_r ** 2)

class SoundWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 24.0 # Nace del mismo tamaño que el player
        self.max_radius = 500.0
        self.expansion_speed = 12.0
        self.active = True
        self.base_color = (0.0, 1.0, 1.0)

    def update(self):
        self.radius += self.expansion_speed
        if self.radius > self.max_radius:
            self.active = False

    def draw(self):
        # Efecto de desvanecimiento
        intensity = 1.0 - (self.radius / self.max_radius)
        intensity = max(0.0, intensity) # evitar negativos, just in case

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
        self.base_color = (0.0, 1.0, 1.0) # Otro Cyan por ahora (cambiar probablemente)

    def update(self, waves):
        if self.brightness > 0:
            self.brightness -= 0.015 # velocidad a la que vuelve la oscuridad
            self.brightness = max(0.0, self.brightness)

        # Colisión con el borde de las ondas
        for wave in waves:
            # encontrar punto más cercano de la pared al centro de la onda
            closest_x = max(self.x, min(wave.x, self.x + self.w))
            closest_y = max(self.y, min(wave.y, self.y + self.h))

            # distancia del punto más cercano al centro de la onda
            distance_x = wave.x - closest_x
            distance_y = wave.y - closest_y
            distance = math.hypot(distance_x, distance_y)

            # damos un grosor virtual para que la colisión no sea estricta
            thickness = 15.0
            if abs(distance - wave.radius) < thickness:
                self.brightness = 1.0
    
    def draw(self):
        # Solo se dibuja la pared si el sonido la ha iluminado
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

            glLineWidth(1.0) # Reset al grosor

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
        glVertex2f(self.x + self.r, self.y + self.r/2)
        glVertex2f(self.x + self.r, self.y - self.r/2)
        glVertex2f(self.x, self.y - self.r)
        glVertex2f(self.x - self.r, self.y - self.r/2)
        glVertex2f(self.x - self.r, self.y + self.r/2)
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

    # Cola de prioridad para el Open Set. Guarda tuplas: (f_score, (col, fila))
    ## Open Set   --> Nosdos descubiertos que aún no han sido evaluados
    ## Closed Set --> Nodos que ya fueron evaluados por completo, para no volver a caminar sobre nuestro propios pasos
    open_set = []
    heapq.heappush(open_set, (0, start))

    # Diccionario para reconstruir el camino
    came_from = {}

    # Costo desde el inicio
    g_score = {start: 0}

    # 8 posibles direcciones de movimiento (4+4): Arriba, Abajo, Izquierda, Derecha + Diagonales
    directions = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]

    while open_set:
        # Extraemos el nodo con el menor f(n)
        current_f, current = heapq.heappop(open_set)

        # Si llegamos al destido/objetivo, reconstruimos el camino hacia atrás
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        # Explorar vecinos
        for dx, dy in directions:
            neighbor_col = current[0] + dx
            neighbor_row = current[1] + dy

            # Verificar que el vecino esté dentro de los límites de la matriz/grid
            if 0 <= neighbor_col < cols and 0 <= neighbor_row < rows:
                # Verificar que no sea una pared (1)
                if grid[neighbor_row][neighbor_col] == 1:
                    continue

                # Costo para moverse en diagonal es mayor (\sqrt{2}) que en línea recta (1)
                move_cost = math.hypot(dx, dy)
                tentative_g = g_score[current] + move_cost
                neighbor = (neighbor_col, neighbor_row)

                # Si encontramos un camino más corto hacia el vecino, lo registramooos
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    # f(n) = g(n) + h(n)
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

    return [] # Si termina el while y no returnamos, no hay camino posible

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 40
        self.color = (1.0, 0.0, 0.0)
        self.speed = 4.5

        # Estados: 'IDLE' (quieto), 'INVESTIGATING' (escuchó sonido), 'FLEEING' (Huyendo del jugador con power-up)
        self.state = 'IDLE'
        self.path = [] # Guarda puntos (X,Y) en píxeles
        self.active = True

    def calculate_path(self, target_x, target_y, grid):
        """Convierte coordenadas a índices, corre A* y guarda la ruta en píxeles"""
        # Discretizar --> Convertir píxeles a índices de celda
        start_col = int(self.x // CELL_SIZE)
        start_row = int(self.y // CELL_SIZE)

        goal_col = int(target_x // CELL_SIZE)
        goal_row = int(target_y // CELL_SIZE)

        start_node = (start_col, start_row)
        goal_node = (goal_col, goal_row)

        # Ejecutamos A*
        grid_path = a_star_search(grid, start_node, goal_node)

        # Covertimos a píxeles nuevamente
        self.path = []
        for col, row in grid_path:
            px_x = (col * CELL_SIZE) + (CELL_SIZE / 2)
            px_y = (row * CELL_SIZE) + (CELL_SIZE / 2)
            self.path.append((px_x, px_y))

    def update(self):
        if not self.active: return
        # Si tenemos una ruta, nos movemos hacia el primer punto de la lista
        if len(self.path) > 0:
            target_x, target_y = self.path[0]

            # Dirección hacia el objetivo (vector de dirección)
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)

            # Si llegamos a ese punto (o estamos muy cerca), lo sacamos de la lista
            if dist < self.speed:
                self.x = target_x
                self.y = target_y
                self.path.pop(0)
            else:
                # Nomalizar el vector y multiplicarlo por la velocidad
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, is_player_hunter):
        if not self.active: return

        # Si el jugador tiene estrella, el enemigo huye (Cambia de color)
        if is_player_hunter:
            self.color = (1.0, 0.5, 0.0) # Naranja
        else:
            self.color = (1.0, 0.0, 0.0) 
        
        # Testeamos al enemigo con un circulo
        draw_circle(self.x, self.y, self.r, self.color)

        # DEBUG --> Dibujamos una línea roja para ver la ruta que planeó A*
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
        # La cámara se centra en el player
        self.x = target_x - (self.width / 2)
        self.y = target_y - (self.height / 2)

        # Evitar que la cámara muestre fuera de los límites del mapa
        self.x = max(0, min(self.x, self.map_width - self.width))
        self.y = max(0, min(self.y, self.map_height - self.height))

    def apply(self):
        # Mueve el mundo en sentido contrario de la cámara
        glLoadIdentity()
        glTranslatef(-self.x, -self.y, 0)

def init_opengl():
    # Contexto 2D de OpenGL
    glViewport(0, 0, WIDTH, HEIGHT)

    glMatrixMode(GL_PROJECTION) # -> Cámara
    glLoadIdentity()

    # Configurar cámara ortográfica 2D
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

    glMatrixMode(GL_MODELVIEW) # -> Objetos
    glLoadIdentity()

    glClearColor(0.02, 0.02, 0.02, 1.0) # -> Fondo

def create_nav_grid(map_w, map_h, walls, cell_size):
    """Convierte el mapa continuo en una matriz discreta de 0 y 1s para navegación | algoritmos"""
    cols = map_w // cell_size
    rows = map_h // cell_size

    # Matriz bidimensional inicializada en 0 (celdas transitables)
    grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            # Coordenadas reales de la celda
            cell_x = c * cell_size
            cell_y = r * cell_size

            # Comprobar si la celda choca con alguna pared
            for wall in walls:
                # Si hay intersección entre la celda y la pared, se marca como no transitable (1)
                if (cell_x < wall.x + wall.w and cell_x + cell_size > wall.x and
                    cell_y < wall.y + wall.h and cell_y + cell_size > wall.y):
                    grid[r][c] = 1
                    break
    return grid

def main():
    pygame.init()
    display_flags = DOUBLEBUF | OPENGL
    pygame.display.set_mode((WIDTH,HEIGHT), display_flags)
    pygame.display.set_caption("Resonance - Entregable 2")

    init_opengl()
    clock = pygame.time.Clock()

    # Definimos un mapa 2 veces más grande que la ventana
    MAP_WIDTH, MAP_HEIGHT = 1600, 1200

    player = Player(MAP_WIDTH//2,MAP_HEIGHT//2)
    camera = Camera(WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT)

    # Game loop
    waves = [] # Almacenamos ondas de sonido activas, en caso el usuario haga jitter
    fruits = [
        Fruit(1050, 970), Fruit(1150, 970), Fruit(1250, 970), # Pasillo superior
        Fruit(250, 250), Fruit(250, 400), Fruit(400, 520)     # Zona Zig-Zag
    ]
    stars = [Star(1100, 320)] # Escondida en la zona de pilares
    walls = [
        # --- BORDES DEL MAPA (Para que la onda ilumine los límites) ---
        Wall(0, 0, 1600, 40),       # Borde Inferior
        Wall(0, 1160, 1600, 40),    # Borde Superior
        Wall(0, 0, 40, 1200),       # Borde Izquierdo
        Wall(1560, 0, 40, 1200),    # Borde Derecho

        # --- ZONA CENTRAL (Refugio de inicio, el jugador nace en 800, 600) ---
        Wall(650, 500, 40, 200),    # Escudo izquierdo
        Wall(910, 500, 40, 200),    # Escudo derecho
        Wall(700, 750, 200, 40),    # Techo del centro

        # --- CUADRANTE INFERIOR IZQUIERDO (Zona de Zig-Zag) ---
        Wall(150, 200, 400, 40),    # Fila 1
        Wall(150, 350, 400, 40),    # Fila 2
        Wall(150, 500, 300, 40),    # Fila 3
        Wall(150, 200, 40, 190),    # Cierre vertical izquierdo
        Wall(510, 350, 40, 190),    # Cierre vertical derecho

        # --- CUADRANTE INFERIOR DERECHO (Zona de Pilares, ideal para sigilo) ---
        Wall(1000, 200, 80, 80),
        Wall(1300, 250, 80, 80),
        Wall(1150, 400, 80, 80),
        Wall(950, 550, 80, 80),
        Wall(1400, 450, 80, 80),

        # --- CUADRANTE SUPERIOR DERECHO (Pasillos largos de alta velocidad) ---
        Wall(1000, 950, 400, 40),   # Pasillo superior
        Wall(900, 800, 500, 40),    # Pasillo medio
        Wall(1360, 600, 40, 390),   # Muro vertical derecho
        Wall(900, 800, 40, 250),    # Muro vertical izquierdo

        # --- CUADRANTE SUPERIOR IZQUIERDO (Laberinto cerrado) ---
        Wall(200, 900, 300, 40),
        Wall(200, 700, 40, 240),
        Wall(350, 750, 250, 40),
        Wall(400, 1000, 40, 160),
        Wall(600, 850, 40, 200)
    ]

    # Generar la matriz de navegación (Solo una vez)
    nav_grid = create_nav_grid(MAP_WIDTH, MAP_HEIGHT, walls, CELL_SIZE)
    
    # Instanciar enemigos
    enemies = [
        Enemy(250, 400),   # Zona Zig-Zag
        Enemy(1200, 320),  # Zona de Pilares
        Enemy(500, 950)    # Zona Superior
    ]

    running = True

    while running:
        # Captura de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    waves.append(SoundWave(player.x, player.y))
        
        # Lógica de actualización (Movimiento, Colisiones, etc.)
        keys = pygame.key.get_pressed()

        ## lógica del juego
        player.update(keys, MAP_WIDTH, MAP_HEIGHT, walls)

        # Recolección de frutas
        for fruit in fruits:
            if fruit.active:
                dist = math.hypot(player.x - fruit.x, player.y - fruit.y)
                if dist < (player.r + fruit.r):
                    fruit.active = False
                    player.score += 10
                    print(f"Puntuación: {player.score}")
        
        # Recolección de Power-Up (Estrella)
        for star in stars:
            if star.active:
                dist = math.hypot(player.x - star.x, player.y - star.y)
                if dist < (player.r + star.r):
                    star.active = False
                    player.is_hunter = True
                    player.hunter_timer = FPS * 10
                    print("MODO CAZA ACTIVADO")

        for enemy in enemies:
            enemy.update()

            # Colisión jugador-enemigo
            if enemy.active:
                dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
                if dist < (player.r + enemy.r):
                    if player.is_hunter:
                        enemy.active = False
                        player.score += 50
                        print(f"Enemigo eliminado, Puntuación: {player.score}")
                    else:
                        print("GAME OVER")
                        running = False

        camera.update(player.x, player.y)

        # Filtar ondas que ya no están activas
        for wave in waves:
            wave.update()

            # DETECCIÓN ENEMIGA
            for enemy in enemies:
                dist = math.hypot(wave.x - enemy.x, wave.y - enemy.y)

                # Si el borde de la onda toca al enemigo (Con un margen de error)
                if abs(dist - wave.radius) < 15.0:
                    enemy.calculate_path(wave.x, wave.y, nav_grid)

        # Filtrar ondas que ya no están activas                    
        waves = [w for w in waves if w.active]

        # Actualizar iluminación de paredes
        for wall in walls:
            wall.update(waves)

        # Renderizado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Aplicar el desplazamiento de la cámara antes de dibujar
        camera.apply()

        draw_grid(MAP_WIDTH, MAP_HEIGHT)

        glColor3f(0.15, 0.15, 0.15)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0,0)
        glVertex2f(MAP_WIDTH, 0)
        glVertex2f(MAP_WIDTH, MAP_HEIGHT)
        glVertex2f(0, MAP_HEIGHT)
        glEnd()

        # Dibujar los obstaculos (con la iluminación)
        for wall in walls:
            wall.draw()
        
        # Dibujamos los objeto recolectables
        for fruit in fruits:
            fruit.draw()

        for star in stars:
            star.draw()

        for wave in waves: # dibujamos las ondas antes que el jugador para que quede por encima
            wave.draw()

        for enemy in enemies:
            enemy.draw(player.is_hunter)
        
        # Jugador
        player.draw()

        # Intercambiar los buffers para mostrar lo que se ha dibujado
        pygame.display.flip()

        # Control de fotogramas per second
        clock.tick(FPS)

    # Limpieza y cierre
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

