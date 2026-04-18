import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

# Global Config
WIDTH, HEIGHT = 800, 600
FPS = 60

def init_opengl():
    # Contexto 2D de OpenGL
    glViewport(0, 0, WIDTH, HEIGHT)

    # matriz de proyección
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Configurar cámara ortográfica 2D
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

    # Volver a la matriz de modelo-vista
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Fondo
    glClearColor(0.02, 0.02, 0.02, 1.0)

def main():
    pygame.init()

    # Conf. pantalla para OpenGL y Doble Buffer
    display_flags = DOUBLEBUF | OPENGL
    pygame.display.set_mode((WIDTH,HEIGHT), display_flags)
    pygame.display.set_caption("Resonance - Entregable 1")

    # Incialización de OpenGL
    init_opengl()

    # Controlar FPS
    clock = pygame.time.Clock()

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

        # Renderizado

        # Limpiar buffer de color y profundidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Usar funciones primitivas de GL para dibujar

        # Intercambiar los buffers para mostrar lo que se ha dibujado
        pygame.display.flip()

        # Control de fotogramas per second
        clock.tick(FPS)

    # Limpieza y cierre
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

