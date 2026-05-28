from entities import Wall, Fruit, Star, Enemy, Exit

MAX_LEVEL = 4

def get_level(n):
    levels = {
        1: level_1,
        2: level_2,
        3: level_3,
        4: level_4,
    }
    return levels.get(n, level_1)()


# =============================================================================
# NIVEL 1 — Tutorial
# Sin enemigos. El jugador aprende ecolocalización, recolección y la salida.
# Cuatro obstáculos en L, uno por cuadrante. Mapa abierto.
# =============================================================================
def level_1():
    walls = [
        # Bordes
        Wall(0, 0, 1600, 40),
        Wall(0, 1160, 1600, 40),
        Wall(0, 0, 40, 1200),
        Wall(1560, 0, 40, 1200),

        # Obstáculo SO
        Wall(250, 250, 300, 40),
        Wall(250, 250, 40, 300),

        # Obstáculo SE
        Wall(1050, 250, 300, 40),
        Wall(1300, 250, 40, 300),

        # Obstáculo NO
        Wall(250, 750, 300, 40),
        Wall(250, 750, 40, 300),

        # Obstáculo NE
        Wall(1050, 750, 300, 40),
        Wall(1300, 750, 40, 300),
    ]

    fruits = [
        Fruit(120, 120),    # Esquina SO
        Fruit(1460, 120),   # Esquina SE
        Fruit(120, 1060),   # Esquina NO
        Fruit(1460, 1060),  # Esquina NE
    ]

    return {
        'walls':        walls,
        'fruits':       fruits,
        'stars':        [],
        'enemies':      [],
        'exit':         Exit(800, 1080),
        'player_start': (800, 600),
    }


# =============================================================================
# NIVEL 2 — Primeros depredadores
# Laberinto complejo con 2 enemigos. El jugador debe usar el sonido para
# detectarlos y moverse en silencio.
# =============================================================================
def level_2():
    walls = [
        # Bordes
        Wall(0, 0, 1600, 40),
        Wall(0, 1160, 1600, 40),
        Wall(0, 0, 40, 1200),
        Wall(1560, 0, 40, 1200),

        # Zona central
        Wall(650, 500, 40, 200),
        Wall(910, 500, 40, 200),
        Wall(700, 750, 200, 40),

        # Cuadrante inferior izquierdo (Zig-Zag)
        Wall(150, 200, 400, 40),
        Wall(150, 350, 400, 40),
        Wall(150, 500, 300, 40),
        Wall(150, 200, 40, 190),
        Wall(510, 350, 40, 190),

        # Cuadrante inferior derecho (Pilares)
        Wall(1000, 200, 80, 80),
        Wall(1300, 250, 80, 80),
        Wall(1150, 400, 80, 80),
        Wall(950, 550, 80, 80),
        Wall(1400, 450, 80, 80),

        # Cuadrante superior derecho (Pasillos)
        Wall(1000, 950, 400, 40),
        Wall(900, 800, 500, 40),
        Wall(1360, 600, 40, 390),
        Wall(900, 800, 40, 250),

        # Cuadrante superior izquierdo (Laberinto)
        Wall(200, 900, 300, 40),
        Wall(200, 700, 40, 240),
        Wall(350, 750, 250, 40),
        Wall(400, 1000, 40, 160),
        Wall(600, 850, 40, 200),
    ]

    fruits = [
        Fruit(1050, 1050), Fruit(1150, 1050), Fruit(1280, 1050),
        Fruit(250, 250),   Fruit(250, 400),   Fruit(300, 450),
    ]

    return {
        'walls':        walls,
        'fruits':       fruits,
        'stars':        [Star(1100, 320)],
        'enemies':      [Enemy(250, 400), Enemy(1200, 320)],
        'exit':         Exit(1450, 1080),
        'player_start': (800, 600),
    }


