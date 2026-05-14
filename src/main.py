import pygame # -> ventana, inputs, loop del juego
from pygame.locals import * # -> CONSTANTES e.g. DOUBLEBUF(double buffer - evitar flickering), OPENGL(contexto OpenGL)
from OpenGL.GL import * # -> Funciones core de OpenGL
from OpenGL.GLU import * # -> Funciones auxiliares de alto nivel e.g. `gluOrtho2D`
import sys
import math

# Global Config
WIDTH, HEIGHT = 800, 600
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
        camera.update(player.x, player.y)

        # Filtar ondas que ya no están activas
        for wave in waves:
            wave.update()
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

        for wave in waves: # dibujamos las ondas antes que el jugador para que quede por encima
            wave.draw()
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

