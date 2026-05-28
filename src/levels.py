from entities import Wall, Fruit, Star, Enemy, Exit

def get_level(n):
    levels = {
        1: level_1,
    }
    return levels.get(n, level_1)()

def level_1():
    walls = [
        # --- BORDES DEL MAPA ---
        Wall(0, 0, 1600, 40),
        Wall(0, 1160, 1600, 40),
        Wall(0, 0, 40, 1200),
        Wall(1560, 0, 40, 1200),

        # --- ZONA CENTRAL (jugador nace en 800, 600) ---
        Wall(650, 500, 40, 200),
        Wall(910, 500, 40, 200),
        Wall(700, 750, 200, 40),

        # --- CUADRANTE INFERIOR IZQUIERDO (Zig-Zag) ---
        Wall(150, 200, 400, 40),
        Wall(150, 350, 400, 40),
        Wall(150, 500, 300, 40),
        Wall(150, 200, 40, 190),
        Wall(510, 350, 40, 190),

        # --- CUADRANTE INFERIOR DERECHO (Pilares) ---
        Wall(1000, 200, 80, 80),
        Wall(1300, 250, 80, 80),
        Wall(1150, 400, 80, 80),
        Wall(950, 550, 80, 80),
        Wall(1400, 450, 80, 80),

        # --- CUADRANTE SUPERIOR DERECHO (Pasillos) ---
        Wall(1000, 950, 400, 40),
        Wall(900, 800, 500, 40),
        Wall(1360, 600, 40, 390),
        Wall(900, 800, 40, 250),

        # --- CUADRANTE SUPERIOR IZQUIERDO (Laberinto) ---
        Wall(200, 900, 300, 40),
        Wall(200, 700, 40, 240),
        Wall(350, 750, 250, 40),
        Wall(400, 1000, 40, 160),
        Wall(600, 850, 40, 200),
    ]

    fruits = [
        Fruit(1050, 970), Fruit(1150, 970), Fruit(1250, 970),
        Fruit(250, 250),  Fruit(250, 400),  Fruit(400, 520),
    ]

    stars = [Star(1100, 320)]

    enemies = [Enemy(250, 400), Enemy(1200, 320), Enemy(500, 950)]

    return {
        'walls':        walls,
        'fruits':       fruits,
        'stars':        stars,
        'enemies':      enemies,
        'exit':         Exit(1450, 1080),
        'player_start': (800, 600),
    }
