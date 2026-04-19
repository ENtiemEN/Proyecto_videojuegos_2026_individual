import pygame # -> ventana, inputs, loop del juego
from pygame.locals import * # -> CONSTANTES e.g. DOUBLEBUF(double buffer - evitar flickering), OPENGL(contexto OpenGL)
from OpenGL.GL import * # -> Funciones core de OpenGL
from OpenGL.GLU import * # -> Funciones auxiliares de alto nivel e.g. `gluOrtho2D`
import sys
import math

# Global Config
WIDTH, HEIGHT = 800, 600
FPS = 60

def draw_circle(x,y,r, color, segments=32):
    """Dibuja un círculo con aproximación poligonal (triángulos)"""
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
        self.r = 8      # tamaño del jugador
        self.speed = 5.0
        self.color = (0.0, 0.46, 1.0) # Neon
    
    def update(self, keys, width, height):
        # Movimiento (W,A,S,D o ↑, ↓, →, ←)
        if keys[K_w] or keys[K_UP]:
            self.y += self.speed
        if keys[K_s] or keys[K_DOWN]:
            self.y -= self.speed
        if keys[K_a] or keys[K_LEFT]:
            self.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            self.x += self.speed

        # Border detection
        if self.x - self.r < 0:
            self.x = self.r
        if self.x + self.r > width:
            self.x = width - self.r
        if self.y - self.r < 0:
            self.y = self.r
        if self.y + self.r > height:
            self.y = height - self.r
    
    def draw(self):
        draw_circle(self.x, self.y, self.r, self.color)


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

    # Iniciar Player en el centro de la screen
    player = Player(WIDTH//2,HEIGHT//2)

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
        #print(keys)

        player.update(keys, WIDTH, HEIGHT)

        # Renderizado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