# =============================================================================
# NIVEL 3 — Estrella obligatoria
# Cuatro cámaras conectadas por pasillos estrechos. Enemigos bloquean cada
# entrada. El jugador debe usar las estrellas para despejar el camino.
#
# Layout:
#   Cámara central (spawn) ── corredor norte ── Cámara norte (frutas)
#                          ── corredor sur  ── Cámara sur  (frutas)
#                          ── corredor este ── Cámara este (frutas + salida)
#
# Estrellas en la zona central (accesibles sin cruzar enemigos).
# =============================================================================
def level_3():
    walls = [
        # Bordes
        Wall(0, 0, 1600, 40),
        Wall(0, 1160, 1600, 40),
        Wall(0, 0, 40, 1200),
        Wall(1560, 0, 40, 1200),

        # --- Muro que separa cámara NORTE del centro (gap x=600-720) ---
        Wall(40, 840, 560, 40),
        Wall(720, 840, 840, 40),

        # --- Muro que separa cámara SUR del centro (gap x=600-720) ---
        Wall(40, 360, 560, 40),
        Wall(720, 360, 840, 40),

        # --- Muro que separa cámara ESTE del centro (gap y=560-680) ---
        Wall(1100, 40, 40, 520),
        Wall(1100, 680, 40, 480),

        # --- Obstáculos en cámara norte ---
        Wall(250, 1000, 300, 40),
        Wall(550, 960, 40, 160),

        # --- Obstáculos en cámara sur ---
        Wall(250, 200, 300, 40),
        Wall(550, 80, 40, 160),

        # --- Obstáculos en cámara este ---
        Wall(1250, 500, 250, 40),
        Wall(1250, 500, 40, 200),

        # --- Obstáculos en zona central (estrechan acceso sin cerrarlo) ---
        Wall(200, 400, 200, 40),
        Wall(1200, 400, 200, 40),
        Wall(200, 760, 200, 40),
        Wall(1200, 760, 200, 40),
    ]

    fruits = [
        Fruit(300, 1050), Fruit(500, 1050),  # Cámara norte
        Fruit(300, 150),  Fruit(500, 150),   # Cámara sur
        Fruit(1350, 650), Fruit(1450, 650),  # Cámara este
    ]

    # Estrellas en la zona central — accesibles desde el spawn sin cruzar enemigos
    stars = [Star(450, 600), Star(1050, 600)]

    # Enemigos guardan cada corredor de entrada
    enemies = [
        Enemy(650, 860),   # Corredor norte
        Enemy(650, 340),   # Corredor sur
        Enemy(1060, 600),  # Corredor este
        Enemy(1350, 650),  # Patrulla en cámara este, cerca de las frutas
    ]

    return {
        'walls':        walls,
        'fruits':       fruits,
        'stars':        stars,
        'enemies':      enemies,
        'exit':         Exit(1450, 750),
        'player_start': (800, 600),
    }


# =============================================================================
# NIVEL 4 — Supervivencia
# Mapa abierto con pilares dispersos. Sin salida. Las frutas reaparecen cada
# 8 segundos. Los enemigos se generan progresivamente en los bordes del mapa.
# El objetivo es acumular la mayor puntuación posible antes de morir.
# =============================================================================
def level_4():
    walls = [
        # Bordes
        Wall(0, 0, 1600, 40),
        Wall(0, 1160, 1600, 40),
        Wall(0, 0, 40, 1200),
        Wall(1560, 0, 40, 1200),

        # Pilares dispersos
        Wall(300,  300,  80, 80),
        Wall(700,  200,  80, 80),
        Wall(1200, 300,  80, 80),
        Wall(200,  700,  80, 80),
        Wall(800,  580,  80, 80),
        Wall(1300, 700,  80, 80),
        Wall(400,  1000, 80, 80),
        Wall(1100, 900,  80, 80),
    ]

    # respawn_delay = 480 frames = 8 segundos a 60 FPS
    fruits = [
        Fruit(200,  200,  480), Fruit(800,  150,  480),
        Fruit(1400, 200,  480), Fruit(150,  600,  480),
        Fruit(1450, 600,  480), Fruit(200,  1050, 480),
        Fruit(800,  1050, 480), Fruit(1400, 1050, 480),
    ]

    return {
        'walls':        walls,
        'fruits':       fruits,
        'stars':        [],
        'enemies':      [Enemy(400, 400), Enemy(1200, 800)],
        'exit':         None,
        'player_start': (800, 600),
        'survival':     True,
    }
