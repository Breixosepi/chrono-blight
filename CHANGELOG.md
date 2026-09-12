# Changelog - Chrono Blight

Todos los cambios notables realizados en el proyecto **Chrono Blight** (Plataformas de Acción / Mini-Metroidvania en Gale y Pygame) están documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

---

## [Unreleased / Estado Actual] - 2026-09-12

### Añadido
- **Comandos Oficiales con Gale (`src/commands.py`)**:
  - Implementación completa del Command Pattern utilizando `CommandBindings` de Gale.
  - Registro de comandos de acción y de estado: `JUMP`, `STOP_JUMP`, `MOVE_LEFT`, `STOP_MOVE_LEFT`, `MOVE_RIGHT`, `STOP_MOVE_RIGHT`, `LOOK_UP`, `STOP_LOOK_UP`, `RUN`, `STOP_RUN`, `ATTACK`, `SPECIAL_ATTACK`, `DASH`, `NEXT_FORM`, `PREV_FORM` y `SHIFT_PHASE`.
  - Mapeo de teclas limpio y desacoplado del bucle principal (`W/A/S/D` y flechas para movimiento, `Espacio` para salto, `J` para ataque, `K` para especial, `C` para dash, `Q`/`E` para cambio de forma, `LShift` para correr).
- **Pruebas Automatizadas de Físicas y Habilidades Aéreas**:
  - Suite de validación en entorno headless (`dummy` video driver) para verificar aislamiento de gravedad, bloqueo vertical de dash y transiciones entre estados.

### Corregido
- **Bloqueo de Altura Vertical en Dash Aéreo de Morph (`src/states/entity/player/DashState.py`)**:
  - Se forzó `vy = 0.0` al entrar y durante la actualización del dash. Se erradicó la inercia ascendente residual que provocaba elevaciones no deseadas al iniciar el dash en medio de un salto.
  - Al concluir la animación, el personaje pasa de forma limpia a `FallState` si sigue en el aire, reanudando la gravedad solo tras el dash.
- **Suspensión Aérea del Ataque Especial de la Espada (`src/states/entity/player/AttackSpecialState.py`)**:
  - Se configuró `has_gravity = False` y se fijó `vy = 0.0` durante la animación del ataque especial.
  - El espadachín ahora queda suspendido en el aire sin perder altura mientras carga y ejecuta el corte, ejecutando el impulso final (`_sword_special_finish`, 78 px) y pasando a `FallState` solo al terminar.
- **Prevención de Dash Involuntario al Cambiar a Morph**:
  - Consumo inmediato y descarte del flag `dash_requested` en todos los estados (`IdleState`, `WalkState`, `JumpState`, `FallState`) cuando la forma activa no tiene dash (Mago y Espadachín).
  - Limpieza explícita de todos los buffers de intención en `Player.change_skin()`.
- **Restauración del Ataque Especial del Mago**:
  - Reconexión de los callbacks `on_update` (`_mage_special_update`) y `on_finish` (`_mage_special_finish`) en `AttackSpecialState`, permitiendo el despliegue progresivo de los 3 círculos de llamas.
- **Sensibilidad y Altura del Salto Variable**:
  - Eliminación del recorte prematuro de velocidad vertical en `JumpState.py`, restaurando la parábola natural y completa de salto con soporte auténtico de salto variable vía `jump_held`.

---

## [0.4.0] - 2026-09-12

### Cambiado / Refactorizado
- **Arquitectura Base Inspirada en *Ultimate Fantasy* (`Entity` vs `Player`)**:
  - Desacoplamiento total entre la lógica física genérica y la lógica específica del jugador.
  - **`src/entities/Entity.py`**: Nueva clase base generalizada que gestiona posición (`x`, `y`), velocidades (`vx`, `vy`), bounding boxes (`hitbox`), máquina de estados (`StateMachine`), gravedad condicional (`apply_gravity`), temporizador de animaciones y colisiones con los límites del mapa y piso.
  - **`src/entities/Player.py`**: Subclase especializada en el protagonista. Administra transformaciones de piel (`sword`, `morph`, `mage`), fases cromáticas (`red`, `green`), estadísticas de HP/MP, cooldowns, combo buffers y el sistema de comandos.
