# Resonance

**Autor:** Enrique Julca Delgado  
**Curso:** Videojuegos y Aplicaciones Móviles — Ciclo IX  
**Plataforma:** PC | **Lenguaje:** Python 3.12 | **Librerías:** PyOpenGL 3.1.x + Pygame 2.x

---

## Descripción

Resonance es un juego de sigilo y resolución de laberintos en 2D con vista ortográfica superior. El jugador controla un murciélago inmerso en oscuridad total dentro de cuevas subterráneas. La única forma de percibir el entorno es emitiendo **pulsos de ecolocalización**: ondas de sonido que viajan por el laberinto, iluminan temporalmente las paredes y revelan la posición de enemigos y objetos coleccionables.

El dilema central del juego: **ver te delata**. Cada pulso que emites es también una señal que los enemigos ciegos usan para cazarte.

---

## Géneros

Puzzle · Estrategia · Sigilo — Single-player

---

## Instalación

```bash
# Entorno Virtual
python -m venv venv
venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

```bash
python src/main.py
```

**Requisitos:** Python 3.12 · pygame 2.6.1 · PyOpenGL 3.1.10

## Mecánicas de Juego

| Acción | Control |
|---|---|
| Movimiento libre | `W A S D` o flechas |
| Emitir pulso de sonido (ecolocalización) | `Barra espaciadora` |
| Recoger fruta / power-up | Pasar sobre el objeto |

### Sistema de Ecolocalización
Al presionar espacio, el murciélago emite una onda circular. Esta onda:
- Viaja por el laberinto y rebota en las paredes.
- Ilumina **temporalmente** el territorio que toca (paredes, frutas, enemigos).
- Alerta a los enemigos: cada criatura tocada por la onda usa **A\*** para dirigirse exactamente al punto donde se emitió el pulso.

### Condiciones
- **Victoria:** Recolectar el 100 % de las frutas del nivel y alcanzar la salida.
- **Derrota:** Ser tocado por un enemigo sin power-up activo.

### Power-up — Estrella
Al recoger una estrella, el jugador obtiene inmunidad temporal y puede eliminar enemigos al contacto, invirtiendo los roles por unos segundos.

---

## Personajes y Elementos

| Elemento | Representación visual |
|---|---|
| Murciélago (jugador) | Círculo azul luminoso — siempre visible |
| Depredadores (enemigos) | Formas geométricas rojas — solo visibles bajo la onda |
| Frutas | Puntos / rombos verdes |
| Estrella (power-up) | Polígono amarillo brillante |
| Paredes | Líneas blancas/cian — solo al contacto con el sonido |

---

## Niveles

| Nivel | Descripción |
|---|---|
| **Nivel 1 — Tutorial** | Laberinto sencillo sin enemigos. Aprende ecolocalización, recolección y salida. |
| **Nivel 2** | Aparecen los primeros depredadores. Aprende a esquivarlos tras emitir el pulso. |
| **Nivel 3** | Se introduce la Estrella. Laberinto complejo con enemigos que bloquean el paso. |
| **Nivel 4 — Supervivencia** | Mapa abierto. La fruta reaparece y los enemigos aumentan progresivamente. Máxima puntuación. |
