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
    
    def update(self, keys, width, height):
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

        # Mover al player
        self.x += self.vx
        self.y += self.vy

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
    pygame.display.set_caption("Resonance - Entregable 1")

    init_opengl()
    clock = pygame.time.Clock()

    # Definimos un mapa 2 veces más grande que la ventana
    MAP_WIDTH, MAP_HEIGHT = 1600, 1200

    player = Player(MAP_WIDTH//2,MAP_HEIGHT//2)
    camera = Camera(WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT)

    # Game loop
    running = True
    while running:
        # Captura de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        # Lógica de actualización (Movimiento, Colisiones, etc.)
        keys = pygame.key.get_pressed()

        ## lógica del juego
        player.update(keys, MAP_WIDTH, MAP_HEIGHT)
        camera.update(player.x, player.y)

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