- **Modularización de la Máquina de Estados Inspirada en *Super Martian***:
  - Sustitución del estado monolítico `PlayerAirborneState` por dos estados aéreos atómicos:
    - **`JumpState.py`**: Gestiona el impulso ascendente, salto variable y doble salto.
    - **`FallState.py`**: Gestiona la caída libre por gravedad, control direccional horizontal y aterrizaje.
  - Estandarización de nombres de archivos en `src/states/entity/player/` (`IdleState`, `WalkState`, `JumpState`, `FallState`, `DashState`, `AttackState`, `AttackSpecialState`, `HitState`, `DeathState`).
  - Cada estado ahora interactúa de manera limpia a través de intenciones (`jump_requested`, `attack_requested`, `dash_requested`, etc.).

---

## [0.3.0] - 2026-09-11

### Añadido
- **Interfaz de Usuario y HUD Permanente (`src/ui/HUD.py`)**:
  - Barras proporcionales de vida (`HP`) y maná (`MP`) con contornos y relleno dinámico.
  - Integración de tipografía pixel art personalizada (`assets/fonts/Minimal4.ttf`).
  - Indicador numérico de vida y maná alineado con las barras.
  - Avatar de la forma activa en el HUD con borde temático.
  - Indicador visual de enfriamiento (cooldown de 5 segundos) al cambiar de forma: medidor circular/aro radial de progreso alrededor del icono.
- **Paleta Cromática de Fase Verde (`green`)**:
  - Reemplazo de la variante azul original por la variante verde para sincronizar con la fase temporal del juego (`Mage_green.png`, `Morph_green.png`, `sword_green.png`, `flame_green.png`).
  - Soporte para renderizado de contornos destacados (`Entity.render_outline`) para maximizar visibilidad del personaje sobre fondos oscuros.
- **Sistema de Combos y Ataque Direccional**:
  - Ataque vertical hacia arriba (`is_looking_up` + botón de ataque).
  - Ventana de buffer de combo en `AttackState` para encadenar el segundo golpe de espada antes de que finalice la primera fase de la animación.

### Cambiado
- **Ajuste de Tiempos e Intervalos de Animación**:
  - Modificación de los intervalos de animación en `src/definitions/entity.py` para permitir mayor legibilidad visual en los ataques rápidos y combos de la espada.

---

## [0.2.0] - 2026-09-11

### Añadido
- **Mapeo Centralizado de Entidades (`src/definitions/entity.py`)**:
  - Extracción de todas las constantes, hitboxes, parámetros de física (`GRAVITY = 850.0`, `WALK_SPEED = 90.0`, `RUN_SPEED = 140.0`, `JUMP_VELOCITY = -320.0`) y diccionarios de animación fuera de `settings.py`.
  - Definición de estadísticas base por personaje (`health`, `max_health`, `mana`, `max_mana`, costos de maná y daño).
  - Callbacks modulares de acción: `_sword_special_finish`, `_mage_special_update`, `_mage_special_finish`, `_morph_dash`.
- **Estados Base de Entidad (`src/states/entity/EntityBaseState.py`)**:
  - Arquitectura estándar para estados de entidad que soporta flags por estado como `has_gravity`.
- **Estados de Daño y Muerte (`HitState`, `DeathState`)**:
  - Manejo de daño con retroceso y tiempo de recuperación.
  - Detección de vida en cero con transición al estado de muerte o rotación entre formas disponibles.

### Corregido
- **Detección de Fin de Animación**:
  - Implementación de `is_animation_finished()` con temporizador de respaldo (`fallback_duration`) para prevenir que las animaciones de un solo ciclo queden atascadas indefinidamente.
- **Movimiento y Volteo (`facing`)**:
  - Solución al sprite estático al desplazarse de izquierda a derecha; orientación dinámica de sprites según `move_direction`.
- **Ataques en el Aire e Inercia Horizontal**:
  - Permitir activar ataques básicos y dashes mientras se está en suspensión aérea sin detener el juego en seco.

---

## [0.1.0] - Inicio del Proyecto

### Añadido
- **Estructura Base del Juego con el Motor Gale**:
  - Configuración inicial de ventana en `main.py` y `settings.py` (resolución base 320x180, escalado a 1280x720).
  - Inicialización de `ChronoBlight.py` gestionando el ciclo de vida del juego.
  - Carga de texturas, hojas de sprites y recortes de frames (`assets/graphics/`).
  - Máquina de estados principal del juego (`PlayState`, `TitleState`, `PauseState`, `PhaseShiftState`).
  - Cámara de seguimiento suave del jugador (`src/world/Camera.py`).
  - Prototipo inicial de las tres transformaciones del jugador: Espada (`Sword`), Mago (`Mage`) y Forma Amorfa (`Morph`).

